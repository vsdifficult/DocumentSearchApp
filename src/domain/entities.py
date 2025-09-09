from pydantic import BaseModel
from typing import Optional
from enum import Enum

class DocumentType(str, Enum):
    GENERAL = "general"
    LEGAL = "legal"
    TECHNICAL = "technical"
    SCIENTIFIC = "scientific"
    FINANCIAL = "financial"

class Document(BaseModel):
    id: int
    text: str
    document_type: DocumentType
    filename: Optional[str] = None
    collection_name: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    document_type: Optional[DocumentType] = None
    filter_by_filename: Optional[str] = None
    limit: int = 10