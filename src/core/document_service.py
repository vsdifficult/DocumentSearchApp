from infrastructure.parser import extract_text
from infrastructure.embedding import get_embedding

class DocumentService:
    def __init__(self, repo):
        self.repo = repo

    def process_and_save(self, filepath: str):
        text = extract_text(filepath)
        if not text:
            raise ValueError("Не удалось извлечь текст.")
        embedding = get_embedding(text)
        self.repo.save(filepath, text, embedding)
