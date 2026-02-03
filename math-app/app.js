const starsEl = document.getElementById("stars");
const streakEl = document.getElementById("streak");
const promptEl = document.getElementById("prompt");
const visualEl = document.getElementById("visual");
const feedbackEl = document.getElementById("feedback");
const answerInput = document.getElementById("answerInput");
const modeSelect = document.getElementById("modeSelect");
const levelSelect = document.getElementById("levelSelect");
const themeSelect = document.getElementById("themeSelect");
const resetScoreBtn = document.getElementById("resetScore");
const checkBtn = document.getElementById("checkBtn");

const themes = {
  garden: {
    emoji: "🌻",
    praise: ["Blooming brilliant!", "You grew a star!", "Petal power!"],
    backgroundClass: "",
  },
  space: {
    emoji: "🚀",
    praise: ["Cosmic job!", "Star pilot!", "Galaxy high-five!"],
    backgroundClass: "theme-space",
  },
  ocean: {
    emoji: "🐠",
    praise: ["Splash-tastic!", "Ocean explorer!", "Wave of applause!"],
    backgroundClass: "theme-ocean",
  },
};

let currentAnswer = 0;
let stars = 0;
let streak = 0;

const levelLimits = {
  1: 5,
  2: 10,
  3: 20,
};

const randomNumber = (max) => Math.floor(Math.random() * max) + 1;

const setTheme = () => {
  const { backgroundClass } = themes[themeSelect.value];
  document.body.classList.remove("theme-space", "theme-ocean");
  if (backgroundClass) {
    document.body.classList.add(backgroundClass);
  }
};

const buildVisual = (count, emoji) => {
  visualEl.innerHTML = "";
  for (let i = 0; i < count; i += 1) {
    const span = document.createElement("span");
    span.textContent = emoji;
    visualEl.appendChild(span);
  }
};

const generateProblem = () => {
  const level = Number(levelSelect.value);
  const max = levelLimits[level];
  const mode = modeSelect.value;
  const theme = themes[themeSelect.value];

  let selectedMode = mode;
  if (mode === "mix") {
    const modes = ["count", "add", "sub"];
    selectedMode = modes[Math.floor(Math.random() * modes.length)];
  }

  let a = randomNumber(max);
  let b = randomNumber(max);

  if (selectedMode === "count") {
    currentAnswer = a;
    promptEl.textContent = "Count the pictures!";
    buildVisual(a, theme.emoji);
  } else if (selectedMode === "add") {
    currentAnswer = a + b;
    promptEl.textContent = `${a} + ${b} = ?`;
    buildVisual(a + b, theme.emoji);
  } else {
    if (b > a) {
      [a, b] = [b, a];
    }
    currentAnswer = a - b;
    promptEl.textContent = `${a} − ${b} = ?`;
    buildVisual(a, theme.emoji);
  }

  answerInput.value = "";
  feedbackEl.textContent = "";
  answerInput.focus();
};

const updateScore = (isCorrect) => {
  if (isCorrect) {
    stars += 1;
    streak += 1;
    const praise =
      themes[themeSelect.value].praise[
        Math.floor(Math.random() * themes[themeSelect.value].praise.length)
      ];
    feedbackEl.textContent = `${praise} ⭐`;
  } else {
    streak = 0;
    feedbackEl.textContent = "Nice try! Let’s count again together.";
  }

  starsEl.textContent = stars;
  streakEl.textContent = streak;
};

checkBtn.addEventListener("click", () => {
  const value = Number(answerInput.value);
  if (Number.isNaN(value)) {
    feedbackEl.textContent = "Type a number to check!";
    return;
  }

  const isCorrect = value === currentAnswer;
  updateScore(isCorrect);
  setTimeout(generateProblem, 900);
});

answerInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    checkBtn.click();
  }
});

modeSelect.addEventListener("change", generateProblem);
levelSelect.addEventListener("change", generateProblem);
themeSelect.addEventListener("change", () => {
  setTheme();
  generateProblem();
});

resetScoreBtn.addEventListener("click", () => {
  stars = 0;
  streak = 0;
  starsEl.textContent = stars;
  streakEl.textContent = streak;
  feedbackEl.textContent = "Score reset! Let's play.";
});

setTheme();
generateProblem();
