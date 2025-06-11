function initializeDashboard(moodData) {
    // Process the data
    const moodLabels = moodData.map(d => new Date(d.date).toLocaleDateString());
    const moodValues = moodData.map(d => d.mood);
    const moodScores = moodData.map(d => d.mood_score);
    const reasons = moodData.map(d => d.reason);

    const moodColors = {
        'Happy': '#4CAF50',
        'Sad': '#2196F3',
        'Depressed': '#9C27B0',
        'Very Happy': '#8BC34A',
        'Very Sad': '#F44336',
        'Neutral': '#9E9E9E'
    };

    // Calculate mood statistics
    const moodCounts = moodValues.reduce((acc, mood) => {
        acc[mood] = (acc[mood] || 0) + 1;
        return acc;
    }, {});

    const mostCommonMood = Object.entries(moodCounts)
        .sort((a, b) => b[1] - a[1])[0][0];

    const lastRecorded = new Date(moodData[moodData.length - 1].date)
        .toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric' 
        });

    const moodTrend = calculateMoodTrend(moodScores);

    // Update statistics
    document.getElementById('commonMood').textContent = mostCommonMood;
    document.getElementById('lastRecorded').textContent = lastRecorded;
    document.getElementById('moodTrend').textContent = moodTrend;
    
    const commonChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#fff',
                    font: {
                        family: "'Poppins', sans-serif",
                        size: 12
                    }
                }
            }
        }
    };

    const commonAxisOptions = {
        grid: {
            color: 'rgba(255, 255, 255, 0.1)',
            borderColor: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
            color: '#fff',
            font: {
                family: "'Poppins', sans-serif",
                size: 12
            }
        }
    };

    // Line Chart - Mood Over Time
    new Chart(document.getElementById("lineChart"), {
        type: "line",
        data: {
            labels: moodLabels,
            datasets: [{
                label: "Mood Score",
                data: moodScores,
                borderColor: "#00B2FF",
                backgroundColor: "rgba(0, 178, 255, 0.1)",
                fill: true,
                tension: 0.4,
                pointBackgroundColor: "#fff",
                pointBorderColor: "#00B2FF",
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        },
        options: {
            ...commonChartOptions,
            plugins: {
                ...commonChartOptions.plugins,
                title: {
                    display: true,
                    text: 'Mood Trend Over Time',
                    color: '#fff',
                    font: {
                        family: "'Poppins', sans-serif",
                        size: 16,
                        weight: 500
                    }
                }
            },
            scales: {
                y: {
                    ...commonAxisOptions,
                    beginAtZero: true,
                    ticks: {
                        ...commonAxisOptions.ticks,
                        callback: function(value) {
                            return ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive'][value + 2];
                        }
                    }
                },
                x: commonAxisOptions
            }        }
    });

    // Bar Chart - Mood Distribution
    new Chart(document.getElementById("barChart"), {
        type: "bar",
        data: {
            labels: Object.keys(moodCounts),
            datasets: [{
                label: "Frequency",
                data: Object.values(moodCounts),
                backgroundColor: Object.keys(moodCounts).map(mood => moodColors[mood]),
                borderRadius: 8
            }]
        },
        options: {
            ...commonChartOptions,
            plugins: {
                ...commonChartOptions.plugins,
                title: {
                    display: true,
                    text: 'Mood Distribution',
                    color: '#fff',
                    font: {
                        family: "'Poppins', sans-serif",
                        size: 16,
                        weight: 500
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    ...commonAxisOptions,
                    beginAtZero: true
                },
                x: commonAxisOptions
            }        }
    });

    // Pie Chart - Mood Analysis
    new Chart(document.getElementById("pieChart"), {
        type: "doughnut",
        data: {
            labels: Object.keys(moodCounts),
            datasets: [{
                data: Object.values(moodCounts),
                backgroundColor: Object.keys(moodCounts).map(mood => moodColors[mood]),
                borderWidth: 2,
                borderColor: '#1a1a1a'
            }]
        },
        options: {
            ...commonChartOptions,
            cutout: '60%',
            plugins: {
                ...commonChartOptions.plugins,
                title: {
                    display: true,
                    text: 'Mood Distribution Analysis',
                    color: '#fff',
                    font: {
                        family: "'Poppins', sans-serif",
                        size: 16,
                        weight: 500
                    },
                    padding: {
                        bottom: 20
                    }
                },
                legend: {
                    position: 'right',
                    labels: {
                        color: '#fff',
                        padding: 20,
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 12
                        },
                        generateLabels: function(chart) {
                            const data = chart.data;
                            if (data.labels.length && data.datasets.length) {
                                return data.labels.map((label, i) => ({
                                    text: `${label}: ${data.datasets[0].data[i]} times`,
                                    fillStyle: data.datasets[0].backgroundColor[i],
                                    strokeStyle: '#1a1a1a',
                                    lineWidth: 2,
                                    hidden: false
                                }));
                            }
                            return [];
                        }
                    }
                }
            }
        }
    });
}

function calculateMoodTrend(moodScores) {
    if (moodScores.length < 2) return "Not enough data";
    
    const recentScores = moodScores.slice(-5);
    const average = recentScores.reduce((a, b) => a + b, 0) / recentScores.length;
    
    if (average > 0.5) return "Improving ↑";
    if (average < -0.5) return "Declining ↓";
    return "Stable →";
}

// Initialize dashboard when document is ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        const moodDataContainer = document.getElementById('moodDataContainer');
        const moodData = JSON.parse(moodDataContainer.dataset.moodData);
        console.log('Loaded mood data:', moodData); // For debugging
        if (Array.isArray(moodData) && moodData.length > 0) {
            initializeDashboard(moodData);
        } else {
            // Handle empty data
            document.getElementById('commonMood').textContent = 'No data yet';
            document.getElementById('lastRecorded').textContent = 'No data yet';
            document.getElementById('moodTrend').textContent = 'No data yet';
        }
    } catch (error) {
        console.error('Error initializing dashboard:', error);
    }
});
