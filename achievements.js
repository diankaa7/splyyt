const ACHIEVEMENTS = {
  "first-income": { name: "Первый доход", desc: "Получил первый доход!" },
  "first-expense": { name: "Первая трата", desc: "Сделал первую покупку" },
  "week-no-spend": { name: "Минималист", desc: "Неделя без трат!" },
  "first-goal": {
    name: "Целеустремлённый",
    desc: "Поставил первую финансовую цель!",
  },
}
function unlockAchievement(id) {
  if (!userData.achievements.includes(id)) {
    userData.achievements.push(id);
    userData.xp += 30;
    const ach = ACHIEVEMENTS[id];
    if (ach) {
      Telegram.WebApp.showPopup({
        title: "🏆 Новая ачивка!",
        message: `${ach.name}\n${ach.desc}`,
        buttons: [{ type: "close" }],
      });
    }
    localStorage.setItem("splytData", JSON.stringify(userData));
    updateUI();
  }
}

function checkAchievements() {
  const now = new Date();

  // First income
  if (userData.income.length > 0) unlockAchievement("first-income");

  // First expense
  if (userData.expenses.length > 0) unlockAchievement("first-expense");

  // First goal
  if (userData.goal) unlockAchievement("first-goal");

  // Week without spending
  if (userData.expenses.length > 0) {
    const lastExpense = new Date(
      userData.expenses[userData.expenses.length - 1].date
    );
    const daysSince = (now - lastExpense) / (1000 * 60 * 60 * 24);
    if (daysSince >= 7) unlockAchievement("week-no-spend");
  }
}

