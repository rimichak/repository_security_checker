const BASE_URL = "http://localhost:8000";

// ================= MODAL =================
function openModal() {
    document.getElementById("authModal").style.display = "flex";
}

function closeModal() {
    document.getElementById("authModal").style.display = "none";
}

function showLogin() {
    document.getElementById("loginBox").style.display = "block";
    document.getElementById("registerBox").style.display = "none";
}

function showRegister() {
    document.getElementById("loginBox").style.display = "none";
    document.getElementById("registerBox").style.display = "block";
}

// ================= LOGOUT =================
function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("userEmail");
    location.reload();
}

// ================= VALIDATION =================
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ================= REGISTER =================
async function register() {
    const username = document.getElementById("reg_username").value.trim();
    const email = document.getElementById("reg_email").value.trim();
    const password = document.getElementById("reg_password").value.trim();

    if (!username || !email || !password) {
        alert("All fields are required ❌");
        return;
    }

    if (!isValidEmail(email)) {
        alert("Enter a valid email ❌");
        return;
    }

    try {
        const res = await fetch(`${BASE_URL}/register`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ username, email, password })
        });

        const data = await res.json();

        if (res.ok) {
            alert("Registration successful ✅");
            showLogin();
        } else {
            if (Array.isArray(data.detail)) {
                alert(data.detail[0].msg);
            } else {
                alert(data.detail || "Registration failed");
            }
        }

    } catch (err) {
        alert("Server error ❌");
        console.error(err);
    }
}

// ================= LOGIN =================
async function login() {
    const email = document.getElementById("login_email").value;
    const password = document.getElementById("login_password").value;

    if (!email || !password) {
        alert("All fields are required ❌");
        return;
    }

    if (!isValidEmail(email)) {
        alert("Enter valid email ❌");
        return;
    }

    try {
        const res = await fetch(`${BASE_URL}/login`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (data.access_token) {
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("userEmail", email);

            alert("Login successful 🚀");
            location.reload();
        } else {
            if (Array.isArray(data.detail)) {
                alert(data.detail[0].msg);
            } else {
                alert(data.detail || "Login failed");
            }
        }

    } catch (err) {
        alert("Server error ❌");
        console.error(err);
    }
}

// ================= ANALYZE =================
async function analyzeRepo() {
    const token = localStorage.getItem("token");
    const url = document.getElementById("repoUrl").value;

    if (!token) {
        alert("Please login first 🔐");
        openModal();
        return;
    }

    if (!url || !url.includes("github.com")) {
        alert("Enter valid GitHub URL ❌");
        return;
    }

    document.getElementById("result").innerHTML = "🔍 Scanning repository...";

    try {
        const res = await fetch(`${BASE_URL}/scan-repo`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ github_url: url })
        });

        const data = await res.json();

        if (res.ok) {
            renderCard(data);
        } else {
            if (Array.isArray(data.detail)) {
                alert(data.detail[0].msg);
            } else {
                alert(data.detail || "Error analyzing repository");
            }
        }

    } catch (err) {
        alert("Server error ❌");
        console.error(err);
    }
}

// ================= RENDER RESULT =================
function renderCard(data) {
    const riskClass = data.risk_level.toLowerCase().replace(" ", "-");

    document.getElementById("result").innerHTML = `
        <div class="card-header ${riskClass}">
            <h2>${data.owner}/${data.name}</h2>
            <div class="score">${data.score}</div>
            <p>${data.risk_level}</p>
        </div>

        <div class="metrics">
            <h3>🚨 Issues</h3>
            ${
                data.issues.length > 0
                ? data.issues.map(i => `<p>❌ ${i}</p>`).join("")
                : "<p>✅ No issues found</p>"
            }

            <h3>💡 Suggestions</h3>
            ${
                data.suggestions.length > 0
                ? data.suggestions.map(s => `<p>👉 ${s}</p>`).join("")
                : "<p>👍 No suggestions</p>"
            }
        </div>
    `;
}

// ================= ON LOAD =================
window.onload = () => {
    const token = localStorage.getItem("token");
    const email = localStorage.getItem("userEmail");

    if (token) {
        document.getElementById("heroSection").style.display = "none";
        document.getElementById("analyzeSection").style.display = "block";

        if (email) {
            document.getElementById("userEmail").innerText = email;
        }
    } else {
        document.getElementById("heroSection").style.display = "block";
        document.getElementById("analyzeSection").style.display = "none";
    }
};
