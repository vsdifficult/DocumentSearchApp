from pymongo import MongoClient
from system.config import MONGO_URI

def get_mongo_client():
    return MongoClient(MONGO_URI)
