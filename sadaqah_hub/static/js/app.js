document.addEventListener('DOMContentLoaded', () => {
  const chartCanvas = document.getElementById('givingChart');
  if (chartCanvas && window.Chart) {
    const labels = JSON.parse(chartCanvas.dataset.labels || '[]');
    const values = JSON.parse(chartCanvas.dataset.values || '[]');
    new Chart(chartCanvas, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Monthly giving',
          data: values,
          borderColor: '#0f766e',
          fill: false,
          tension: 0.2,
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }
});
