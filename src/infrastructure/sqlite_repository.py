import os
import sqlite3
import hashlib
from src.domain.repositories import VectorRepository
from src.domain.entities import Document, QueryRequest, DocumentType
from typing import List

class SQLiteVectorRepository(VectorRepository):
    def __init__(self):
        self.conn = sqlite3.connect('data/documents.db')
        self._init_db()
    
    def _init_db(self):
        """Инициализация SQLite базы"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                document_type TEXT NOT NULL,
                filename TEXT,
                embedding_hash TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создаем индекс для поиска
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_document_type ON documents(document_type)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_filename ON documents(filename)
        ''')
        
        self.conn.commit()
    
    def ensure_collection(self, document_type: DocumentType) -> str:
        return document_type.value
    
    def add_documents(self, documents: List[Document]) -> int:
        cursor = self.conn.cursor()
        count = 0
        
        for doc in documents:
            # Создаем хэш текста для "эмуляции" embedding
            embedding_hash = hashlib.sha256(doc.text.encode()).hexdigest()
            
            cursor.execute('''
                INSERT OR REPLACE INTO documents (id, text, document_type, filename, embedding_hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (doc.id, doc.text, doc.document_type.value, doc.filename, embedding_hash))
            
            count += 1
        
        self.conn.commit()
        return count
    
    def search_documents(self, request: QueryRequest) -> List[dict]:
        cursor = self.conn.cursor()
        
        # Простой текстовый поиск (можно улучшить)
        query = '''
            SELECT id, text, document_type, filename 
            FROM documents 
            WHERE text LIKE ?
        '''
        params = [f'%{request.query}%']
        
        if request.document_type:
            query += ' AND document_type = ?'
            params.append(request.document_type.value)
        
        if request.filter_by_filename:
            query += ' AND filename = ?'
            params.append(request.filter_by_filename)
        
        query += ' LIMIT ?'
        params.append(request.limit)
        
        cursor.execute(query, params)
        results = []
        
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'entity': {
                    'text': row[1][:500] + '...' if len(row[1]) > 500 else row[1],
                    'document_type': row[2],
                    'filename': row[3]
                },
                'distance': 0.0  
            })
        
        return results
    
    def get_stats(self):
        """Возвращает статистику по документам"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT document_type, COUNT(*) as count 
            FROM documents 
            GROUP BY document_type
        ''')
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]
        
        return stats