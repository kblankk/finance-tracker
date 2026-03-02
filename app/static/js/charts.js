// FinanceTracker - Dashboard Charts

document.addEventListener('DOMContentLoaded', function() {
    const chartDefaults = {
        color: '#adb5bd',
        borderColor: 'rgba(255, 255, 255, 0.1)',
    };

    Chart.defaults.color = chartDefaults.color;
    Chart.defaults.borderColor = chartDefaults.borderColor;

    // Monthly Trend Chart (Line)
    fetch('/api/monthly-trend')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('trendChart');
            if (!ctx) return;
            new Chart(ctx, {
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
                                callback: function(v) { return 'R$ ' + v; }
                            }
                        }
                    }
                }
            });
        })
        .catch(() => {});

    // Expense by Category Chart (Doughnut)
    fetch('/api/expense-by-category')
        .then(r => r.json())
        .then(data => {
            const ctx = document.getElementById('expensePieChart');
            if (!ctx || data.labels.length === 0) return;
            new Chart(ctx, {
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
                            callbacks: {
                                label: function(ctx) {
                                    return ctx.label + ': R$ ' + ctx.parsed.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(() => {});
});
