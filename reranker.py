from sentence_transformers import CrossEncoder

# Lightweight and stable reranker
reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank(query, chunks):

    if not chunks:
        return []

    pairs = []

    for chunk in chunks:
        pairs.append([query, chunk.content])

    scores = reranker_model.predict(pairs)

    ranked = list(zip(chunks, scores))

    ranked.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return [item[0] for item in ranked[:5]]