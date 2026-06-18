import os
from fastapi import APIRouter, UploadFile, File
from database import SessionLocal
from models import DocumentChunk
from rag_pipeline import extract_text_from_pdf
from rag_pipeline import clause_aware_chunking
from rag_pipeline import create_embedding

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_path)

    chunks = clause_aware_chunking(text)

    db = SessionLocal()

    for chunk in chunks:
        embedding = create_embedding(chunk["content"])

        row = DocumentChunk(
            document_name=file.filename,
            section=chunk["heading"],
            clause=chunk["heading"],
            page=1,
            content=chunk["content"],
            embedding=embedding
        )

        db.add(row)

    db.commit()

    return {
        "message": "Document uploaded successfully",
        "chunks": len(chunks)
    }