from tokenizers import Tokenizer
from pathlib import Path


class TextChunker:
    """Chunks text based on token count using the FastEmbed tokenizer."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        max_tokens: int = 256,
        overlap_tokens: int = 50,
    ):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self._tokenizer = self._load_tokenizer(model_name)

    def _load_tokenizer(self, model_name: str) -> Tokenizer:
        """Load the tokenizer from the FastEmbed cache or download it."""
        # FastEmbed caches models in ~/.cache/fastembed
        cache_dir = Path.home() / ".cache" / "fastembed" / f"models--{model_name.replace('/', '--')}"
        tokenizer_path = cache_dir / "tokenizer.json"

        if tokenizer_path.exists():
            return Tokenizer.from_file(str(tokenizer_path))

        # Fallback: load from HuggingFace Hub
        return Tokenizer.from_pretrained(model_name)

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in text."""
        return len(self._tokenizer.encode(text).ids)

    def chunk(self, text: str, doc_id: str, title: str = "") -> list[dict]:
        """
        Chunk text into segments that fit within max_tokens.

        Returns list of dicts with:
            - id: "{doc_id}#chunk{n}"
            - text: chunk content
            - title: original title
            - chunk_index: position in original document
            - parent_id: original doc_id
        """
        # Encode full text to get tokens
        encoded = self._tokenizer.encode(text)
        tokens = encoded.ids
        total_tokens = len(tokens)

        # If text fits in one chunk, return as-is
        if total_tokens <= self.max_tokens:
            return [{
                "id": doc_id,
                "text": text,
                "title": title,
                "chunk_index": 0,
                "parent_id": doc_id,
            }]

        chunks = []
        start = 0
        chunk_index = 0

        while start < total_tokens:
            end = min(start + self.max_tokens, total_tokens)

            # Get token slice and decode back to text
            chunk_tokens = tokens[start:end]
            chunk_text = self._tokenizer.decode(chunk_tokens)

            chunks.append({
                "id": f"{doc_id}#chunk{chunk_index}",
                "text": chunk_text,
                "title": f"{title} (part {chunk_index + 1})" if title else f"Part {chunk_index + 1}",
                "chunk_index": chunk_index,
                "parent_id": doc_id,
            })

            # Move start with overlap
            start = end - self.overlap_tokens
            if start >= total_tokens:
                break
            chunk_index += 1

        return chunks

    def chunk_documents(self, documents: list[dict]) -> list[dict]:
        """Chunk a list of documents. Each doc: {id, text, title?, metadata?}"""
        all_chunks = []
        for doc in documents:
            doc_chunks = self.chunk(
                text=doc["text"],
                doc_id=doc["id"],
                title=doc.get("title", ""),
            )
            # Preserve original metadata on each chunk
            for chunk in doc_chunks:
                chunk["metadata"] = doc.get("metadata", {})
            all_chunks.extend(doc_chunks)
        return all_chunks
