"""Benchmark 5 group queries against the scholarship corpus in data/hoc-bong/.

Each member changes only STRATEGY (or passes --strategy) so every run shares the same
corpus, queries, embedder and scoring.

Usage:
    python bench.py                          # run STRATEGY below; embedder from EMBEDDING_PROVIDER in .env
    python bench.py --strategy all           # run every strategy and print a summary
    python bench.py --answers gemini         # also generate agent answers with Gemini
    python bench.py --baseline               # ChunkingStrategyComparator on 3 documents
    python bench.py --embedder mock          # structure check only (no semantics)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from src.agent import KnowledgeBaseAgent
from src.chunking import (
    ChunkingStrategyComparator,
    FixedSizeChunker,
    HeadingChunker,
    RecursiveChunker,
    SentenceChunker,
)
from src.embeddings import GeminiEmbedder, LocalEmbedder, OpenAIEmbedder, _mock_embed
from src.models import Document
from src.store import EmbeddingStore

DATA_DIR = Path("data/hoc-bong")
CACHE_DIR = Path(".cache")
CHUNK_SIZE = 500
TOP_K = 3

# ---- The one line each member changes -------------------------------------------------
STRATEGY = "heading"  # "fixed_size" | "recursive" | "by_sentences" | "heading"
# ---------------------------------------------------------------------------------------

STRATEGIES = {
    "fixed_size": lambda: FixedSizeChunker(chunk_size=CHUNK_SIZE, overlap=CHUNK_SIZE // 10),
    "recursive": lambda: RecursiveChunker(chunk_size=CHUNK_SIZE),
    "by_sentences": lambda: SentenceChunker(max_sentences_per_chunk=3),
    "heading": lambda: HeadingChunker(chunk_size=CHUNK_SIZE),
}

# `evidence`: a phrase copied from the gold passage; a retrieved chunk counts as relevant
# only if it comes from the gold document AND contains this phrase.
QUERIES = [
    {
        "id": "Q1",
        "type": "điều kiện (cần filter)",
        "query": "Học bổng khuyến khích học tập ở Viện Cơ khí VIMARU được xét như thế nào?",
        "gold_doc": "vimaru-hbkkht-tieu-chuan-sinh-vien",
        "evidence": "3.20 ≤ ĐTBHB < 3.60",
        "filter": {"audience": "student"},
        "ab_test": True,
    },
    {
        "id": "Q2",
        "type": "tra số liệu",
        "query": "Học bổng Vallet dành cho học viên sau đại học năm 2026 có bao nhiêu suất và mỗi suất trị giá bao nhiêu?",
        "gold_doc": "vallet-hoc-bong-sau-dai-hoc",
        "evidence": "42 suất",
        "filter": None,
    },
    {
        "id": "Q3",
        "type": "quy trình",
        "query": "Quy trình xét học bổng hỗ trợ đột xuất của UEH gồm những bước nào và mất bao lâu?",
        "gold_doc": "ueh-ke-hoach-xet-hoc-bong-2026",
        "evidence": "Trình xin ý kiến Ban Giám đốc",
        "filter": None,
    },
    {
        "id": "Q4",
        "type": "liệt kê",
        "query": "Hồ sơ đăng ký học bổng K-T của ULIS gồm những giấy tờ gì?",
        "gold_doc": "ulis-hoc-bong-kt-2025-2026",
        "evidence": "Bài phát biểu cảm tưởng",
        "filter": None,
    },
    {
        "id": "Q5",
        "type": "điều kiện + số liệu",
        "query": "Tân sinh viên HSB muốn được tài trợ 100% học phí có điều kiện thì cần điểm thi bao nhiêu và phải hoàn trả thế nào?",
        "gold_doc": "hsb-hoc-bong-tan-sinh-vien-2026",
        "evidence": "24/30",
        "filter": None,
    },
]


# ---- Corpus loading ------------------------------------------------------------------

def load_markdown(path: Path) -> tuple[dict[str, str], str]:
    """Split a Markdown file into (frontmatter metadata, body)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text.strip()
    _, front_matter, body = text.split("---", 2)
    metadata = {}
    for line in front_matter.strip().splitlines():
        key, sep, value = line.partition(":")
        if sep:
            metadata[key.strip()] = value.strip().strip('"')
    return metadata, body.strip()


def build_documents(chunker) -> list[Document]:
    """Chunk every file outside the store; each chunk carries the file's full frontmatter."""
    documents = []
    for path in sorted(DATA_DIR.glob("*.md")):
        metadata, body = load_markdown(path)
        for i, chunk in enumerate(chunker.chunk(body)):
            documents.append(
                Document(
                    id=f"{path.stem}#{i}",
                    content=chunk,
                    metadata={**metadata, "doc_id": path.stem, "chunk_index": i},
                )
            )
    return documents


# ---- Embedders -----------------------------------------------------------------------

class CachedEmbedder:
    """Disk cache keyed by content hash, so re-runs do not re-embed (or re-pay for) the same text."""

    def __init__(self, embedder, name: str) -> None:
        self._embedder = embedder
        self._backend_name = getattr(embedder, "_backend_name", name)
        CACHE_DIR.mkdir(exist_ok=True)
        self._path = CACHE_DIR / f"embeddings-{name}.json"
        self._cache = json.loads(self._path.read_text(encoding="utf-8")) if self._path.exists() else {}
        self._dirty = False

    def __call__(self, text: str) -> list[float]:
        key = hashlib.sha256(f"{self._backend_name}\n{text}".encode("utf-8")).hexdigest()
        if key not in self._cache:
            self._cache[key] = self._embed_with_retry(text)
            self._dirty = True
            if len(self._cache) % 25 == 0:
                self.save()  # keep progress if a long API run is interrupted
        return self._cache[key]

    def _embed_with_retry(self, text: str, attempts: int = 6) -> list[float]:
        # Free-tier APIs (Gemini) return 429 / RESOURCE_EXHAUSTED when the per-minute quota is hit.
        for attempt in range(1, attempts + 1):
            try:
                return self._embedder(text)
            except Exception as error:  # SDK-specific error classes differ per provider
                message = str(error)
                if attempt == attempts or not ("429" in message or "RESOURCE_EXHAUSTED" in message):
                    raise
                wait = 15 * attempt
                print(f"  rate limited, retrying in {wait}s (attempt {attempt}/{attempts})...")
                time.sleep(wait)
        raise RuntimeError("unreachable")

    def save(self) -> None:
        if self._dirty:
            self._path.write_text(json.dumps(self._cache), encoding="utf-8")
            self._dirty = False


def make_embedder(name: str):
    if name == "mock":
        return _mock_embed
    factories = {"local": LocalEmbedder, "openai": OpenAIEmbedder, "gemini": GeminiEmbedder}
    try:
        return CachedEmbedder(factories[name](), name)
    except (ImportError, RuntimeError) as error:
        # Same fallback rule as README: a missing backend falls back to the mock embedder.
        print(f"WARNING: embedder '{name}' unavailable ({error}); falling back to mock embeddings.")
        print("         Results below have no semantic meaning — install the backend before CP6.")
        return _mock_embed


def demo_llm(prompt: str) -> str:
    """Stand-in LLM: no API key is configured, so return the prompt head to show grounding."""
    return "[DEMO LLM — chưa gọi model thật]\n" + prompt[:400]


GEMINI_LLM_MODEL = os.getenv("GEMINI_LLM_MODEL", "gemini-flash-lite-latest")


def make_llm(name: str):
    if name != "gemini":
        return demo_llm
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY missing; agent answers use the demo LLM.")
        return demo_llm
    client = genai.Client(api_key=api_key)
    CACHE_DIR.mkdir(exist_ok=True)
    cache_path = CACHE_DIR / f"answers-{GEMINI_LLM_MODEL}.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}

    def gemini_llm(prompt: str) -> str:
        key = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        if key in cache:
            return cache[key]
        for attempt in range(1, 9):
            try:
                response = client.models.generate_content(model=GEMINI_LLM_MODEL, contents=prompt)
                cache[key] = (response.text or "").strip()
                cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
                return cache[key]
            except Exception as error:
                retryable = any(code in str(error) for code in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE"))
                if attempt == 8 or not retryable:
                    raise
                print(f"  LLM busy/rate limited, retrying in {20 * attempt}s...")
                time.sleep(20 * attempt)
        raise RuntimeError("unreachable")

    return gemini_llm


def agent_answer(llm, question: str, results: list[dict]) -> str:
    """Same prompt as KnowledgeBaseAgent.answer, but over already-(filtered) results."""
    if not results:
        return "Không tìm thấy thông tin liên quan trong cơ sở tri thức."
    return llm(KnowledgeBaseAgent._build_prompt(question, results))


# ---- Evaluation ----------------------------------------------------------------------

def evaluate(results: list[dict], query: dict) -> dict:
    """Score one query at two levels.

    naive   : only checks whether the gold doc_id appears in top-k (inflates results).
    content : gold doc must appear AND the retrieved context must contain the evidence string.
    Scale (both): 2 = gold at top-1, 1 = gold at top-2/3, 0 = absent (content: also 0 if the
    context cannot answer).
    """
    gold_rank = next((r for r, res in enumerate(results, 1) if res["metadata"]["doc_id"] == query["gold_doc"]), None)
    evidence_rank = next(
        (r for r, res in enumerate(results, 1)
         if res["metadata"]["doc_id"] == query["gold_doc"] and query["evidence"] in res["content"]),
        None,
    )
    naive_points = 2 if gold_rank == 1 else (1 if gold_rank else 0)
    content_points = 0 if evidence_rank is None else naive_points
    return {
        "gold_rank": gold_rank,
        "evidence_rank": evidence_rank,
        "naive_points": naive_points,
        "content_points": content_points,
    }


def print_results(label: str, results: list[dict], query: dict) -> dict:
    ev = evaluate(results, query)
    print(
        f"  {label}: gold doc rank = {ev['gold_rank'] or '-'} | evidence chunk rank = {ev['evidence_rank'] or '-'}"
        f" | naive {ev['naive_points']}đ, content {ev['content_points']}đ"
    )
    for position, result in enumerate(results, start=1):
        preview = " ".join(result["content"].split())[:110]
        marker = "*" if position == ev["evidence_rank"] else " "
        print(f"   {marker}{position}. {result['score']:.3f}  {result['id']:<45} audience={result['metadata'].get('audience')}")
        print(f"        {preview}")
    return ev


def run_strategy(strategy: str, embedder, verbose: bool = True, llm=None) -> dict:
    documents = build_documents(STRATEGIES[strategy]())
    store = EmbeddingStore(collection_name=f"bench-{strategy}", embedding_fn=embedder)
    store.add_documents(documents)

    lengths = [len(doc.content) for doc in documents]
    summary = {
        "strategy": strategy,
        "chunks": len(documents),
        "avg_length": sum(lengths) / len(lengths) if lengths else 0.0,
        "naive_points": 0,
        "content_points": 0,
        "evals": {},
        "top3": {},
    }
    if verbose:
        print(f"\n=== Strategy: {strategy} | {len(documents)} chunks | avg {summary['avg_length']:.0f} chars ===")

    for query in QUERIES:
        if verbose:
            print(f"\n{query['id']} [{query['type']}] {query['query']}")
            print(f"  gold: {query['gold_doc']} (evidence: \"{query['evidence']}\")")
        if query.get("ab_test"):
            unfiltered = store.search_with_filter(query["query"], top_k=TOP_K, metadata_filter=None)
            key = f"{query['id']}-nofilter"
            summary["evals"][key] = print_results("A) no filter", unfiltered, query) if verbose else evaluate(unfiltered, query)
            summary["top3"][key] = [(r["id"], round(r["score"], 3), r["metadata"].get("audience")) for r in unfiltered]
            if llm:
                summary.setdefault("answers", {})[key] = agent_answer(llm, query["query"], unfiltered)
        results = store.search_with_filter(query["query"], top_k=TOP_K, metadata_filter=query["filter"])
        label = f"B) filter={query['filter']}" if query.get("ab_test") else f"filter={query['filter']}"
        ev = print_results(label, results, query) if verbose else evaluate(results, query)
        summary["evals"][query["id"]] = ev
        summary["top3"][query["id"]] = [(r["id"], round(r["score"], 3), r["metadata"].get("audience")) for r in results]
        summary["naive_points"] += ev["naive_points"]
        summary["content_points"] += ev["content_points"]
        if llm:
            summary.setdefault("answers", {})[query["id"]] = agent_answer(llm, query["query"], results)

    for key, answer in summary.get("answers", {}).items():
        print(f"\n--- [{strategy}] Agent answer {key} ---\n{answer}")

    if verbose and not llm:
        agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)
        print(f"\n--- Agent prompt sample (Q1, top-{TOP_K} không filter) ---")
        print(agent.answer(QUERIES[0]["query"], top_k=TOP_K))
    return summary


def run_baseline() -> None:
    comparator = ChunkingStrategyComparator()
    for stem in ["hsb-hoc-bong-tan-sinh-vien-2026", "ueh-ke-hoach-xet-hoc-bong-2026", "vimaru-hbkkht-tieu-chuan-sinh-vien"]:
        _, body = load_markdown(DATA_DIR / f"{stem}.md")  # frontmatter removed before measuring
        result = comparator.compare(body, chunk_size=CHUNK_SIZE)
        heading_chunks = HeadingChunker(chunk_size=CHUNK_SIZE).chunk(body)
        result["heading"] = {
            "count": len(heading_chunks),
            "avg_length": sum(map(len, heading_chunks)) / len(heading_chunks),
            "chunks": heading_chunks,
        }
        print(f"\n{stem} ({len(body)} chars)")
        for name, stats in result.items():
            lengths = [len(c) for c in stats["chunks"]]
            print(f"  {name:<13} count={stats['count']:>3}  avg={stats['avg_length']:>6.1f}  min={min(lengths):>4}  max={max(lengths):>4}")


def main() -> int:
    load_dotenv(override=False)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strategy", default=STRATEGY, choices=[*STRATEGIES, "all"])
    parser.add_argument("--embedder", default=os.getenv("EMBEDDING_PROVIDER", "local"), choices=["local", "mock", "openai", "gemini"])
    parser.add_argument("--baseline", action="store_true", help="only run ChunkingStrategyComparator on 3 documents")
    parser.add_argument("--answers", choices=["gemini", "demo"], help="also generate agent answers with this LLM")
    args = parser.parse_args()

    if args.baseline:
        run_baseline()
        return 0

    embedder = make_embedder(args.embedder)
    print(f"Embedder: {getattr(embedder, '_backend_name', args.embedder)} | chunk_size={CHUNK_SIZE} | top_k={TOP_K}")
    strategies = list(STRATEGIES) if args.strategy == "all" else [args.strategy]
    llm = make_llm(args.answers) if args.answers else None
    summaries = [run_strategy(name, embedder, verbose=len(strategies) == 1, llm=llm) for name in strategies]
    if isinstance(embedder, CachedEmbedder):
        embedder.save()

    print("\n=== Summary: points per query as naive/content (2 = gold top-1, 1 = gold top-2/3, 0 = miss;"
          " content also requires the evidence string in the retrieved context) ===")
    keys = [q["id"] for q in QUERIES] + ["Q1-nofilter"]
    print(f"{'strategy':<13}{'chunks':>7}{'avg':>6}  " + "".join(f"{k:>13}" for k in keys) + "   naive  content")
    for s in summaries:
        cells = "".join(f"{str(s['evals'][k]['naive_points']) + '/' + str(s['evals'][k]['content_points']):>13}" for k in keys)
        print(f"{s['strategy']:<13}{s['chunks']:>7}{s['avg_length']:>6.0f}  {cells}   {s['naive_points']:>2}/10   {s['content_points']:>2}/10")
    print(f"\nQ1 A/B top-{TOP_K} (id, score, audience):")
    for s in summaries:
        print(f"  {s['strategy']}")
        print(f"    A no filter : {s['top3']['Q1-nofilter']}")
        print(f"    B student   : {s['top3']['Q1']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
