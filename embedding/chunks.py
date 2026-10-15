"""Bound embedding input without discarding any part of a document."""

from __future__ import annotations


# The embedding models used by NUR accept roughly 8,000 tokens. Three characters
# per token leaves margin for the metadata prefix and tokenization differences.
DEFAULT_CHUNK_CHARS = 24_000
DEFAULT_OVERLAP_CHARS = 600


def chunks(text: str, size: int = DEFAULT_CHUNK_CHARS,
           overlap: int = DEFAULT_OVERLAP_CHARS) -> list[str]:
    """Return ordered, overlapping chunks that collectively retain all text."""
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("chunk size must be positive and overlap smaller than size")
    if not text:
        return [""]
    step = size - overlap
    return [text[start:start + size] for start in range(0, len(text), step)]


def mean(vectors: list[list[float]]) -> list[float]:
    """Represent every chunk in NUR's existing one-vector-per-page store."""
    if not vectors:
        raise ValueError("at least one embedding is required")
    width = len(vectors[0])
    if not width or any(len(vector) != width for vector in vectors):
        raise ValueError("embedding vectors must have one non-empty shape")
    return [sum(vector[index] for vector in vectors) / len(vectors)
            for index in range(width)]
