from sqlalchemy import Column, String, Text, Integer
from pgvector.sqlalchemy import Vector
from database import Base
import uuid

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_name = Column(String)
    section = Column(String)
    clause = Column(String)
    page = Column(Integer)
    content = Column(Text)
    embedding = Column(Vector(1024))