from pymongo import MongoClient
from app.config import settings

try:
    client = MongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=5000
    )

    client.admin.command("ping")

    print("MongoDB connection successful!")

except Exception as e:
    print("MongoDB connection failed:")
    print(e)