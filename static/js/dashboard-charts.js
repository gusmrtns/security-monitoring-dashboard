/**
 * static/js/dashboard-charts.js
 *
 * Busca os dados de cada gráfico via fetch() nos endpoints JSON do
 * blueprint dashboard e renderiza com Chart.js. Cada gráfico é
 * independente - se um endpoint falhar, os outros continuam funcionando.
 */

const SEVERITY_COLORS = { "Alta": "#dc2626", "Média": "#d97706", "Baixa": "#0891b2" };
const PALETTE = ["#2563eb", "#7c3aed", "#0891b2", "#16a34a", "#d97706", "#dc2626", "#db2777", "#4f46e5"];

async function fetchJSON(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Falha ao buscar ${url}: ${res.status}`);
    return res.json();
}

async function renderSeverityChart() {
    const data = await fetchJSON("/api/charts/severity");
    new Chart(document.getElementById("chart-severity"), {
        type: "doughnut",
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: data.labels.map(l => SEVERITY_COLORS[l] || "#64748b"),
            }],
        },
        options: { plugins: { legend: { labels: { color: "#e2e8f0" } } } },
    });
}

async function renderCategoriesChart() {
    const data = await fetchJSON("/api/charts/categories");
    new Chart(document.getElementById("chart-categories"), {
        type: "bar",
        data: {
            labels: data.labels,
            datasets: [{ data: data.values, backgroundColor: PALETTE }],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" } },
                y: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" }, beginAtZero: true },
            },
        },
    });
}

async function renderTimelineChart() {
    const data = await fetchJSON("/api/charts/timeline");
    new Chart(document.getElementById("chart-timeline"), {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                borderColor: "#2563eb",
                backgroundColor: "rgba(37, 99, 235, 0.15)",
                fill: true,
                tension: 0.3,
            }],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#94a3b8" }, grid: { display: false } },
                y: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" }, beginAtZero: true },
            },
        },
    });
}

async function renderTopIpsChart() {
    const data = await fetchJSON("/api/charts/top-ips");
    new Chart(document.getElementById("chart-top-ips"), {
        type: "bar",
        data: {
            labels: data.labels,
            datasets: [{ data: data.values, backgroundColor: "#dc2626" }],
        },
        options: {
            indexAxis: "y",
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#94a3b8" }, grid: { color: "#334155" }, beginAtZero: true },
                y: { ticks: { color: "#94a3b8" }, grid: { display: false } },
            },
        },
    });
}

document.addEventListener("DOMContentLoaded", () => {
    renderSeverityChart().catch(console.error);
    renderCategoriesChart().catch(console.error);
    renderTimelineChart().catch(console.error);
    renderTopIpsChart().catch(console.error);
});
