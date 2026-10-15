from context.budget import TRUNCATED, allocate, encoded_length, fit
from embedding.chunks import chunks, mean


def test_large_document_is_chunked_without_losing_its_tail():
    text = "A" * 19 + "TAIL"
    parts = chunks(text, size=10, overlap=2)
    assert parts == [text[0:10], text[8:18], text[16:23]]
    assert parts[-1].endswith("TAIL")


def test_chunk_embeddings_are_combined_without_dropping_a_chunk():
    assert mean([[1.0, 4.0], [3.0, 8.0], [5.0, 12.0]]) == [3.0, 8.0]


def test_ranked_document_is_truncated_to_budget_with_receipt():
    document = {"id": "top", "title": "Top", "spaceKey": "S", "content": "x" * 500}
    included = fit(document, 150)
    assert included is not None
    assert included["content"].endswith(TRUNCATED)
    assert encoded_length(included) <= 150
    assert included["content"].startswith("x")


def test_document_that_cannot_fit_its_identity_is_left_for_another_slot():
    document = {"id": "top", "title": "Top", "spaceKey": "S", "content": "evidence"}
    assert fit(document, 5) is None


def test_large_top_result_cannot_suppress_later_evidence():
    documents = [
        {"id": "top", "title": "Top", "spaceKey": "S", "content": "x" * 1_000},
        {"id": "next", "title": "Next", "spaceKey": "S", "content": "second source"},
    ]
    included = allocate(documents, 300)
    assert [document["id"] for document in included] == ["top", "next"]
    assert included[0]["content"].endswith(TRUNCATED)
    assert included[1]["content"] == "second source"
    assert sum(encoded_length(document) for document in included) <= 300
