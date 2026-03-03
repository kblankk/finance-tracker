const monthNames = ['Janeiro','Fevereiro','Marco','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
let categoryChart = null;
let trendChart = null;
window.ftCharts = window.ftCharts || {};

const isPrivacy = () => document.body.classList.contains('privacy-mode');

function fmt(v) {
    if (isPrivacy()) return '***';
    return 'R$ ' + parseFloat(v).toFixed(2);
}

function loadComparison(m1, y1, m2, y2) {
    fetch(`/reports/api/comparison?month1=${m1}&year1=${y1}&month2=${m2}&year2=${y2}`)
        .then(r => r.json())
        .then(data => {
            document.getElementById('month1Title').textContent = monthNames[m1-1] + ' ' + y1;
            document.getElementById('month2Title').textContent = monthNames[m2-1] + ' ' + y2;

            document.getElementById('m1Income').textContent = fmt(data.month1.income);
            document.getElementById('m1Expense').textContent = fmt(data.month1.expense);
            document.getElementById('m1Balance').textContent = fmt(data.month1.balance);
            document.getElementById('m1Balance').className = 'fw-bold ' + (data.month1.balance >= 0 ? 'text-success' : 'text-danger');

            document.getElementById('m2Income').textContent = fmt(data.month2.income);
            document.getElementById('m2Expense').textContent = fmt(data.month2.expense);
            document.getElementById('m2Balance').textContent = fmt(data.month2.balance);
            document.getElementById('m2Balance').className = 'fw-bold ' + (data.month2.balance >= 0 ? 'text-success' : 'text-danger');

            // Store data for privacy toggle
            window._reportData = data;
            window._reportMonths = [m1, y1, m2, y2];

            // Category comparison chart
            const allCats = new Set();
            data.month1.categories.forEach(c => allCats.add(c.name));
            data.month2.categories.forEach(c => allCats.add(c.name));
            const labels = Array.from(allCats);

            const d1 = labels.map(l => {
                const c = data.month1.categories.find(x => x.name === l);
                return c ? c.amount : 0;
            });
            const d2 = labels.map(l => {
                const c = data.month2.categories.find(x => x.name === l);
                return c ? c.amount : 0;
            });

            if (categoryChart) categoryChart.destroy();
            categoryChart = new Chart(document.getElementById('categoryCompareChart'), {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        { label: monthNames[m1-1] + ' ' + y1, data: d1, backgroundColor: 'rgba(117, 183, 152, 0.7)' },
                        { label: monthNames[m2-1] + ' ' + y2, data: d2, backgroundColor: 'rgba(234, 134, 143, 0.7)' },
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { labels: { color: '#adb5bd' } },
                        tooltip: { enabled: !isPrivacy() }
                    },
                    scales: {
                        x: { ticks: { color: '#adb5bd' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                        y: {
                            ticks: {
                                color: '#adb5bd',
                                callback: function(v) { return isPrivacy() ? '' : 'R$ ' + v; }
                            },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        },
                    }
                }
            });
            window.ftCharts.reportCategory = categoryChart;
        });
}

function loadTrend() {
    fetch('/reports/api/trend?months=12')
        .then(r => r.json())
        .then(data => {
            if (trendChart) trendChart.destroy();
            trendChart = new Chart(document.getElementById('trendChart'), {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Receitas',
                            data: data.income,
                            borderColor: '#75b798',
                            backgroundColor: 'rgba(117, 183, 152, 0.1)',
                            fill: true, tension: 0.3,
                        },
                        {
                            label: 'Despesas',
                            data: data.expenses,
                            borderColor: '#ea868f',
                            backgroundColor: 'rgba(234, 134, 143, 0.1)',
                            fill: true, tension: 0.3,
                        },
                        {
                            label: 'Saldo',
                            data: data.balance,
                            borderColor: '#6ea8fe',
                            borderDash: [5, 5],
                            fill: false, tension: 0.3,
                        },
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { labels: { color: '#adb5bd' } },
                        tooltip: { enabled: !isPrivacy() }
                    },
                    scales: {
                        x: { ticks: { color: '#adb5bd' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                        y: {
                            ticks: {
                                color: '#adb5bd',
                                callback: function(v) { return isPrivacy() ? '' : 'R$ ' + v; }
                            },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        },
                    }
                }
            });
            window.ftCharts.reportTrend = trendChart;
        });
}

// Reagir ao toggle de privacidade
window.addEventListener('ft-privacy-change', function() {
    // Atualizar valores textuais dos cards
    if (window._reportData) {
        const data = window._reportData;
        document.getElementById('m1Income').textContent = fmt(data.month1.income);
        document.getElementById('m1Expense').textContent = fmt(data.month1.expense);
        document.getElementById('m1Balance').textContent = fmt(data.month1.balance);
        document.getElementById('m2Income').textContent = fmt(data.month2.income);
        document.getElementById('m2Expense').textContent = fmt(data.month2.expense);
        document.getElementById('m2Balance').textContent = fmt(data.month2.balance);
    }

    // Atualizar graficos
    Object.values(window.ftCharts).forEach(function(chart) {
        if (chart.options.plugins && chart.options.plugins.tooltip) {
            chart.options.plugins.tooltip.enabled = !isPrivacy();
        }
        chart.update();
    });
});
