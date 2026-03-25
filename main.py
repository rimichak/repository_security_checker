from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from fastapi.security import OAuth2PasswordBearer
import requests
import re
from typing import Optional, List
from pymongo import MongoClient
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


client = MongoClient("mongodb://localhost:27017/")
db = client["repo_analyzer_db"]
repos_collection = db["repositories"]
users_collection = db["users"]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = users_collection.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



class RepoURL(BaseModel):
    github_url: str = Field(..., example="https://github.com/user/repo")


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class SecurityResponse(BaseModel):
    name: str
    owner: str
    score: int
    risk_level: str
    issues: List[str]
    suggestions: List[str]


def extract_owner(url: str):
    pattern = r"https://github\.com/([^/]+)/([^/]+?)(?:\.git|/)?$"
    match = re.match(pattern, url)

    if not match:
        return None, None

    return match.group(1), match.group(2)


def get_repo_files(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    response = requests.get(url, timeout=5)

    if response.status_code != 200:
        return []

    return response.json()


def scan_for_secrets(files):
    patterns = {
        "AWS Key": r"AKIA[0-9A-Z]{16}",
        "Google API Key": r"AIza[0-9A-Za-z-_]{35}",
        "Password": r"password\s*=\s*['\"].+['\"]",
        "JWT Token": r"eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+",
    }

    findings = []

    for file in files:
        if file["type"] == "file" and file.get("download_url"):
            try:
                content = requests.get(file["download_url"], timeout=5).text

                for name, pattern in patterns.items():
                    if re.search(pattern, content):
                        findings.append(f"{name} found in {file['name']}")

            except:
                continue

    return findings


def analyze_security(findings):
    score = 100

    for _ in findings:
        score -= 20

    score = max(score, 0)

    if score >= 80:
        level = "Low Risk"
    elif score >= 50:
        level = "Medium Risk"
    else:
        level = "High Risk"

    return score, level


def generate_suggestions(findings):
    suggestions = []

    for f in findings:
        if "AWS Key" in f:
            suggestions.append("Move AWS keys to environment variables (.env)")
        elif "Google API Key" in f:
            suggestions.append("Restrict API key usage and move to secure storage")
        elif "Password" in f:
            suggestions.append("Use hashed passwords (bcrypt) instead of plain text")
        elif "JWT" in f:
            suggestions.append("Store JWT securely and avoid hardcoding")

    return list(set(suggestions))



@app.post("/register")
def register(user: UserRegister):
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


@app.post("/scan-repo", response_model=SecurityResponse)
def scan_repo(payload: RepoURL, current_user=Depends(get_current_user)):
    owner, repo = extract_owner(payload.github_url)

    if not owner or not repo:
        raise HTTPException(status_code=400, detail="Invalid GitHub URL")

    
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url, timeout=5)

    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Repository not found")

    data = response.json()

    
    files = get_repo_files(owner, repo)
    findings = scan_for_secrets(files)

    
    score, risk_level = analyze_security(findings)
    suggestions = generate_suggestions(findings)

    result = SecurityResponse(
        name=data["name"],
        owner=owner,
        score=score,
        risk_level=risk_level,
        issues=findings,
        suggestions=suggestions
    )

    
    repos_collection.insert_one({
        **result.model_dump(),
        "user_email": current_user["email"],
        "scanned_at": datetime.utcnow()
    })

    return result
