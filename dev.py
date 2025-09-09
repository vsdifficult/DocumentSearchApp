import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Проверяет версию Python"""
    if sys.version_info < (3, 11, 1):
        print("Требуется Python 3.11.1 или выше")
        print(f"Текущая версия: {sys.version}")
        return False
    return True

def install_requirements():
    """Устанавливает зависимости"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError:
        print("Ошибка установки зависимостей")
        return False

def create_data_directory():
    """Создает директорию для данных"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return True

def run_app():
    """Запускает приложение"""
    os.environ["USE_SQLITE"] = "true"
    os.environ["EMBEDDING_MODEL"] = "cointegrated/rubert-tiny"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "uvicorn", 
            "src.api.app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\nПриложение остановлено")
    except Exception as e:
        print(f"Ошибка запуска: {e}")

if __name__ == "__main__":
    print("Запуск Document Search App...")
    
    if not check_python_version():
        sys.exit(1)
    
    print("Установка зависимостей...")
    if not install_requirements():
        sys.exit(1)
    
    print("Создание директорий...")
    create_data_directory()
    
    print("Запуск приложения на http://localhost:8000")
    print("Документация: http://localhost:8000/docs")
    run_app()