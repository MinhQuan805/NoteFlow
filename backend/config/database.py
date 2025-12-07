import os
from dotenv import load_dotenv

load_dotenv()

USE_LOCAL_DB = os.getenv("USE_LOCAL_DB", "false").lower() == "true"

if USE_LOCAL_DB:
    print("Using LOCAL database (TinyDB)")
    from config.local_backend import LocalBackend
    db = LocalBackend()
else:
    print("Using CLOUD database (MongoDB)")
    from config.mongo_backend import MongoBackend
    db = MongoBackend()
