from pydantic import BaseSettings

class Settings(BaseSettings):
    milvus_host: str = "standalone"
    milvus_port: str = "19530"
    embedding_model: str = "cointegrated/rubert-tiny"
    
    class Config:
        env_file = ".env"

settings = Settings()