Telegram.WebApp.ready();
Telegram.WebApp.expand();
Telegram.WebApp.setHeaderColor("#f9f9f9");
Telegram.WebApp.setBackgroundColor("#f9f9f9");

let userData = JSON.parse(localStorage.getItem("splytData")) || {
  income: [],
  expenses: [],
  goal: null,
  xp: 0,
  achievements: [],
  avatar: "🙂",
};

const LEVELS = [
  { name: "Новичок", xp: 0 },
  { name: "Хранитель", xp: 100 },
  { name: "Стратег", xp: 300 },
  { name: "Финансовый Ниндзя", xp: 600 },
];

function getCurrentLevel(xp) {
  let level = LEVELS[0];
  for (let l of LEVELS) {
    if (xp >= l.xp) level = l;
  }
  return level;
}

function updateUI() {
  const incomeTotal = userData.income.reduce((sum, i) => sum + i.amount, 0);
  const expenseTotal = userData.expenses.reduce((sum, e) => sum + e.amount, 0);
  const balance = incomeTotal - expenseTotal;

  document.getElementById("total-income").textContent = `${incomeTotal} ₽`;
  document.getElementById("total-expense").textContent = `${expenseTotal} ₽`;
  document.getElementById("balance").textContent = `${balance} ₽`;

  document.getElementById("current-avatar").textContent = userData.avatar;
  document.getElementById("profile-avatar").textContent = userData.avatar;

  const level = getCurrentLevel(userData.xp);
  document.getElementById("level-badge").textContent = level.name;
  document.getElementById("profile-level").textContent = level.name;
  document.getElementById("profile-xp").textContent = userData.xp;

  // Цель
  const goalCard = document.getElementById("goal-card");
  if (userData.goal) {
    const progress = Math.min(100, (balance / userData.goal.amount) * 100);
    document.getElementById("goal-title").textContent = userData.goal.name;
    document.getElementById("goal-progress").style.width = `${progress}%`;
    document.getElementById("goal-percent").textContent = `${Math.round(
      progress
    )}%`;
    goalCard.style.display = "block";
  } else {
    goalCard.style.display = "none";
  }

  // Диаграмма
  if (userData.expenses.length > 0) {
    document.getElementById("chart-card").style.display = "block";
    renderExpenseChart();
  } else {
    document.getElementById("chart-card").style.display = "none";
  }

  // Ачивки в профиле
  const achList = document.getElementById("achievements-list");
  if (userData.achievements.length === 0) {
    achList.innerHTML =
      "<p>Пока нет ачивок. Начни добавлять доходы и цели!</p>";
  } else {
    let html = "";
    userData.achievements.forEach((id) => {
      const ach = ACHIEVEMENTS[id];
      if (ach) {
        html += `<div class="achievement-item"><div class="achievement-title">${ach.name}</div><div>${ach.desc}</div></div>`;
      }
    });
    achList.innerHTML = html;
  }
}

function showScreen(screenId) {
  document
    .querySelectorAll(".screen")
    .forEach((s) => s.classList.add("hidden"));
  document.getElementById(`${screenId}-screen`).classList.remove("hidden");
}

// Инициализация экранов
document.getElementById("start-btn").addEventListener("click", () => {
  showScreen("dashboard");
  updateUI();
});

// Доход
document
  .getElementById("add-income-btn")
  .addEventListener("click", () => showScreen("add-income"));
document
  .getElementById("back-from-income")
  .addEventListener("click", () => showScreen("dashboard"));
document.getElementById("save-income-btn").addEventListener("click", () => {
  const source = document.getElementById("income-source").value;
  const amount = parseFloat(document.getElementById("income-amount").value);
  if (source && amount > 0) {
    userData.income.push({ source, amount, date: new Date().toISOString() });
    localStorage.setItem("splytData", JSON.stringify(userData));
    checkAchievements();
    updateUI();
    showScreen("dashboard");
  }
});

// Трата
document
  .getElementById("add-expense-btn")
  .addEventListener("click", () => showScreen("add-expense"));
document
  .getElementById("back-from-expense")
  .addEventListener("click", () => showScreen("dashboard"));
document.getElementById("save-expense-btn").addEventListener("click", () => {
  const desc = document.getElementById("expense-desc").value;
  const amount = parseFloat(document.getElementById("expense-amount").value);
  const category = document.getElementById("expense-category").value;
  if (desc && amount > 0) {
    userData.expenses.push({
      desc,
      amount,
      category,
      date: new Date().toISOString(),
    });
    localStorage.setItem("splytData", JSON.stringify(userData));
    checkAchievements();
    updateUI();
    showScreen("dashboard");
  }
});

// Цель
document
  .getElementById("set-goal-btn")
  .addEventListener("click", () => showScreen("set-goal"));
document
  .getElementById("back-from-goal")
  .addEventListener("click", () => showScreen("dashboard"));
document.getElementById("save-goal-btn").addEventListener("click", () => {
  const name = document.getElementById("goal-name").value;
  const amount = parseFloat(document.getElementById("goal-amount").value);
  if (name && amount > 0) {
    userData.goal = { name, amount };
    localStorage.setItem("splytData", JSON.stringify(userData));
    checkAchievements();
    updateUI();
    showScreen("dashboard");
  }
});

// Обучение
document
  .getElementById("learn-btn")
  .addEventListener("click", () => showScreen("learn"));
document
  .getElementById("back-from-learn")
  .addEventListener("click", () => showScreen("dashboard"));

// Профиль
document.getElementById("profile-btn").addEventListener("click", () => {
  updateUI(); // чтобы обновить ачивки
  showScreen("profile");
});
document
  .getElementById("back-from-profile")
  .addEventListener("click", () => showScreen("dashboard"));

// Магазин
document
  .getElementById("shop-btn")
  .addEventListener("click", () => showScreen("shop"));
document
  .getElementById("back-from-shop")
  .addEventListener("click", () => showScreen("dashboard"));

// Покупки (Stars)
document.querySelectorAll(".buy-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const item = btn.dataset.item;
    const price = parseInt(btn.dataset.price);
    // В реальном проекте: Telegram.WebApp.openInvoice()
    Telegram.WebApp.showPopup({
      title: "✨ Покупка",
      message: `Покупка за ${price} ⭐ будет доступна после подключения Stars.`,
      buttons: [{ type: "close" }],
    });
    // Пример разблокировки (для демо — бесплатно):
    if (item === "avatar-sunglasses") userData.avatar = "🕶️";
    if (item === "avatar-rocket") userData.avatar = "🚀";
    localStorage.setItem("splytData", JSON.stringify(userData));
    updateUI();
  });
});

// Запуск
if (!localStorage.getItem("splytOnboarded")) {
  showScreen("onboarding");
  showOnboardingSlide(0);
} else if (!localStorage.getItem("splytData")) {
  showScreen("welcome");
} else {
  showScreen("dashboard");
  updateUI();
}
