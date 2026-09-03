// Surf Heat Manager front end.
// Every screen is drawn from the JSON the Flask back end sends back, so
// nothing on the page ever needs to be refreshed.

let currentRound = 1;
let openHeatId = 0;

function showMessage(text) {
  document.getElementById("message").textContent = text;
}

// Adds one row to a table, with one cell for each value given.
function addRow(body, values) {
  let row = body.insertRow();
  for (let i = 0; i < values.length; i++) {
    row.insertCell().textContent = values[i];
  }
}

// This is the asynchronous function. It sends one request to the back end
// and gives back the JSON, or null if the back end refused the request.
async function api(address, method, body) {
  let settings = { method: method };
  if (body !== null) {
    settings.headers = { "Content-Type": "application/json" };
    settings.body = JSON.stringify(body);
  }

  let response = await fetch(address, settings);
  let data = await response.json();
  if (response.ok === false) {
    showMessage(data.error);
    return null;
  }
  showMessage("");
  return data;
}

function showScreen(name) {
  let screens = document.querySelectorAll(".screen");
  for (let i = 0; i < screens.length; i++) {
    if (screens[i].id === "screen-" + name) {
      screens[i].classList.add("visible");
    } else {
      screens[i].classList.remove("visible");
    }
  }

  let buttons = document.querySelectorAll("#menu button");
  for (let i = 0; i < buttons.length; i++) {
    if (buttons[i].dataset.screen === name) {
      buttons[i].classList.add("active");
    } else {
      buttons[i].classList.remove("active");
    }
  }

  if (name === "surfers") { loadSurfers(); }
  if (name === "draw") { loadHeats(currentRound); }
  if (name === "forecast") { loadForecast(); }
  if (name === "leaderboard") { loadLeaderboard(); }
  if (name === "sheet") { loadSheet(); }
}

// SC16: a viewer only sees the leaderboard, the director sees every screen.
function applyRole(role, username) {
  let parts = document.querySelectorAll(".director");
  for (let i = 0; i < parts.length; i++) {
    if (role === "director") {
      parts[i].style.display = "";
    } else {
      parts[i].style.display = "none";
    }
  }

  if (role === "director") {
    document.getElementById("loginTab").style.display = "none";
    document.getElementById("whoami").textContent = "Director: " + username;
  } else {
    document.getElementById("loginTab").style.display = "";
    document.getElementById("whoami").textContent = "Viewer (read only)";
  }
}

// ---- Surfers (SC1, SC2) --------------------------------------------------

function drawSurfers(data) {
  let body = document.querySelector("#surferTable tbody");
  body.innerHTML = "";
  for (let i = 0; i < data.surfers.length; i++) {
    let surfer = data.surfers[i];
    addRow(body, [surfer.name, surfer.skill, surfer.group_name]);
  }
  document.getElementById("surferCount").textContent =
    data.surfers.length + " of " + data.max_surfers + " surfers entered";
}

async function loadSurfers() {
  let data = await api("/api/surfers", "GET", null);
  if (data !== null) { drawSurfers(data); }
}

async function submitSurfer(event) {
  event.preventDefault();
  let data = await api("/api/surfers", "POST", {
    name: document.getElementById("surferName").value,
    skill: Number(document.getElementById("surferSkill").value),
    group_name: document.getElementById("surferGroup").value
  });
  if (data !== null) {
    drawSurfers(data);
    document.getElementById("surferForm").reset();
  }
}

// ---- Heat draw (SC3, SC4, SC5) ------------------------------------------

function fillRounds(select, rounds, chosen) {
  select.innerHTML = "";
  for (let i = 0; i < rounds.length; i++) {
    let option = document.createElement("option");
    option.value = rounds[i];
    option.textContent = "Round " + rounds[i];
    if (rounds[i] === chosen) { option.selected = true; }
    select.appendChild(option);
  }
}

function drawHeats(data) {
  currentRound = data.round_number;
  fillRounds(document.getElementById("roundSelect"), data.rounds, currentRound);

  let list = document.getElementById("heatList");
  list.innerHTML = "";
  if (data.heats.length === 0) {
    list.innerHTML = "<p class='hint'>No heats drawn yet.</p>";
    return;
  }

  for (let i = 0; i < data.heats.length; i++) {
    let heat = data.heats[i];
    let text = "<h3>Heat " + heat.heat_number + "</h3><ul>";
    for (let j = 0; j < heat.surfers.length; j++) {
      let surfer = heat.surfers[j];
      text = text + "<li>" + surfer.name + " - " + surfer.group_name +
             " (skill " + surfer.skill + ")</li>";
    }

    let panel = document.createElement("div");
    panel.className = "panel";
    panel.innerHTML = text + "</ul><p class='hint'>Click to enter scores</p>";
    panel.onclick = function () { openHeat(heat.id); };
    list.appendChild(panel);
  }
}

async function loadHeats(round) {
  let data = await api("/api/heats?round=" + round, "GET", null);
  if (data !== null) { drawHeats(data); }
}

async function clickDraw() {
  let data = await api("/api/draw", "POST", {});
  if (data !== null) { drawHeats(data); }
}

// SC9: the director chooses how many surfers advance from each heat.
async function clickAdvance() {
  let data = await api("/api/advance", "POST", {
    round_number: currentRound,
    top_n: Number(document.getElementById("topN").value)
  });
  if (data !== null) { drawHeats(data); }
}

// ---- Score entry (SC6, SC7, SC8) ----------------------------------------

function drawHeatScores(data) {
  document.getElementById("scoreTitle").textContent =
    "Round " + data.heat.round_number + ", heat " + data.heat.heat_number;

  let list = document.getElementById("scoreList");
  list.innerHTML = "";

  for (let i = 0; i < data.results.length; i++) {
    let surfer = data.results[i];

    let waves = "No waves yet";
    for (let j = 0; j < surfer.scores.length; j++) {
      let score = surfer.scores[j];
      let line = score.raw_score + " x " + score.weight + " = " + score.weighted;
      if (j === 0) { waves = line; } else { waves = waves + "  |  " + line; }
    }

    let box = document.createElement("div");
    box.className = "surfer-scores";
    box.innerHTML =
      "<h3>" + surfer.place + ". " + surfer.name + " (" + surfer.group_name + ")</h3>" +
      "<p class='waves'>" + waves + "</p>" +
      "<p class='total'>Best two total: " + surfer.total.toFixed(2) + "</p>";

    let form = document.createElement("form");
    form.innerHTML =
      "<input type='number' step='0.1' min='0' max='10' placeholder='Score 0-10' required />" +
      "<input type='number' step='0.1' min='1' max='1.3' value='1.0' required />" +
      "<button type='submit'>Add wave</button>";

    form.onsubmit = async function (event) {
      event.preventDefault();
      let inputs = form.querySelectorAll("input");
      let updated = await api("/api/scores", "POST", {
        heat_id: openHeatId,
        surfer_id: surfer.id,
        raw_score: Number(inputs[0].value),
        weight: Number(inputs[1].value)
      });
      if (updated !== null) {
        drawHeatScores(updated);
        loadLeaderboard();
      }
    };

    box.appendChild(form);
    list.appendChild(box);
  }
}

async function openHeat(heatId) {
  openHeatId = heatId;
  let data = await api("/api/heats/" + heatId, "GET", null);
  if (data !== null) {
    showScreen("scores");
    drawHeatScores(data);
  }
}

// ---- Leaderboard (SC11, SC12) -------------------------------------------

async function loadLeaderboard() {
  let data = await api("/api/leaderboard", "GET", null);
  if (data === null) { return; }

  let body = document.querySelector("#leaderboardTable tbody");
  body.innerHTML = "";
  for (let i = 0; i < data.leaderboard.length; i++) {
    let surfer = data.leaderboard[i];
    addRow(body, [surfer.place, surfer.name, surfer.group_name, surfer.skill,
                  surfer.heats_surfed, surfer.wave_count,
                  surfer.best_wave.toFixed(2), surfer.total.toFixed(2)]);
  }
}

// ---- Forecast (SC13) -----------------------------------------------------

function drawForecast(data) {
  let body = document.querySelector("#forecastTable tbody");
  body.innerHTML = "";
  for (let i = 0; i < data.slots.length; i++) {
    let slot = data.slots[i];
    addRow(body, [slot.rank, slot.slot_time, slot.wave_height,
                  slot.tide_level, slot.suitability.toFixed(3)]);
  }
}

async function loadForecast() {
  let data = await api("/api/forecast", "GET", null);
  if (data !== null) { drawForecast(data); }
}

async function submitForecast(event) {
  event.preventDefault();
  let data = await api("/api/forecast", "POST", {
    slot_time: document.getElementById("slotTime").value,
    wave_height: Number(document.getElementById("waveHeight").value),
    tide_level: Number(document.getElementById("tideLevel").value)
  });
  if (data !== null) {
    drawForecast(data);
    document.getElementById("forecastForm").reset();
  }
}

// ---- Printable heat sheet (SC14, SC15) ----------------------------------

async function loadSheet() {
  let rounds = await api("/api/heats?round=" + currentRound, "GET", null);
  if (rounds !== null) {
    fillRounds(document.getElementById("sheetRound"), rounds.rounds, currentRound);
  }

  let data = await api("/api/sheet?round=" + currentRound, "GET", null);
  if (data === null) { return; }

  let text = "<h2>Escola de Surf Peniche - Round " + data.round_number + "</h2>";
  for (let i = 0; i < data.heats.length; i++) {
    let heat = data.heats[i];
    text = text + "<div class='sheet-heat'><h3>Heat " + heat.heat_number + "</h3>" +
           "<table><thead><tr><th>Name</th><th>Group</th><th>Skill</th>" +
           "<th>Wave 1</th><th>Wave 2</th><th>Total</th></tr></thead><tbody>";
    for (let j = 0; j < heat.surfers.length; j++) {
      let surfer = heat.surfers[j];
      text = text + "<tr><td>" + surfer.name + "</td><td>" + surfer.group_name +
             "</td><td>" + surfer.skill + "</td><td></td><td></td><td></td></tr>";
    }
    text = text + "</tbody></table></div>";
  }
  document.getElementById("sheet").innerHTML = text;
}

// ---- Login (SC16) --------------------------------------------------------

async function submitLogin(event) {
  event.preventDefault();
  let data = await api("/api/login", "POST", {
    username: document.getElementById("username").value,
    password: document.getElementById("password").value
  });
  if (data !== null) {
    applyRole(data.role, data.username);
    document.getElementById("loginForm").reset();
    showScreen("leaderboard");
  }
}

async function clickLogout() {
  await api("/api/logout", "POST", {});
  applyRole("viewer", "");
  showScreen("leaderboard");
}

// ---- Setting up the buttons ---------------------------------------------

let menuButtons = document.querySelectorAll("#menu button[data-screen]");
for (let i = 0; i < menuButtons.length; i++) {
  let button = menuButtons[i];
  button.onclick = function () { showScreen(button.dataset.screen); };
}

document.getElementById("surferForm").onsubmit = submitSurfer;
document.getElementById("forecastForm").onsubmit = submitForecast;
document.getElementById("loginForm").onsubmit = submitLogin;
document.getElementById("logoutBtn").onclick = clickLogout;
document.getElementById("drawBtn").onclick = clickDraw;
document.getElementById("advanceBtn").onclick = clickAdvance;
document.getElementById("backToDraw").onclick = function () { showScreen("draw"); };
document.getElementById("printBtn").onclick = function () { window.print(); };

document.getElementById("roundSelect").onchange = function (event) {
  loadHeats(Number(event.target.value));
};

document.getElementById("sheetRound").onchange = function (event) {
  currentRound = Number(event.target.value);
  loadSheet();
};

// ---- Starting up ---------------------------------------------------------

// SC12: the leaderboard redraws every 2 seconds, with no page refresh.
setInterval(function () {
  if (document.getElementById("screen-leaderboard").classList.contains("visible")) {
    loadLeaderboard();
  }
}, 2000);

async function start() {
  let data = await api("/api/session", "GET", null);
  applyRole(data.role, data.username);
  showScreen("leaderboard");
}

start();
