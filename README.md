# 🔐 Repository Security Analyzer

A FastAPI-based tool that scans GitHub repositories for exposed secrets, security risks, and misconfigurations — helping developers identify vulnerabilities before attackers do.

---

## 🚀 Features

* 🔍 Scan public GitHub repositories
* 🔑 Detect exposed secrets:

  * AWS Keys
  * Google API Keys
  * Hardcoded passwords
  * JWT tokens
* 📊 Security scoring system (Low / Medium / High risk)
* 💡 Smart suggestions to fix vulnerabilities
* 🔐 User authentication using JWT
* 🗄️ MongoDB database for storing scan results

---

## 🧱 Tech Stack

* Backend: FastAPI
* Database: MongoDB
* Authentication: JWT (python-jose)
* Security: Passlib (bcrypt hashing)
* API Integration: GitHub REST API

---

## 📁 Project Structure

```
main.py
database.py
models/
  user_model.py
  repo_model.py
routes/
  auth.py
  scan.py
services/
  security_service.py
utils/
  auth_utils.py
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/repo-analyzer.git
cd repo-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup environment variables

Create a `.env` file:

```
SECRET_KEY=my_secret_key
GITHUB_TOKEN=my_github_token
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

### 5. Open API docs

```
http://127.0.0.1:8000/docs
```

---

## 🔐 Authentication Flow

1. Register user → `/register`
2. Login → `/login`
3. Get JWT token
4. Use token to scan repositories

---

## 📊 Example API

### Scan Repository

```
POST /scan-repo
```

Request:

```json
{
  "github_url": "https://github.com/user/repo"
}
```

---

## 📈 How it Works

1. Extract repo owner & name
2. Fetch repository files using GitHub API
3. Scan files using regex patterns
4. Detect secrets & vulnerabilities
5. Generate security score and suggestions
6. Store results in MongoDB

---

## 🚨 Problem Solved

Many developers accidentally push sensitive data (API keys, passwords) to GitHub.
This tool helps identify and fix those issues early.

---

## 🔥 Future Improvements

* Deep recursive scanning
* Parallel scanning for faster performance
* AI-based vulnerability detection
* Frontend dashboard (React)
* Private repository scanning

---

## 👨‍💻 Author

Rimi Chakraborty

---

## ⭐ Contribute

Feel free to fork and improve this project!
