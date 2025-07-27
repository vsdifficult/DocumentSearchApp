import subprocess
import os

class MongoRunner:
    def __init__(self, mongo_path="mongo/bin/mongod.exe", db_path="mongo/data"):
        self.mongo_path = mongo_path
        self.db_path = db_path
        os.makedirs(self.db_path, exist_ok=True)

    def run(self):
        return subprocess.Popen([self.mongo_path, "--dbpath", self.db_path])
