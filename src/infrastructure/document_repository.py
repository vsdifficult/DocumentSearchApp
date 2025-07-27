from pymongo.collection import Collection
from bson.binary import Binary
import gridfs

class DocumentRepository:
    def __init__(self, db):
        self.db = db
        self.collection: Collection = db["docs"]
        self.fs = gridfs.GridFS(db)

    def save(self, filename: str, text: str, embedding: list[float]):
        file_id = self.fs.put(open(filename, "rb"), filename=filename)
        self.collection.insert_one({
            "filename": filename,
            "file_id": file_id,
            "text": text,
            "embedding": embedding
        })

    def search(self, vector: list[float], limit: int = 5):
        return self.collection.aggregate([
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": vector,
                    "numCandidates": 100,
                    "limit": limit
                }
            }
        ])
