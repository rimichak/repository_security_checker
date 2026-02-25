const BASE_URL = "http://localhost:8000";

/* ===========================
   MODAL UI HELPERS (NEW)
=========================== */

function openModal(){
    document.getElementById("authModal").style.display = "flex";
}

function closeModal(){
    document.getElementById("authModal").style.display = "none";
}

/* ===========================
   AUTH TAB SWITCHING
=========================== */

function showLogin() {
    document.getElementById("loginBox").style.display = "block";
    document.getElementById("registerBox").style.display = "none";
}

function showRegister() {
    document.getElementById("loginBox").style.display = "none";
    document.getElementById("registerBox").style.display = "block";
}

/* ===========================
   LOGOUT
=========================== */

function logout() {
    localStorage.removeItem("token");

    document.getElementById("analyzeSection").style.display = "none";
    document.getElementById("heroSection").style.display = "block";
}

/* ===========================
   REGISTER
=========================== */

async function register() {
    const username = document.getElementById("reg_username").value;
    const email = document.getElementById("reg_email").value;
    const password = document.getElementById("reg_password").value;

    const res = await fetch(`${BASE_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
    });

    const data = await res.json();

    if (res.ok) {
        alert("Registration successful! Please login.");
        showLogin();
    } else {
        alert(data.detail || "Registration failed");
    }
}

/* ===========================
   LOGIN
=========================== */

async function login() {
    const email = document.getElementById("login_email").value;
    const password = document.getElementById("login_password").value;

    const res = await fetch(`${BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (res.ok && data.access_token) {
        localStorage.setItem("token", data.access_token);

        closeModal();
        document.getElementById("heroSection").style.display = "none";
        document.getElementById("analyzeSection").style.display = "block";
    } else {
        alert(data.detail || "Login failed");
    }
}

/* ===========================
   SCORE CATEGORY LOGIC
=========================== */

function getCategory(score) {
    if (score < 40) return "poor";
    if (score < 60) return "fair";
    if (score < 80) return "good";
    return "excellent";
}

function getMessage(category) {
    if (category === "poor") return ["Do Not Use", "fail"];
    if (category === "fair") return ["Use With Caution", "warn"];
    if (category === "good") return ["Safe to Use", "pass"];
    return ["Highly Recommended", "pass"];
}

function formatDate(dateString) {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString();
}

/* ===========================
   ANALYZE REPO
=========================== */

async function analyzeRepo() {
    const token = localStorage.getItem("token");

    if (!token) {
        alert("Please login first");
        openModal();
        return;
    }

    const url = document.getElementById("repoUrl").value;

    const res = await fetch(`${BASE_URL}/repo-metadata`, {
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
        alert(data.detail || "Error analyzing repository");
    }
}

/* ===========================
   RENDER RESULT CARD
=========================== */

function renderCard(data) {
    const category = getCategory(data.score);
    const [msg, msgClass] = getMessage(category);

    document.getElementById("result").innerHTML = `
        <div class="repo-header">
            <h2>${data.owner} / ${data.name}</h2>
            <p>${data.description || "No description available"}</p>
        </div>

        <div class="card-result">
            <div class="card-header ${category}">
                <div>${category.toUpperCase()}</div>
                <div class="score" id="scoreValue">0</div>
            </div>

            <div class="metrics">
                <div><span>⭐ Stars</span><b>${data.stars}</b></div>
                <div><span>🍴 Forks</span><b>${data.forks}</b></div>
                <div><span>🧠 Language</span><b>${data.language || "N/A"}</b></div>
                <div><span>📅 Created</span><b>${formatDate(data.created_at)}</b></div>
                <div><span>🔄 Updated</span><b>${formatDate(data.updated_at)}</b></div>
            </div>

            <div class="footer ${msgClass}">
                <strong>${msg}</strong>
            </div>
        </div>
    `;

    animateScore(data.score);
}

/* ===========================
   SCORE ANIMATION (NEW)
=========================== */

function animateScore(finalScore) {
    let current = 0;
    const el = document.getElementById("scoreValue");

    const interval = setInterval(() => {
        current += 2;
        el.innerText = current;

        if (current >= finalScore) {
            el.innerText = finalScore;
            clearInterval(interval);
        }
    }, 20);
}

/* ===========================
   AUTO LOGIN ON REFRESH
=========================== */

window.onload = function() {
    const token = localStorage.getItem("token");

    if (token) {
        document.getElementById("heroSection").style.display = "none";
        document.getElementById("analyzeSection").style.display = "block";
    }
}