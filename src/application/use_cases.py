from typing import List
from src.domain.entities import Document, QueryRequest, DocumentType
from src.domain.repositories import VectorRepository, FileProcessor

class AddDocumentsUseCase:
    def __init__(self, repository: VectorRepository, file_processor: FileProcessor):
        self.repository = repository
        self.file_processor = file_processor
    
    def execute(self, files: List) -> dict:
        documents = []
        results = {
            "total_processed": 0,
            "by_type": {},
            "errors": []
        }
        
        for file_info in files:
            try:
                text = self.file_processor.extract_text(file_info["path"], file_info["filename"])
                document_type = self.file_processor.detect_document_type(text, file_info["filename"])
                
                document = Document(
                    id=hash(text + file_info["filename"]),
                    text=text,
                    document_type=document_type,
                    filename=file_info["filename"]
                )
                documents.append(document)
                
                # Update statistics
                if document_type.value not in results["by_type"]:
                    results["by_type"][document_type.value] = 0
                results["by_type"][document_type.value] += 1
                results["total_processed"] += 1
                
            except Exception as e:
                results["errors"].append({
                    "filename": file_info["filename"],
                    "error": str(e)
                })
        
        if documents:
            count = self.repository.add_documents(documents)
            results["added_to_vector_db"] = count
        
        return results

class SearchDocumentsUseCase:
    def __init__(self, repository: VectorRepository):
        self.repository = repository
    
    def execute(self, request: QueryRequest) -> List[dict]:
        return self.repository.search_documents(request)