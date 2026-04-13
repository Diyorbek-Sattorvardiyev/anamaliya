const apiPrefix = "/api/v1";
let token = "";
let lastAlertId = 0;

const landingContent = document.getElementById("landingContent");
const statusText = document.getElementById("statusText");
const statusBadge = document.getElementById("statusBadge");
const dashboard = document.getElementById("dashboard");
const alertList = document.getElementById("alertList");
const suspiciousList = document.getElementById("suspiciousList");
const totalAnomalies = document.getElementById("totalAnomalies");
const topIp = document.getElementById("topIp");
const protocolSummary = document.getElementById("protocolSummary");
const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const liveTrafficChart = new Chart(document.getElementById("liveTrafficChart"), {
  type: "line",
  data: {
    labels: [],
    datasets: [{
      label: "Paket hajmi",
      data: [],
      borderColor: "#67f7d4",
      backgroundColor: "rgba(103, 247, 212, 0.16)",
      fill: true,
      tension: 0.35
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: "#d8efed" } } },
    scales: {
      x: { ticks: { color: "#8eb0ad" }, grid: { color: "rgba(255,255,255,0.06)" } },
      y: { ticks: { color: "#8eb0ad" }, grid: { color: "rgba(255,255,255,0.06)" } }
    }
  }
});

const anomalyTimelineChart = new Chart(document.getElementById("anomalyTimelineChart"), {
  type: "bar",
  data: { labels: [], datasets: [{ label: "Anomaliya bali", data: [], backgroundColor: [] }] },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: "#d8efed" } } },
    scales: {
      x: { ticks: { color: "#8eb0ad" }, grid: { color: "rgba(255,255,255,0.06)" } },
      y: {
        min: 0,
        max: 1,
        ticks: { color: "#8eb0ad" },
        grid: { color: "rgba(255,255,255,0.06)" }
      }
    }
  }
});

const protocolChart = new Chart(document.getElementById("protocolChart"), {
  type: "doughnut",
  data: { labels: [], datasets: [{ data: [], backgroundColor: ["#67f7d4", "#ffb84d", "#7df0b1", "#ff7d66", "#6ed3ff"] }] },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: "#d8efed" } } }
  }
});

function authHeaders() {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function setStatus(message, connected = false) {
  statusText.textContent = message;
  statusBadge.classList.toggle("connected", connected);
}

function showDashboard() {
  landingContent.classList.add("hidden");
  dashboard.classList.remove("hidden");
}

async function login(event) {
  event?.preventDefault();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  setStatus("Tizimga kirilmoqda...");

  const res = await fetch(`${apiPrefix}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Kirish amalga oshmadi" }));
    setStatus(typeof error.detail === "string" ? error.detail : "Kirish amalga oshmadi");
    return;
  }

  const data = await res.json();
  token = data.access_token;
  setStatus("Ulandi", true);
  showDashboard();

  if (Notification.permission === "default") {
    Notification.requestPermission();
  }

  await refreshAll();
}

async function register(event) {
  event?.preventDefault();

  const full_name = document.getElementById("registerName").value.trim();
  const email = document.getElementById("registerEmail").value.trim();
  const password = document.getElementById("registerPassword").value;

  setStatus("Akkaunt yaratilmoqda...");

  const res = await fetch(`${apiPrefix}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ full_name, email, password })
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Ro‘yxatdan o‘tish amalga oshmadi" }));
    setStatus(typeof error.detail === "string" ? error.detail : "Ro‘yxatdan o‘tish amalga oshmadi");
    return;
  }

  const data = await res.json();
  token = data.access_token;
  document.getElementById("email").value = email;
  document.getElementById("password").value = password;
  setStatus("Akkaunt yaratildi va tizimga ulandi", true);
  showDashboard();
  await refreshAll();
}

async function simulateTraffic() {
  if (!token) return;
  setStatus("Sun'iy trafik yuborilmoqda...", true);
  await fetch(`${apiPrefix}/traffic/ingest`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ packets: [], simulate_count: 40, async_mode: false })
  });
  setStatus("Ulandi", true);
  await refreshAll();
}

async function trainModels() {
  if (!token) return;
  setStatus("Model qayta o‘qitilmoqda...", true);
  await fetch(`${apiPrefix}/train-model`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ samples: 7000, epochs: 20 })
  });
  setStatus("Ulandi", true);
}

function renderHeatmap(points) {
  const heatmap = document.getElementById("heatmap");
  heatmap.innerHTML = "";
  const recent = points.slice(-12);
  for (const point of recent) {
    const score = point.anomaly_score;
    const intensity = Math.min(255, Math.floor(score * 255));
    const color = `rgb(255, ${255 - intensity}, ${120 - Math.floor(intensity / 2)})`;

    const cell = document.createElement("div");
    cell.className = "heat-cell";
    cell.style.background = color;
    cell.textContent = score.toFixed(2);
    heatmap.appendChild(cell);
  }
}

async function fetchLive() {
  if (!token) return;

  const res = await fetch(`${apiPrefix}/traffic/live`, { headers: { ...authHeaders() } });
  if (!res.ok) return;

  const data = await res.json();
  const points = data.points;

  totalAnomalies.textContent = String(data.total_anomalies);
  topIp.textContent = data.top_suspicious_ips[0]?.src_ip ?? "-";
  protocolSummary.textContent = Object.keys(data.protocol_distribution).join(", ") || "-";

  liveTrafficChart.data.labels = points.map((p) => new Date(p.timestamp).toLocaleTimeString());
  liveTrafficChart.data.datasets[0].data = points.map((p) => p.packet_size);
  liveTrafficChart.update();

  anomalyTimelineChart.data.labels = points.map((p) => new Date(p.timestamp).toLocaleTimeString());
  anomalyTimelineChart.data.datasets[0].data = points.map((p) => p.anomaly_score);
  anomalyTimelineChart.data.datasets[0].backgroundColor = points.map((p) => p.is_anomaly ? "#f05f64" : "#2eca8b");
  anomalyTimelineChart.update();

  protocolChart.data.labels = Object.keys(data.protocol_distribution);
  protocolChart.data.datasets[0].data = Object.values(data.protocol_distribution);
  protocolChart.update();

  suspiciousList.innerHTML = "";
  for (const ip of data.top_suspicious_ips) {
    const li = document.createElement("li");
    li.textContent = `${ip.src_ip} -> ${ip.anomaly_count} ta anomaliya`;
    suspiciousList.appendChild(li);
  }

  renderHeatmap(points);
}

async function fetchAlerts() {
  if (!token) return;

  const res = await fetch(`${apiPrefix}/alerts?limit=20`, { headers: { ...authHeaders() } });
  if (!res.ok) return;
  const alerts = await res.json();

  alertList.innerHTML = "";
  for (const alert of alerts) {
    const li = document.createElement("li");
    li.textContent = `[${alert.severity}] ${alert.message}`;
    alertList.appendChild(li);

    if (alert.id > lastAlertId && Notification.permission === "granted") {
      new Notification("Tarmoq anomaliyasi ogohlantirishi", { body: alert.message });
    }
  }

  if (alerts.length > 0) {
    lastAlertId = Math.max(lastAlertId, ...alerts.map((a) => a.id));
  }
}

async function refreshAll() {
  await Promise.all([fetchLive(), fetchAlerts()]);
}

document.getElementById("simulateBtn").addEventListener("click", simulateTraffic);
document.getElementById("trainBtn").addEventListener("click", trainModels);
loginForm.addEventListener("submit", login);
registerForm.addEventListener("submit", register);

setInterval(refreshAll, 4000);
