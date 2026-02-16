const API_BASE = "/api";

// --- Utility Functions ---
function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// --- Dashboard Logic ---
async function loadDashboard() {
    if (!document.getElementById("dashboard-stats")) return;

    try {
        const statsRes = await fetch(`${API_BASE}/dashboard-stats`);
        const stats = await statsRes.json();

        document.getElementById("total-sellers").innerText = stats.total_sellers;
        document.getElementById("avg-score").innerText = stats.avg_trust_score;
        document.getElementById("high-risk").innerText = stats.high_risk_count;
        document.getElementById("low-risk").innerText = stats.low_risk_count;

        const riskRes = await fetch(`${API_BASE}/risk-analysis`);
        const riskData = await riskRes.json();

        renderRiskChart(riskData.distribution);
        renderScoreDistribution(riskData.scores);

    } catch (e) {
        console.error("Error loading dashboard data:", e);
    }
}

function renderRiskChart(distribution) {
    const ctx = document.getElementById("riskParamsChart").getContext("2d");
    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Low Risk", "Medium Risk", "High Risk"],
            datasets: [{
                data: [distribution.Low, distribution.Medium, distribution.High],
                backgroundColor: ["#28a745", "#ffc107", "#dc3545"]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });
}

function renderScoreDistribution(scores) {
    const ctx = document.getElementById("trustScoreChart").getContext("2d");
    // Create bins for histogram
    const bins = [0, 20, 40, 60, 80, 100];
    const data = [0, 0, 0, 0, 0];
    scores.forEach(s => {
        if (s < 20) data[0]++;
        else if (s < 40) data[1]++;
        else if (s < 60) data[2]++;
        else if (s < 80) data[3]++;
        else data[4]++;
    });

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["0-20", "20-40", "40-60", "60-80", "80-100"],
            datasets: [{
                label: "Number of Sellers",
                data: data,
                backgroundColor: "#0056b3"
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// --- Seller List Logic ---
async function loadSellerList() {
    const tableBody = document.getElementById("seller-table-body");
    if (!tableBody) return;

    try {
        const res = await fetch(`${API_BASE}/sellers`);
        const sellers = await res.json();

        tableBody.innerHTML = "";
        sellers.forEach(seller => {
            const row = document.createElement("tr");
            let badgeClass = "badge-low";
            if (seller.risk_level === "Medium") badgeClass = "badge-medium";
            if (seller.risk_level === "High") badgeClass = "badge-high";

            row.innerHTML = `
                <td>${seller.seller_id}</td>
                <td>${seller.name}</td>
                <td>${seller.trust_score}</td>
                <td>${seller.confidence_score}%</td>
                <td><span class="badge ${badgeClass}">${seller.risk_level}</span></td>
                <td><a href="seller.html?id=${seller.seller_id}" class="btn">View</a></td>
            `;
            tableBody.appendChild(row);
        });

    } catch (e) {
        console.error("Error loading seller list data:", e);
    }
}

// --- Seller Profile Logic ---
async function loadSellerProfile() {
    const profileContainer = document.getElementById("seller-profile");
    if (!profileContainer) return;

    const sellerId = getQueryParam("id");
    if (!sellerId) {
        profileContainer.innerHTML = "<p>No seller ID provided.</p>";
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/seller/${sellerId}`);
        if (!res.ok) throw new Error("Seller not found");

        const seller = await res.json();

        document.getElementById("seller-name").innerText = seller.name;
        document.getElementById("trust-score-val").innerText = seller.trust_score;
        document.getElementById("risk-label").innerText = seller.risk_level;
        document.getElementById("risk-label").className = `badge badge-${seller.risk_level.toLowerCase()}`;
        document.getElementById("confidence-val").innerText = seller.confidence_score + "%";

        // Update metrics
        document.getElementById("score-delivery").innerText = seller.metrics.delivery;
        document.getElementById("score-return").innerText = seller.metrics.return_rate_score;
        document.getElementById("score-response").innerText = seller.metrics.response;
        document.getElementById("score-auth").innerText = seller.metrics.authenticity;
        document.getElementById("score-const").innerText = seller.metrics.consistency;
        document.getElementById("score-age").innerText = seller.metrics.age;

        // Stats
        document.getElementById("real-reviews").innerText = seller.stats.real_reviews;
        document.getElementById("fake-reviews").innerText = seller.stats.fake_reviews;

        renderMetricsChart(seller.metrics);

    } catch (e) {
        profileContainer.innerHTML = `<p>Error: ${e.message}</p>`;
    }
}

function renderMetricsChart(metrics) {
    const ctx = document.getElementById("metricsChart").getContext("2d");
    new Chart(ctx, {
        type: "radar",
        data: {
            labels: ["Delivery", "Returns", "Response", "Authenticity", "Consistency", "Account Age"],
            datasets: [{
                label: "Seller Metrics",
                data: [
                    metrics.delivery,
                    metrics.return_rate_score,
                    metrics.response,
                    metrics.authenticity,
                    metrics.consistency,
                    metrics.age
                ],
                backgroundColor: "rgba(0, 86, 179, 0.2)",
                borderColor: "#0056b3",
                pointBackgroundColor: "#0056b3"
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    suggestedMin: 0,
                    suggestedMax: 100
                }
            }
        }
    });
}

// --- Risk Analysis Logic ---
async function loadRiskAnalysis() {
    if (!document.getElementById("low-risk-count")) return;

    try {
        const statsRes = await fetch(`${API_BASE}/dashboard-stats`);
        const stats = await statsRes.json();

        const sellersRes = await fetch(`${API_BASE}/sellers`);
        const sellers = await sellersRes.json();

        const riskRes = await fetch(`${API_BASE}/risk-analysis`);
        const riskData = await riskRes.json();

        // Update summary cards
        document.getElementById("low-risk-count").innerText = stats.low_risk_count;
        document.getElementById("medium-risk-count").innerText = stats.medium_risk_count;
        document.getElementById("high-risk-count").innerText = stats.high_risk_count;

        const totalFakeReviews = sellers.reduce((sum, s) => sum + (s.stats.fake_reviews || 0), 0);
        document.getElementById("total-fake-reviews").innerText = totalFakeReviews;

        // Render charts
        renderRiskAnalysisCharts(riskData, sellers, stats);

        // Update insights
        updateInsights(stats, sellers, totalFakeReviews);

    } catch (e) {
        console.error("Error loading risk analysis:", e);
    }
}

function renderRiskAnalysisCharts(riskData, sellers, stats) {
    // Trust Score Histogram
    const histCtx = document.getElementById("trustScoreHistogram");
    if (histCtx) {
        const data = [0, 0, 0, 0, 0];
        riskData.scores.forEach(s => {
            if (s < 20) data[0]++;
            else if (s < 40) data[1]++;
            else if (s < 60) data[2]++;
            else if (s < 80) data[3]++;
            else data[4]++;
        });

        new Chart(histCtx.getContext("2d"), {
            type: "bar",
            data: {
                labels: ["0-20", "20-40", "40-60", "60-80", "80-100"],
                datasets: [{
                    label: "Number of Sellers",
                    data: data,
                    backgroundColor: [
                        "rgba(239, 68, 68, 0.8)",
                        "rgba(251, 146, 60, 0.8)",
                        "rgba(250, 204, 21, 0.8)",
                        "rgba(52, 211, 153, 0.8)",
                        "rgba(16, 185, 129, 0.8)"
                    ],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // Risk Pie Chart
    const pieCtx = document.getElementById("riskPieChart");
    if (pieCtx) {
        new Chart(pieCtx.getContext("2d"), {
            type: "doughnut",
            data: {
                labels: ["Low Risk", "Medium Risk", "High Risk"],
                datasets: [{
                    data: [riskData.distribution.Low, riskData.distribution.Medium, riskData.distribution.High],
                    backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: "bottom" }
                }
            }
        });
    }

    // Top Sellers Chart
    const topCtx = document.getElementById("topSellersChart");
    if (topCtx) {
        const topSellers = sellers
            .sort((a, b) => b.trust_score - a.trust_score)
            .slice(0, 10);

        new Chart(topCtx.getContext("2d"), {
            type: "bar",
            data: {
                labels: topSellers.map(s => s.name),
                datasets: [{
                    label: "Trust Score",
                    data: topSellers.map(s => s.trust_score),
                    backgroundColor: "rgba(102, 126, 234, 0.8)",
                    borderRadius: 8
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    // Fake Reviews Chart
    const fakeCtx = document.getElementById("fakeReviewsChart");
    if (fakeCtx) {
        const sellersWithFakes = sellers
            .filter(s => s.stats.fake_reviews > 0)
            .sort((a, b) => b.stats.fake_reviews - a.stats.fake_reviews)
            .slice(0, 10);

        new Chart(fakeCtx.getContext("2d"), {
            type: "bar",
            data: {
                labels: sellersWithFakes.map(s => s.name),
                datasets: [{
                    label: "Fake Reviews",
                    data: sellersWithFakes.map(s => s.stats.fake_reviews),
                    backgroundColor: "rgba(239, 68, 68, 0.8)",
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    }
}

function updateInsights(stats, sellers, totalFakeReviews) {
    const totalReviews = sellers.reduce((sum, s) => sum + s.stats.real_reviews + s.stats.fake_reviews, 0);
    const fakeRate = (totalFakeReviews / totalReviews * 100).toFixed(1);

    document.getElementById("avg-trust-insight").innerText =
        `The platform average is ${stats.avg_trust_score}, indicating ${stats.avg_trust_score > 70 ? 'good overall' : 'moderate'} seller quality.`;

    document.getElementById("risk-distribution-insight").innerText =
        `${stats.low_risk_count} sellers (${(stats.low_risk_count / stats.total_sellers * 100).toFixed(0)}%) are low risk, ${stats.medium_risk_count} medium, and ${stats.high_risk_count} high risk.`;

    document.getElementById("fake-rate-insight").innerText =
        `${totalFakeReviews} fake reviews detected out of ${totalReviews} total (${fakeRate}% detection rate).`;
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
    loadSellerList();
    loadSellerProfile();
    loadRiskAnalysis();
});
