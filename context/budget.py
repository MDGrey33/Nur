"""Fit ranked document evidence into a real character budget."""

from __future__ import annotations

import json

TRUNCATED = " [Content truncated due to size limit.]"


def encoded_length(document: dict) -> int:
    return len(json.dumps(document))


def fit(document: dict, budget: int) -> dict | None:
    """Return the largest visible prefix of a document that fits, or None."""
    if budget <= 0:
        return None
    if encoded_length(document) <= budget:
        return document
    base = dict(document, content="")
    if encoded_length(base) + len(TRUNCATED) > budget:
        return None
    content = document.get("content", "")
    low, high = 0, len(content)
    while low < high:
        middle = (low + high + 1) // 2
        candidate = dict(base, content=content[:middle] + TRUNCATED)
        if encoded_length(candidate) <= budget:
            low = middle
        else:
            high = middle - 1
    return dict(base, content=content[:low] + TRUNCATED)


def allocate(documents: list[dict], budget: int) -> list[dict]:
    """Keep ranked evidence visible while reserving space for later results."""
    included = []
    used = 0
    for position, document in enumerate(documents):
        remaining = budget - used
        candidates_left = len(documents) - position
        share = remaining // candidates_left if candidates_left else 0
        item = fit(document, share)
        if item is not None:
            included.append(item)
            used += encoded_length(item)
    return included
