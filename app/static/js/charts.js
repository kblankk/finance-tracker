// FinanceTracker - Dashboard Charts

document.addEventListener('DOMContentLoaded', function() {
    function getThemeColors() {
        const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        return {
            text: isDark ? '#adb5bd' : '#495057',
            grid: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
        };
    }

    const colors = getThemeColors();
    Chart.defaults.color = colors.text;
    Chart.defaults.borderColor = colors.grid;

    const isPrivacy = () => document.body.classList.contains('privacy-mode');
    window.ftCharts = window.ftCharts || {};

    // Monthly Trend Chart (Line)
    fetch('/api/monthly-trend')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('trendChart');
            if (!ctx) return;
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Receitas',
                            data: data.income,
                            borderColor: '#75b798',
                            backgroundColor: 'rgba(117, 183, 152, 0.1)',
                            fill: true,
                            tension: 0.4,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                        },
                        {
                            label: 'Despesas',
                            data: data.expenses,
                            borderColor: '#ea868f',
                            backgroundColor: 'rgba(234, 134, 143, 0.1)',
                            fill: true,
                            tension: 0.4,
                            pointRadius: 4,
                            pointHoverRadius: 6,
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: { usePointStyle: true, padding: 20 }
                        },
                        tooltip: {
                            enabled: !isPrivacy(),
                            callbacks: {
                                label: function(ctx) {
                                    return ctx.dataset.label + ': R$ ' + ctx.parsed.y.toFixed(2);
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(v) {
                                    return isPrivacy() ? '' : 'R$ ' + v;
                                }
                            }
                        }
                    }
                }
            });
            window.ftCharts.dashboardTrend = chart;
        })
        .catch(() => {});

    // Expense by Category Chart (Doughnut)
    fetch('/api/expense-by-category')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('expensePieChart');
            if (!ctx || data.labels.length === 0) return;
            const chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: data.colors,
                        borderWidth: 0,
                        hoverOffset: 8,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '65%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                usePointStyle: true,
                                padding: 12,
                                font: { size: 11 }
                            }
                        },
                        tooltip: {
                            enabled: !isPrivacy(),
                            callbacks: {
                                label: function(ctx) {
                                    return ctx.label + ': R$ ' + ctx.parsed.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
            window.ftCharts.dashboardPie = chart;
        })
        .catch(() => {});

    // Reagir ao toggle de privacidade
    window.addEventListener('ft-privacy-change', function() {
        Object.values(window.ftCharts).forEach(function(chart) {
            if (chart.options.plugins && chart.options.plugins.tooltip) {
                chart.options.plugins.tooltip.enabled = !isPrivacy();
            }
            chart.update();
        });
    });
});
