from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Document, QueryRequest, DocumentType

class VectorRepository(ABC):
    @abstractmethod
    def ensure_collection(self, document_type: DocumentType, dimension: int) -> str:
        pass
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> int:
        pass
    
    @abstractmethod
    def search_documents(self, request: QueryRequest) -> List[dict]:
        pass

class FileProcessor(ABC):
    @abstractmethod
    def extract_text(self, file_path: str, filename: str) -> str:
        pass
    
    @abstractmethod
    def detect_document_type(self, text: str, filename: str) -> DocumentType:
        pass