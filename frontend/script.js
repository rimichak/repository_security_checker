const BASE_URL = "http://localhost:8000";

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

function logout() {
    localStorage.removeItem("token");
    location.reload();
}

async function register() {
    const username = reg_username.value;
    const email = reg_email.value;
    const password = reg_password.value;

    const res = await fetch(`${BASE_URL}/register`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, email, password})
    });

    const data = await res.json();
    alert(data.message || data.detail);
}

async function login() {
    const email = login_email.value;
    const password = login_password.value;

    const res = await fetch(`${BASE_URL}/login`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email, password})
    });

    const data = await res.json();

    if (data.access_token) {
        localStorage.setItem("token", data.access_token);
        alert("Login successful 🚀");
        location.reload();
    } else {
        alert("Login failed");
    }
}

async function analyzeRepo() {
    const token = localStorage.getItem("token");
    const url = repoUrl.value;

    if (!url.includes("github.com")) {
        alert("Enter valid GitHub URL");
        return;
    }

    document.getElementById("result").innerHTML = "🔍 Scanning...";

    const res = await fetch(`${BASE_URL}/scan-repo`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ github_url: url })
    });

    const data = await res.json();

    if (res.ok) renderCard(data);
    else alert(data.detail);
}

function renderCard(data) {
    document.getElementById("result").innerHTML = `
        <div class="card-header ${data.risk_level.toLowerCase().replace(" ", "-")}">
            <h2>${data.owner}/${data.name}</h2>
            <div class="score">${data.score}</div>
            <p>${data.risk_level}</p>
        </div>

        <div class="metrics">
            <h3>🚨 Issues</h3>
            ${data.issues.map(i => `<p>❌ ${i}</p>`).join("") || "None"}

            <h3>💡 Suggestions</h3>
            ${data.suggestions.map(s => `<p>👉 ${s}</p>`).join("") || "None"}
        </div>
    `;
}

window.onload = () => {
    if (localStorage.getItem("token")) {
        heroSection.style.display = "none";
        analyzeSection.style.display = "block";
    }
};
