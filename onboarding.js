let currentSlide = 0;
const totalSlides = 3;

function showOnboardingSlide(index) {
  document
    .querySelectorAll(".onboarding-slide")
    .forEach((s) => s.classList.remove("active"));
  document
    .querySelectorAll(".dot")
    .forEach((d) => d.classList.remove("active"));

  document
    .querySelector(`.onboarding-slide[data-index="${index}"]`)
    .classList.add("active");
  document.querySelector(`.dot[data-dot="${index}"]`).classList.add("active");
  currentSlide = index;

  const nextBtn = document.getElementById("onboarding-next");
  if (index === totalSlides - 1) {
    nextBtn.textContent = "Начать";
  } else {
    nextBtn.textContent = "Далее";
  }
}

document.getElementById("onboarding-next").addEventListener("click", () => {
  if (currentSlide < totalSlides - 1) {
    showOnboardingSlide(currentSlide + 1);
  } else {
    localStorage.setItem("splytOnboarded", "true");
    showScreen("dashboard");
    updateUI();
  }
});

document.getElementById("onboarding-skip").addEventListener("click", () => {
  localStorage.setItem("splytOnboarded", "true");
  showScreen("dashboard");
  updateUI();
});

document.querySelectorAll(".dot").forEach((dot) => {
  dot.addEventListener("click", () => {
    showOnboardingSlide(parseInt(dot.dataset.dot));
  });
});
