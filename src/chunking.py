from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Lookbehind keeps the punctuation attached to its sentence instead of consuming it.
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]

        n = self.max_sentences_per_chunk
        return [" ".join(sentences[i : i + n]) for i in range(0, len(sentences), n)]


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        pieces = (piece.strip() for piece in self._split(text, self.separators))
        return [piece for piece in pieces if piece]

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        size = max(1, self.chunk_size)

        # Base case 1: already small enough.
        if len(current_text) <= size:
            return [current_text] if current_text else []

        # Base case 2 and 3: no separators left, or the "" separator -> hard cut by size.
        if not remaining_separators or remaining_separators[0] == "":
            return [current_text[i : i + size] for i in range(0, len(current_text), size)]

        separator, rest = remaining_separators[0], remaining_separators[1:]
        if separator not in current_text:
            return self._split(current_text, rest)

        # Keep the separator attached to the end of each piece so no text (e.g. the period) is lost.
        parts = current_text.split(separator)
        pieces = [part + separator for part in parts[:-1]] + [parts[-1]]

        # Merge adjacent small pieces up to chunk_size; recurse into pieces that are still too long.
        chunks: list[str] = []
        buffer = ""
        for piece in pieces:
            if len(buffer) + len(piece) <= size:
                buffer += piece
                continue
            if buffer:
                chunks.append(buffer)
                buffer = ""
            if len(piece) > size:
                chunks.extend(self._split(piece, rest))
            else:
                buffer = piece
        if buffer:
            chunks.append(buffer)
        return chunks


class HeadingChunker:
    """
    Split Markdown by headings: every section (heading + body) becomes one chunk.

    Each chunk starts with its heading path (ancestor headings + own heading), so a
    short section such as "## 2. Giá trị" still says which document and which part it
    belongs to. Sections longer than chunk_size are split further with RecursiveChunker,
    and the heading path is repeated on every sub-chunk.
    """

    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        chunks: list[str] = []
        path: list[tuple[int, str]] = []  # (level, heading line) of the current section and its ancestors
        body_lines: list[str] = []

        def flush() -> None:
            body = "\n".join(body_lines).strip()
            if body:
                chunks.extend(self._section_chunks([line for _, line in path], body))
            body_lines.clear()

        for line in text.splitlines():
            match = self.HEADING_PATTERN.match(line)
            if not match:
                body_lines.append(line)
                continue
            flush()
            level = len(match.group(1))
            while path and path[-1][0] >= level:
                path.pop()
            path.append((level, line.strip()))
        flush()
        return chunks

    def _section_chunks(self, headings: list[str], body: str) -> list[str]:
        prefix = "\n".join(headings)
        whole = f"{prefix}\n{body}" if prefix else body
        if len(whole) <= self.chunk_size:
            return [whole]
        # Section too long: split the body, then re-attach the heading path to every piece.
        body_budget = max(100, self.chunk_size - len(prefix) - 1)
        pieces = RecursiveChunker(chunk_size=body_budget).chunk(body)
        return [f"{prefix}\n{piece}" if prefix else piece for piece in pieces]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        chunkers = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=chunk_size // 10),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        result: dict[str, dict] = {}
        for name, chunker in chunkers.items():
            chunks = chunker.chunk(text)
            count = len(chunks)
            result[name] = {
                "count": count,
                "avg_length": sum(len(c) for c in chunks) / count if count else 0.0,
                "chunks": chunks,
            }
        return result
