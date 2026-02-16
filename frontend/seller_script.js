document.addEventListener('DOMContentLoaded', async () => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user || user.role !== 'seller') {
        window.location.href = 'login.html';
        return;
    }

    // Fallback for demo: if seller_id is missing, use '1'
    const sellerId = user.seller_id || '1';
    console.log('Fetching data for Seller ID:', sellerId);

    // Set Welcome Header (if on dashboard)
    const sellerName = document.getElementById('sellerName');
    if (sellerName && window.location.pathname.includes('reviews')) {
        sellerName.textContent = 'Customer Reviews'; // Static for reviews page
    } else if (sellerName) {
        sellerName.textContent = `${user.username}'s Dashboard`;
    }

    // Logout logic (Event Delegation)
    document.addEventListener('click', (e) => {
        if (e.target && (e.target.id === 'logoutBtn' || e.target.closest('#logoutBtn'))) {
            e.preventDefault();
            localStorage.removeItem('user');
            window.location.href = 'index.html';
        }
    });

    try {
        const response = await fetch(`/api/seller/dashboard?seller_id=${sellerId}`);
        const data = await response.json();

        if (response.ok) {
            // Check which page we are on
            if (window.location.pathname.includes('seller_reviews.html')) {
                renderReviewPage(data);
            } else {
                updateSellerUI(data); // Dashboard logic
            }
        } else {
            console.error('Server returned error:', data);
            alert(`Error fetching dashboard details: ${data.detail || response.statusText}`);
        }
    } catch (err) {
        console.error('Error fetching seller data:', err);
        alert('Exception fetching dashboard: ' + err.message);
    }
});

function renderReviewPage(data) {
    // Stats
    document.getElementById('pageAvgRating').textContent = data.summary.avg_rating;
    document.getElementById('pageTotalReviews').textContent = data.summary.total_reviews;

    // Calculate Positive %
    const total = data.summary.total_reviews;
    const positive = data.sentiment_analysis.positive;
    const posPercent = total > 0 ? Math.round((positive / total) * 100) : 0;
    document.getElementById('pagePositive').textContent = posPercent + '%';

    // Table
    const tbody = document.getElementById('allReviewsBody');
    tbody.innerHTML = '';

    if (data.reviews.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center p-4">No reviews found.</td></tr>';
        return;
    }

    // Sort by date desc (if available, otherwise rely on backend order)
    // Assuming backend sends reliable order or we sort manually here if needed
    // data.reviews.sort((a, b) => new Date(b.review_date) - new Date(a.review_date));

    data.reviews.forEach(rev => {
        const rating = Number(rev.rating);
        let sentimentBadge = '';
        if (rating >= 4) sentimentBadge = '<span class="trust-badge risk-low">Positive</span>';
        else if (rating === 3) sentimentBadge = '<span class="trust-badge risk-medium">Neutral</span>';
        else sentimentBadge = '<span class="trust-badge risk-high">Negative</span>';

        // Stars
        let stars = '';
        for (let i = 0; i < 5; i++) {
            stars += `<i class="${i < rating ? 'fas' : 'far'} fa-star" style="color: #f59e0b;"></i>`;
        }

        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid var(--border)';
        tr.innerHTML = `
            <td style="padding: 16px;">${new Date(rev.review_date).toLocaleDateString()}</td>
            <td style="padding: 16px;">${stars}</td>
            <td style="padding: 16px; color: var(--text-dim); max-width: 400px;">${rev.review_text}</td>
            <td style="padding: 16px;">${sentimentBadge}</td>
        `;
        tbody.appendChild(tr);
    });
}

function updateSellerUI(data) {
    const s = data.score_card;

    // Top Stats
    const trustScoreEl = document.getElementById('trustScore');
    if (trustScoreEl) trustScoreEl.textContent = s.trust_score;

    const confidenceScoreEl = document.getElementById('confidenceScore');
    if (confidenceScoreEl) confidenceScoreEl.textContent = s.confidence_score + '%';

    const riskBadge = document.getElementById('riskLevelBadge');
    if (riskBadge) {
        riskBadge.textContent = s.risk_level;
        riskBadge.className = 'trust-badge risk-' + s.risk_level.toLowerCase();
    }

    // Review Analysis
    if (s.stats) {
        const fakeEl = document.getElementById('fakeReviewsCount');
        if (fakeEl) fakeEl.textContent = s.stats.fake_reviews;

        const realEl = document.getElementById('realReviewsCount');
        if (realEl) realEl.textContent = s.stats.real_reviews;
    }

    // Detailed Metrics
    const m = s.metrics;
    if (document.getElementById('mDelivery')) {
        document.getElementById('mDelivery').textContent = m.delivery;
        document.getElementById('mReturn').textContent = m.return_rate_score;
        document.getElementById('mResponse').textContent = m.response;
        document.getElementById('mAuthenticity').textContent = m.authenticity;
        document.getElementById('mConsistency').textContent = m.consistency;
        document.getElementById('mAge').textContent = m.age;
    }

    // Recent Reviews Table (Dashboard version - Top 5)
    const tbody = document.getElementById('reviewsBody');
    if (tbody) {
        tbody.innerHTML = '';
        const recentReviews = data.reviews.slice(0, 5);
        if (recentReviews.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align:center; padding: 20px;">No reviews found.</td></tr>';
        } else {
            recentReviews.forEach(rev => {
                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid var(--border)';
                tr.innerHTML = `
                    <td style="padding: 16px;"><strong>${rev.rating}/5</strong></td>
                    <td style="padding: 16px; color: var(--text-dim);">${rev.review_text}</td>
                    <td style="padding: 16px; color: var(--text-dim); font-size: 0.9rem;">${new Date(rev.review_date).toLocaleDateString()}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    }

    // Charts (only render if canvas exists)
    if (document.getElementById('sellerRadarChart')) renderSellerRadar(data.score_card.metrics);
    if (document.getElementById('trendChart')) renderTrendChart(data.trend_data);
    if (document.getElementById('benchmarkChart')) renderBenchmarkChart(data.score_card, data.benchmarks);
    if (document.getElementById('sentimentChart')) renderSentimentChart(data.sentiment_analysis);
    if (document.getElementById('aiInsightsList')) populateInsights(data.insights);
}

function renderTrendChart(trendData) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Month 1', 'Month 2', 'Month 3', 'Month 4', 'Month 5', 'Current'],
            datasets: [{
                label: 'Trust Score History',
                data: trendData,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: false, min: 0, max: 100, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function renderBenchmarkChart(seller, benchmarks) {
    const ctx = document.getElementById('benchmarkChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Trust Score', 'Delivery', 'Response', 'Authenticity'],
            datasets: [
                {
                    label: 'You',
                    data: [seller.trust_score, seller.metrics.delivery, seller.metrics.response, seller.metrics.authenticity],
                    backgroundColor: '#3b82f6',
                    borderRadius: 4
                },
                {
                    label: 'Platform Average',
                    data: [benchmarks.avg_trust_score, benchmarks.avg_delivery, benchmarks.avg_response, benchmarks.avg_authenticity],
                    backgroundColor: '#94a3b8',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 100, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
            },
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

function renderSentimentChart(sentiment) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive (4-5★)', 'Neutral (3★)', 'Negative (1-2★)'],
            datasets: [{
                data: [sentiment.positive, sentiment.neutral, sentiment.negative],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { boxWidth: 12 } } }
        }
    });
}

function populateInsights(insights) {
    const container = document.getElementById('aiInsightsList');
    container.innerHTML = '';

    if (insights.length === 0) {
        container.innerHTML = '<p class="text-center text-dim">No critical insights at this time. Keep up the good work!</p>';
        return;
    }

    insights.forEach(item => {
        let alertClass = 'alert-green';
        if (item.type === 'warning') alertClass = 'alert-red'; // abusing red for warning visibility
        if (item.type === 'danger') alertClass = 'alert-red';
        if (item.type === 'info') alertClass = 'alert-green'; // utilizing green for info

        // Custom styling for warning/yellow if needed, but reusing existing classes for now
        const div = document.createElement('div');
        div.className = `review-alert ${alertClass}`;
        div.style.marginBottom = '12px';
        div.style.padding = '16px';

        div.innerHTML = `
            <div style="display: flex; align-items: flex-start;">
                <i class="fas ${item.icon} alert-icon" style="font-size: 1.2rem; margin-top: 2px;"></i>
                <div class="alert-content">
                    <h4 style="font-size: 0.95rem; margin-bottom: 2px;">${item.type.toUpperCase()}</h4>
                    <p style="font-size: 0.85rem; margin: 0; opacity: 0.9;">${item.msg}</p>
                </div>
            </div>
        `;
        container.appendChild(div);
    });
}

function renderSellerRadar(metrics) {
    const ctx = document.getElementById('sellerRadarChart').getContext('2d');
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Delivery', 'Returns', 'Response', 'Authenticity', 'Consistency', 'Age'],
            datasets: [{
                label: 'Metric Score',
                data: [
                    metrics.delivery,
                    metrics.return_rate_score,
                    metrics.response,
                    metrics.authenticity,
                    metrics.consistency,
                    metrics.age
                ],
                backgroundColor: 'rgba(59, 130, 246, 0.2)', // Blue tint
                borderColor: '#3b82f6',
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#3b82f6'
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(0,0,0,0.1)' },
                    grid: { color: 'rgba(0,0,0,0.1)' },
                    pointLabels: {
                        font: { size: 12, family: "'Outfit', sans-serif", weight: '600' },
                        color: '#64748b'
                    },
                    ticks: { display: false, max: 100, min: 0 }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}
