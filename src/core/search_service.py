from infrastructure.embedding import get_embedding

class SearchService:
    def __init__(self, repo):
        self.repo = repo

    def search(self, query: str, top_k: int = 5):
        vector = get_embedding(query)
        return self.repo.search(vector, limit=top_k)
