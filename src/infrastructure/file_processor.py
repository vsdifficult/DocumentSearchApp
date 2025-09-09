import PyPDF2
import docx
import pandas as pd
from src.domain.repositories import FileProcessor
from src.domain.entities import DocumentType

class DefaultFileProcessor(FileProcessor):
    def extract_text(self, file_path: str, filename: str) -> str:
        text = ""
        
        try:
            if filename.lower().endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            
            elif filename.lower().endswith(('.docx', '.doc')):
                doc = docx.Document(file_path)
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        text += paragraph.text + "\n"
            
            elif filename.lower().endswith(('.txt', '.md')):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    text = file.read()
            
            elif filename.lower().endswith(('.csv', '.xlsx', '.xls')):
                try:
                    if filename.lower().endswith('.csv'):
                        df = pd.read_csv(file_path)
                    else:
                        df = pd.read_excel(file_path)
                    text = df.to_string()
                except:
                    text = f"Табличный файл: {filename}"
            
            else:
                # Пытаемся прочитать как текст
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        text = file.read()
                except:
                    raise Exception(f"Неподдерживаемый формат файла: {filename}")
            
            return text.strip() or "Не удалось извлечь текст"
            
        except Exception as e:
            raise Exception(f"Ошибка чтения файла {filename}: {str(e)}")
    
    def detect_document_type(self, text: str, filename: str) -> DocumentType:
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Простая логика определения типа
        legal_words = ['договор', 'соглашение', 'закон', 'статья', 'юрист']
        tech_words = ['технический', 'код', 'программ', 'алгоритм', 'api']
        finance_words = ['финанс', 'отчет', 'баланс', 'прибыль', 'бюджет']
        science_words = ['исследование', 'научн', 'анализ', 'гипотеза']
        
        if any(word in text_lower for word in legal_words):
            return DocumentType.LEGAL
        
        if any(word in text_lower for word in tech_words):
            return DocumentType.TECHNICAL
        
        if any(word in text_lower for word in finance_words):
            return DocumentType.FINANCIAL
        
        if any(word in text_lower for word in science_words):
            return DocumentType.SCIENTIFIC
        
        return DocumentType.GENERAL