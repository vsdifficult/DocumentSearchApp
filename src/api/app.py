from fastapi import FastAPI, HTTPException, File, UploadFile, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
from typing import List, Optional

from src.domain.entities import QueryRequest, DocumentType
from src.application.use_cases import AddDocumentsUseCase, SearchDocumentsUseCase
from src.infrastructure.sqlite_repository import SQLiteVectorRepository  # Изменено!
from src.infrastructure.file_processor import DefaultFileProcessor

app = FastAPI(
    title="Document Search API",
    description="API для поиска по документам с использованием SQLite",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection - используем SQLite вместо Milvus
vector_repo = SQLiteVectorRepository()
file_processor = DefaultFileProcessor()

add_documents_uc = AddDocumentsUseCase(vector_repo, file_processor)
search_documents_uc = SearchDocumentsUseCase(vector_repo)

@app.post("/upload-documents/")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Загружает документы в систему.
    Автоматически определяет тип и сохраняет в SQLite.
    """
    file_infos = []
    try:
        for file in files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                file_infos.append({
                    "path": tmp_file.name,
                    "filename": file.filename
                })
        
        results = add_documents_uc.execute(file_infos)
        
        # Cleanup
        for file_info in file_infos:
            os.unlink(file_info["path"])
        
        return JSONResponse(content=results)
    
    except Exception as e:
        for file_info in file_infos:
            if os.path.exists(file_info["path"]):
                os.unlink(file_info["path"])
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/search/")
def search_documents(
    query: str = Query(..., description="Поисковый запрос"),
    document_type: Optional[DocumentType] = Query(None, description="Фильтр по типу документа"),
    filter_by_filename: Optional[str] = Query(None, description="Фильтр по имени файла"),
    limit: int = Query(10, description="Лимит результатов")
):
    """
    Поиск документов по текстовому запросу.
    """
    try:
        request = QueryRequest(
            query=query,
            document_type=document_type,
            filter_by_filename=filter_by_filename,
            limit=limit
        )
        results = search_documents_uc.execute(request)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stats/")
def get_statistics():
    """
    Возвращает статистику по документам.
    """
    try:
        stats = vector_repo.get_stats()
        return {"statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/")
def health_check():
    return {
        "status": "healthy",
        "storage": "SQLite",
        "message": "API работает успешно"
    }

@app.get("/")
def read_root():
    return {
        "message": "Document Search API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }