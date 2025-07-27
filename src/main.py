import tkinter as tk
from tkinter import filedialog, messagebox

from infrastructure.mongo_client import get_mongo_client
from infrastructure.document_repository import DocumentRepository
from core.document_service import DocumentService
from core.search_service import SearchService
from system.mongod_runner import MongoRunner

def start_ui():
    runner = MongoRunner()
    runner.run()

    client = get_mongo_client()
    db = client["documents"]
    repo = DocumentRepository(db)

    doc_service = DocumentService(repo)
    search_service = SearchService(repo)

    def upload_file():
        filepath = filedialog.askopenfilename()
        try:
            doc_service.process_and_save(filepath)
            messagebox.showinfo("Успех", "Документ успешно сохранён")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def search_query():
        query = query_entry.get()
        result_text.delete(1.0, tk.END)
        results = search_service.search(query)
        for doc in results:
            result_text.insert(tk.END, f"{doc['filename']}\n{doc['text'][:400]}...\n---\n")

    root = tk.Tk()
    root.title("Документы и Поиск")

    tk.Button(root, text="Загрузить документ", command=upload_file).pack(pady=10)
    tk.Label(root, text="Поисковый запрос:").pack()
    query_entry = tk.Entry(root, width=50)
    query_entry.pack()
    tk.Button(root, text="Найти", command=search_query).pack(pady=5)

    result_text = tk.Text(root, height=20, width=100)
    result_text.pack()

    root.mainloop()

if __name__ == "__main__":
    start_ui()
