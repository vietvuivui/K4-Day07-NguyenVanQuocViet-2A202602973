from typing import Callable

from .store import EmbeddingStore


NO_CONTEXT_ANSWER = "Không tìm thấy thông tin liên quan trong cơ sở tri thức."


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            # Nothing to ground the answer on: do not call the LLM.
            return NO_CONTEXT_ANSWER
        return self.llm_fn(self._build_prompt(question, results))

    @staticmethod
    def _build_prompt(question: str, results: list[dict]) -> str:
        # Number each chunk with its source so the answer can cite [n] back to a chunk and file.
        context_blocks = []
        for number, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})
            source = metadata.get("doc_id") or result.get("id", "unknown")
            source_url = metadata.get("source_url")
            header = f"[{number}] (nguồn: {source}" + (f", {source_url}" if source_url else "") + ")"
            context_blocks.append(f"{header}\n{result['content']}")
        context = "\n\n".join(context_blocks)

        return (
            "Bạn là trợ lý trả lời câu hỏi về quy định và dịch vụ đại học.\n"
            "Chỉ sử dụng thông tin trong phần NGỮ CẢNH bên dưới, không dùng kiến thức bên ngoài.\n"
            "Khi dùng thông tin từ đoạn nào, trích dẫn số của đoạn đó, ví dụ [1] hoặc [2].\n"
            f'Nếu ngữ cảnh không chứa câu trả lời, hãy trả lời: "{NO_CONTEXT_ANSWER}"\n\n'
            f"NGỮ CẢNH:\n{context}\n\n"
            f"CÂU HỎI: {question}\n\n"
            "TRẢ LỜI:"
        )
