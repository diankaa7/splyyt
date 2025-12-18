function renderExpenseChart() {
  const ctx = document.getElementById("expense-chart").getContext("2d");

  const categoryMap = {};
  userData.expenses.forEach((e) => {
    categoryMap[e.category] = (categoryMap[e.category] || 0) + e.amount;
  });

  const labels = Object.keys(categoryMap).map((cat) => {
    const map = {
      entertainment: "🎮 Развлечения",
      style: "👟 Стиль",
      food: "☕ Кофе",
      education: "📚 Образование",
      other: "📦 Прочее",
    };
    return map[cat] || cat;
  });
  const data = Object.values(categoryMap);

  if (window.expenseChart) window.expenseChart.destroy();

  window.expenseChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [
        {
          data: data,
          backgroundColor: [
            "#FF6384",
            "#36A2EB",
            "#FFCE56",
            "#4BC0C0",
            "#9966FF",
          ],
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function (context) {
              return `${context.label}: ${context.raw} ₽`;
            },
          },
        },
      },
      animation: {
        animateRotate: true,
        duration: 1000,
        easing: "easeOutQuart",
      },
    },
  });

  // Подписи под диаграммой
  const chartCard = document.getElementById("chart-card");
  let legendHtml = '<div class="chart-legend">';
  labels.forEach((label, i) => {
    legendHtml += `<div class="legend-item"><span class="legend-color" style="background:${window.expenseChart.data.datasets[0].backgroundColor[i]}"></span> ${label}</div>`;
  });
  legendHtml += "</div>";
  chartCard.innerHTML = `<h3>📈 Твои траты</h3><canvas id="expense-chart" height="200"></canvas>${legendHtml}`;
}
