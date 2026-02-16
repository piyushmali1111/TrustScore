document.addEventListener('DOMContentLoaded', async () => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user || user.role !== 'admin') {
        window.location.href = 'login.html';
        return;
    }

    const welcomeUser = document.getElementById('welcomeUser');
    if (welcomeUser) {
        welcomeUser.textContent = `Welcome, ${user.username}`;
    }

    // Logout logic
    // Logout logic with event delegation
    document.addEventListener('click', (e) => {
        if (e.target && (e.target.id === 'logoutBtn' || e.target.closest('#logoutBtn'))) {
            e.preventDefault();
            console.log('Logging out...');
            localStorage.removeItem('user');
            window.location.href = 'index.html';
        }
    });

    // Only run dashboard logic if value elements exist
    if (document.getElementById('totalSellers')) {
        try {
            const response = await fetch('/api/admin/dashboard');
            const data = await response.json();

            if (response.ok) {
                updateStats(data.stats);
                renderRiskChart(data.stats);
                renderScoreDistribution(data.sellers);
                populateSellersTable(data.sellers);
            }
        } catch (err) {
            console.error('Error fetching admin data:', err);
        }
    }
});

function updateStats(stats) {
    document.getElementById('totalSellers').textContent = stats.total_sellers;
    document.getElementById('avgTrustScore').textContent = stats.avg_trust_score;
    document.getElementById('highRiskCount').textContent = stats.high_risk_count;
    document.getElementById('lowRiskCount').textContent = stats.low_risk_count;
}

function renderRiskChart(stats) {
    const ctx = document.getElementById('riskChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                data: [stats.low_risk_count, stats.medium_risk_count, stats.high_risk_count],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#64748b' } }
            }
        }
    });
}

function renderScoreDistribution(sellers) {
    const scores = sellers.map(s => s.trust_score);
    const bins = [0, 0, 0, 0, 0]; // 0-20, 21-40, 41-60, 61-80, 81-100
    scores.forEach(s => {
        if (s <= 20) bins[0]++;
        else if (s <= 40) bins[1]++;
        else if (s <= 60) bins[2]++;
        else if (s <= 80) bins[3]++;
        else bins[4]++;
    });

    const ctx = document.getElementById('scoreDistributionChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-20', '21-40', '41-60', '61-80', '81-100'],
            datasets: [{
                label: 'Number of Sellers',
                data: bins,
                backgroundColor: '#6366f1',
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { color: '#64748b' } },
                x: { grid: { display: false }, ticks: { color: '#64748b' } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function populateSellersTable(sellers) {
    const tbody = document.getElementById('sellersBody');
    tbody.innerHTML = '';

    sellers.forEach(seller => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${seller.seller_id}</td>
            <td>${seller.name}</td>
            <td><span class="gradient-text font-bold" style="font-size: 1.1rem;">${seller.trust_score}</span></td>
            <td><strong>${seller.confidence_score}%</strong></td>
            <td><span class="trust-badge risk-${seller.risk_level.toLowerCase()}">${seller.risk_level}</span></td>
            <td><a href="admin_seller_details.html?id=${seller.seller_id}" class="btn btn-primary" style="padding: 6px 20px; border-radius: 6px; font-size: 0.85rem;">View</a></td>
        `;
        tbody.appendChild(tr);
    });
}
