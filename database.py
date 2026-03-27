from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient("mongodb://localhost:27017/")
db = client["repo_analyzer_db"]

repos_collection = db["repositories"]
users_collection = db["users"]

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60