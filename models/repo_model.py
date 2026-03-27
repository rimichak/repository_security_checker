from pydantic import BaseModel, Field
from typing import List

class RepoURL(BaseModel):
    github_url: str = Field(..., example="https://github.com/user/repo")


class SecurityResponse(BaseModel):
    name: str
    owner: str
    score: int
    risk_level: str
    issues: List[str]
    suggestions: List[str]