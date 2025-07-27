import os

def extract_text(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""
    elif ext == ".pdf":
        try:
            import PyPDF2
            text = []
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text() or "")
            return "\n".join(text)
        except Exception:
            return ""
    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(filepath)
            return "\n".join([p.text for p in doc.paragraphs])
        except Exception:
            return ""
    else:
        # Для других расширений можно добавить поддержку
        return ""
