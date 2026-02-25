from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer
import requests
import re
from typing import Optional
from pymongo import MongoClient
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()
SECRET_KEY= os.getenv("SECRET_KEY")

client = MongoClient("mongodb://localhost:27017/")
db = client["repo_analyzer_db"]
collections = db["repositories"]
users_collection = db["users"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

algorithm = "HS256"
Access_token_expire_minutes = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")


class repourl(BaseModel):
    github_url: str = Field(..., example= "https://github.com/rimichak/Insurance-policy-red-flag-ditector")

class response_data(BaseModel):
    name: str
    owner: str
    description: Optional[str]
    stars: int
    forks: int
    language: Optional[str]
    created_at: str
    updated_at: str
    score: int
    insights: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
class UserLogin(BaseModel):
    email: str
    password: str

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=Access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=algorithm)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])
        email= payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = users_collection.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="user not find")
        return user
    
    except JWTError:
        raise HTTPException(status_code=401, detail="invalid token")


def extract_owner(url: str):
    pattern = r"https://github\.com/([^/]+)/([^/]+?)(?:\.git|/)?$"

    match = re.match(pattern, url)

    if not match:
        return None, None
    return match.group(1), match.group(2)

def analyze_data(data):
    score = 0
    insights = []

    if data["stargazers_count"] > 100:
        score += 3
        insights.append("Popular repo")
    elif data["stargazers_count"] > 10:
        score += 1
        insights.append("Decent Popularity")

    if data["forks_count"] > 10:
        score += 2
        insights.append("Good community Engagement")

    if data["license"]:
        score += 2
        insights.append("License present")

    return score, ",".join(insights)

@app.post("/register")
def register(user: UserRegister):
    print("PASSWORD RECEIVED:", user.password)
    print("PASSWORD LENGTH:", len(user.password))
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password)
    })
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": db_user["email"]})
    return {"access_token": token, "token_type": "bearer"}
    


@app.post("/repo-metadata", response_model = response_data)
def get_repo_metadata(payload: repourl, current_user=Depends(get_current_user)):
    owner, repo = extract_owner(payload.github_url)

    if not owner or not repo:
        raise HTTPException(status_code= 400, detail="invalid github repository")
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url)


    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Repository not found")

    data = response.json()
    score, insights = analyze_data(data)
    result = response_data(
        name=data["name"],
        owner=owner,
        description=data["description"],
        stars=data["stargazers_count"],
        forks=data["forks_count"],
        language=data["language"],
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        score=score,
        insights=insights
    )

    collections.insert_one({
        **result.model_dump(),
        "user_email": current_user["email"]
        })

    return result
                             


