from pymongo import MongoClient
from app.config import settings


client = MongoClient(
    settings.mongodb_uri,
    maxPoolSize=10,
    serverSelectionTimeoutMS=5000
)

db = client[settings.database_name]

users_collection = db["users"]
jobs_collection = db["jobs"]
notifications_collection = db["notifications"]
agent_logs_collection = db["agent_logs"]


# Prevent the same job URL from being stored twice
jobs_collection.create_index(
    "url",
    unique=True
)