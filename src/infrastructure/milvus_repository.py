import os
import hashlib
from src.domain.repositories import VectorRepository
from src.domain.entities import Document, QueryRequest, DocumentType
from typing import List
from pymilvus import MilvusClient, model, connections

class MilvusVectorRepository(VectorRepository):
    def __init__(self):
        self.host = os.getenv("MILVUS_HOST", "standalone")
        self.port = os.getenv("MILVUS_PORT", "19530")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "cointegrated/rubert-tiny")
        self.dimension = 768  
        
        connections.connect(host=self.host, port=self.port)
        self.client = MilvusClient(uri=f"http://{self.host}:{self.port}")
        
        self.embedding_fn = model.dense.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model,
            device='cpu'
        )
    
    def _get_collection_name(self, document_type: DocumentType) -> str:
        """Генерирует имя коллекции на основе типа документа"""
        return f"documents_{document_type.value}"
    
    def ensure_collection(self, document_type: DocumentType) -> str:
        """Создает коллекцию если ее нет"""
        collection_name = self._get_collection_name(document_type)
        
        if not self.client.has_collection(collection_name=collection_name):
            schema = self.client.create_schema(auto_id=False, enable_dynamic_field=True)
            schema.add_field(field_name="id", datatype="int64", is_primary=True)
            schema.add_field(field_name="vector", datatype="FLOAT_VECTOR", dim=self.dimension)
            schema.add_field(field_name="text", datatype="VARCHAR", max_length=65535)
            schema.add_field(field_name="document_type", datatype="VARCHAR", max_length=50)
            schema.add_field(field_name="filename", datatype="VARCHAR", max_length=255)
            
            index_params = self.client.prepare_index_params()
            index_params.add_index(
                field_name="vector",
                index_type="IVF_FLAT",
                metric_type="L2",
                params={"nlist": 128}
            )
            
            self.client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )
        
        return collection_name
    
    def add_documents(self, documents: List[Document]) -> int:
        """Добавляет документы в соответствующие коллекции"""
        total_added = 0
        
        documents_by_type = {}
        for doc in documents:
            if doc.document_type not in documents_by_type:
                documents_by_type[doc.document_type] = []
            documents_by_type[doc.document_type].append(doc)
        
        for doc_type, docs in documents_by_type.items():
            collection_name = self.ensure_collection(doc_type)
            
            texts = [doc.text for doc in docs]
            vectors = self.embedding_fn.encode_documents(texts)
            
            data = [
                {
                    "id": doc.id,
                    "vector": vectors[i],
                    "text": doc.text[:65530],
                    "document_type": doc.document_type.value,
                    "filename": doc.filename
                }
                for i, doc in enumerate(docs)
            ]
            
            result = self.client.insert(collection_name=collection_name, data=data)
            total_added += len(docs)
        
        return total_added
    
    def search_documents(self, request: QueryRequest) -> List[dict]:
        """Поиск документов по запросу"""
        results = []
        
        if request.document_type:
            collection_name = self._get_collection_name(request.document_type)
            if self.client.has_collection(collection_name=collection_name):
                results.extend(self._search_in_collection(collection_name, request))
        else:
            all_collections = self.client.list_collections()
            for collection_name in all_collections:
                if collection_name.startswith("documents_"):
                    results.extend(self._search_in_collection(collection_name, request))
        
        results.sort(key=lambda x: x.get('distance', 0))
        return results[:request.limit]
    
    def _search_in_collection(self, collection_name: str, request: QueryRequest) -> List[dict]:
        """Поиск в конкретной коллекции"""
        query_vector = self.embedding_fn.encode_queries([request.query])
        
        filter_parts = []
        if request.filter_by_filename:
            filter_parts.append(f'filename == "{request.filter_by_filename}"')
        
        filter_expr = " and ".join(filter_parts) if filter_parts else ""
        
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        
        try:
            collection_results = self.client.search(
                collection_name=collection_name,
                data=query_vector,
                anns_field="vector",
                param=search_params,
                limit=request.limit,
                output_fields=["text", "document_type", "filename"],
                filter=filter_expr if filter_expr else None
            )
            
            if collection_results:
                return collection_results[0]
        except Exception:
            pass
        
        return []