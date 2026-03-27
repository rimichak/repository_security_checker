import requests
import re


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
    score = max(100 - (len(findings) * 20), 0)

    if score >= 80:
        return score, "Low Risk"
    elif score >= 50:
        return score, "Medium Risk"
    else:
        return score, "High Risk"


def generate_suggestions(findings):
    suggestions = []

    for f in findings:
        if "AWS Key" in f:
            suggestions.append("Move AWS keys to .env")
        elif "Google API Key" in f:
            suggestions.append("Restrict API keys")
        elif "Password" in f:
            suggestions.append("Use hashed passwords")
        elif "JWT" in f:
            suggestions.append("Avoid hardcoding JWT")

    return list(set(suggestions))