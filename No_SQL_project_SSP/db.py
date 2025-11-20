# db.py
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "Students_Performance"

def get_client():
    return MongoClient(MONGO_URI)

def get_db():
    client = get_client()
    return client[DB_NAME]

def get_predictions_collection():
    return get_db()["predicted_results"]

def get_users_collection():
    return get_db()["users"]

def seed_default_users():
    """
    Ensure default users exist:
      - admin / admin123 (role: admin)
      - student / student123 (role: student)
    Passwords are stored in plain text for demo; replace with hashing for production.
    """
    users = get_users_collection()
    # create index on username unique
    users.create_index([("username", ASCENDING)], unique=True)
    defaults = [
        {"username": "admin", "password": "admin123", "role": "admin", "created_at": datetime.utcnow()},
        {"username": "student", "password": "student123", "role": "student", "created_at": datetime.utcnow()},
    ]
    for u in defaults:
        try:
            users.insert_one(u)
        except Exception:
            # user already exists -> ignore
            pass
