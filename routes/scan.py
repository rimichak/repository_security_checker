from fastapi import APIRouter, HTTPException, Depends
from models.repo_model import RepoURL, SecurityResponse
from utils.auth_utils import get_current_user
from services.security_service import *
from database import repos_collection
from datetime import datetime
import requests

router = APIRouter()

@router.post("/scan-repo", response_model=SecurityResponse)
def scan_repo(payload: RepoURL, current_user=Depends(get_current_user)):
    owner, repo = extract_owner(payload.github_url)

    if not owner:
        raise HTTPException(status_code=400, detail="Invalid URL")

    response = requests.get(f"https://api.github.com/repos/{owner}/{repo}")
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Repo not found")

    data = response.json()

    files = get_repo_files(owner, repo)
    findings = scan_for_secrets(files)

    score, risk = analyze_security(findings)
    suggestions = generate_suggestions(findings)

    result = SecurityResponse(
        name=data["name"],
        owner=owner,
        score=score,
        risk_level=risk,
        issues=findings,
        suggestions=suggestions
    )

    repos_collection.insert_one({
        **result.model_dump(),
        "user_email": current_user["email"],
        "scanned_at": datetime.utcnow()
    })

    return result