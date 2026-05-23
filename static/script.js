const state = {
  memes: {},
  genre: "tech",
  lastIndex: -1,
  clicks: 0,
  streak: 0,
  lastVisual: -1,
  gifRequest: 0
};

const visuals = {
  tech: [
    ["LOL", "production is fine", "#77e4c8", "#ffd166"],
    ["</>", "works on my machine", "#7bdff2", "#f7d6e0"],
    ["CPU", "fans entered chat", "#c3f73a", "#ff9f1c"],
    ["BUG", "feature with paperwork", "#ff6b6b", "#f7fff7"]
  ],
  movies: [
    ["REC", "dramatic zoom", "#ff6b6b", "#ffd166"],
    ["PLOT", "twist loading", "#b8f2e6", "#ffa69e"],
    ["ACT 3", "budget went here", "#f6bd60", "#84a59d"],
    ["CUT", "director said no", "#f28482", "#f5cac3"]
  ],
  games: [
    ["XP+", "side quest unlocked", "#a0c4ff", "#caffbf"],
    ["BOSS", "health bar appears", "#ffadad", "#ffd6a5"],
    ["GG", "lag is strategy", "#bdb2ff", "#fdffb6"],
    ["LVL", "skill issue denied", "#9bf6ff", "#ffc6ff"]
  ],
  office: [
    ["FYI", "meeting survived", "#ffcf5a", "#45d1b3"],
    ["ETA", "blocked by reality", "#d0f4de", "#a9def9"],
    ["SYNC", "calendar attacked", "#e4c1f9", "#fcf6bd"],
    ["PDF", "final_v9_real", "#f7a072", "#eddea4"]
  ],
  school: [
    ["A+?", "confidence chapter", "#bde0fe", "#ffc8dd"],
    ["DUE", "started spiritually", "#caffbf", "#fdffb6"],
    ["PRES", "body present", "#ffd6a5", "#a0c4ff"],
    ["QUIZ", "panic speedrun", "#ffadad", "#bdb2ff"]
  ],
  sports: [
    ["VAR", "still blaming ref", "#90be6d", "#f9c74f"],
    ["20-0", "playlist believes", "#43aa8b", "#f3722c"],
    ["GOAL", "tactic: shout", "#4d96ff", "#ffd93d"],
    ["REP", "one more tomorrow", "#06d6a0", "#ef476f"]
  ],
  food: [
    ["NOM", "research meal", "#ffbe0b", "#fb5607"],
    ["ETA", "5 mins forever", "#f77f00", "#fcbf49"],
    ["SALT", "taste is chaos", "#eae2b7", "#fcbf49"],
    ["DIET", "after this bite", "#80ed99", "#ffd166"]
  ],
  travel: [
    ["BAG", "zero chargers", "#8ecae6", "#ffb703"],
    ["GATE", "sprint later", "#219ebc", "#fb8500"],
    ["MAP", "route questionable", "#b7e4c7", "#ffafcc"],
    ["WIFI", "emotionally offline", "#a2d2ff", "#ffc8dd"]
  ],
  family: [
    ["IT", "touched one setting", "#ffd166", "#06d6a0"],
    ["PIC", "43 negotiations", "#f4a261", "#e9c46a"],
    ["Q?", "job explanation failed", "#cdb4db", "#ffc8dd"],
    ["NEWS", "everyone has opinion", "#ffafcc", "#bde0fe"]
  ],
  random: [
    ["TAB", "life audit opened", "#f15bb5", "#00bbf9"],
    ["0", "inbox folklore", "#fee440", "#00f5d4"],
    ["73%", "quick question stuck", "#9b5de5", "#f15bb5"],
    ["REST", "chores optional", "#00f5d4", "#fee440"]
  ]
};

const genreSelect = document.querySelector("#genre");
const memeButton = document.querySelector("#memeButton");
const shuffleButton = document.querySelector("#shuffle");
const genreTag = document.querySelector("#genreTag");
const memeTitle = document.querySelector("#memeTitle");
const memeText = document.querySelector("#memeText");
const memeFace = document.querySelector("#memeFace");
const memeBadge = document.querySelector("#memeBadge");
const gifMedia = document.querySelector("#gifMedia");
const score = document.querySelector("#score");
const combo = document.querySelector("#combo");
const streak = document.querySelector("#streak");
const status = document.querySelector("#status");

function applyVisual(index) {
  const list = visuals[state.genre] || visuals.random;
  let visualIndex = index % list.length;
  if (list.length > 1 && visualIndex === state.lastVisual) {
    visualIndex = (visualIndex + 1) % list.length;
  }

  state.lastVisual = visualIndex;
  const [face, badge, colorA, colorB] = list[visualIndex];
  memeFace.textContent = face;
  memeBadge.textContent = badge;
  memeButton.style.setProperty("--meme-a", colorA);
  memeButton.style.setProperty("--meme-b", colorB);
}

async function loadGif(title, text) {
  const requestId = ++state.gifRequest;
  memeButton.classList.remove("has-gif");
  gifMedia.removeAttribute("src");
  memeBadge.textContent = "searching gif";

  const params = new URLSearchParams({
    genre: state.genre,
    title,
    text,
    reshuffle: String(state.gifRequest)
  });

  try {
    const response = await fetch(`/api/gif?${params}`, { cache: "no-store" });
    const data = await response.json();
    if (requestId !== state.gifRequest) return;

    if (data.ok && data.url) {
      gifMedia.src = data.url;
      memeButton.classList.add("has-gif");
      memeBadge.textContent = "gif from web";
      return;
    }
  } catch (error) {
    if (requestId !== state.gifRequest) return;
  }

  memeButton.classList.remove("has-gif");
  memeBadge.textContent = "local fallback";
}

function pickMeme() {
  const list = state.memes[state.genre] || [];
  if (!list.length) return;

  let index = Math.floor(Math.random() * list.length);
  if (list.length > 1) {
    while (index === state.lastIndex) {
      index = Math.floor(Math.random() * list.length);
    }
  }

  state.lastIndex = index;
  const [title, text] = list[index];
  genreTag.textContent = state.genre.toUpperCase();
  memeTitle.textContent = title;
  memeText.textContent = text;
  applyVisual(index);
  status.textContent = `${list.length} memes in ${state.genre}`;
  loadGif(title, text);
}

function registerClick() {
  state.clicks += 1;
  state.streak += 1;
  score.textContent = state.clicks;
  combo.textContent = state.streak;
  streak.textContent = `Current streak: ${state.streak}`;
  memeButton.classList.remove("pop");
  requestAnimationFrame(() => memeButton.classList.add("pop"));
  pickMeme();
}

async function boot() {
  const response = await fetch("/api/genres", { cache: "no-store" });
  const data = await response.json();
  state.memes = data.memes;
  pickMeme();
}

genreSelect.addEventListener("change", (event) => {
  state.genre = event.target.value;
  state.lastIndex = -1;
  state.lastVisual = -1;
  state.streak = 0;
  combo.textContent = "0";
  streak.textContent = "Current streak: 0";
  pickMeme();
});

memeButton.addEventListener("click", registerClick);
shuffleButton.addEventListener("click", registerClick);

boot().catch(() => {
  memeTitle.textContent = "Server hiccup";
  memeText.textContent = "The meme machine tripped before the punchline.";
});
