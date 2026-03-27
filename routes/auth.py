from fastapi import APIRouter, HTTPException
from models.user_model import UserRegister, UserLogin
from database import users_collection
from utils.auth_utils import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post("/register")
def register(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email exists")

    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password)
    })

    return {"message": "User registered"}


@router.post("/login")
def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})

    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user["email"]})

    return {"access_token": token, "token_type": "bearer"}