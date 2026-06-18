from sentence_transformers import SentenceTransformer
from database import SessionLocal
from sqlalchemy import text

embedding_model = SentenceTransformer(
    "BAAI/bge-large-en-v1.5"
)


def hybrid_search(query, top_k=10):

    db = SessionLocal()

    query_embedding = embedding_model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    # Convert embedding list to pgvector format
    embedding_str = "[" + ",".join(
        map(str, query_embedding)
    ) + "]"

    vector_query = text("""
        SELECT
            id,
            document_name,
            section,
            clause,
            page,
            content,
            embedding <=> CAST(:embedding AS vector) AS distance
        FROM document_chunks
        ORDER BY distance
        LIMIT 20
    """)

    vector_results = db.execute(
        vector_query,
        {
            "embedding": embedding_str
        }
    ).fetchall()

    keyword_query = text("""
        SELECT
            id,
            document_name,
            section,
            clause,
            page,
            content
        FROM document_chunks
        WHERE to_tsvector('english', content)
        @@ plainto_tsquery(:query)
        LIMIT 20
    """)

    keyword_results = db.execute(
        keyword_query,
        {
            "query": query
        }
    ).fetchall()

    combined = []
    seen = set()

    for row in vector_results:
        if row.id not in seen:
            combined.append(row)
            seen.add(row.id)

    for row in keyword_results:
        if row.id not in seen:
            combined.append(row)
            seen.add(row.id)

    return combined[:top_k]