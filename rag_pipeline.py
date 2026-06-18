import re
import fitz
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    return full_text


def clause_aware_chunking(text):
    pattern = r'(Section\s+\d+|Clause\s+\d+\.\d+)'
    splits = re.split(pattern, text)

    chunks = []

    current_heading = ""

    for item in splits:
        if "Section" in item or "Clause" in item:
            current_heading = item
        else:
            if len(item.strip()) > 50:
                chunks.append({
                    "heading": current_heading,
                    "content": item.strip()
                })

    return chunks

def create_embedding(text):
    embedding = embedding_model.encode(text, normalize_embeddings=True)
    return embedding.tolist()