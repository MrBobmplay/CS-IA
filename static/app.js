// Surf Heat Manager front end. Every screen is drawn from JSON returned by
// the Flask back end, so nothing on the page needs a refresh.

let role = "viewer";
let currentRound = 1;
let openHeatId = null;

function show(message) {
  document.getElementById("message").textContent = message || "";
}

// Sends one request and returns the JSON, or null if the server refused.
async function api(url, method, body) {
  const options = { method: method || "GET" };
  if (body) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(body);
  }
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    show(data.error);
    return null;
  }
  show("");
  return data;
}

function showScreen(name) {
  document.querySelectorAll(".screen").forEach(function (screen) {
    screen.classList.toggle("visible", screen.id === "screen-" + name);
  });
  document.querySelectorAll("#menu button").forEach(function (button) {
    button.classList.toggle("active", button.dataset.screen === name);
  });
  if (name === "surfers") loadSurfers();
  if (name === "draw") loadHeats(currentRound);
  if (name === "forecast") loadForecast();
  if (name === "leaderboard") loadLeaderboard();
  if (name === "sheet") loadSheet();
}

// SC16: viewers only see the leaderboard, the director sees every screen.
function applyRole(newRole, username) {
  role = newRole;
  document.querySelectorAll(".director").forEach(function (element) {
    element.style.display = role === "director" ? "" : "none";
  });
  document.getElementById("loginTab").style.display = role === "director" ? "none" : "";
  document.getElementById("whoami").textContent =
    role === "director" ? "Director: " + username : "Viewer (read only)";
}

// ---- Surfers (SC1, SC2) --------------------------------------------------

function drawSurfers(data) {
  const body = document.querySelector("#surferTable tbody");
  body.innerHTML = "";
  data.surfers.forEach(function (surfer) {
    const row = body.insertRow();
    row.insertCell().textContent = surfer.name;
    row.insertCell().textContent = surfer.skill;
    row.insertCell().textContent = surfer.group_name;
  });
  document.getElementById("surferCount").textContent =
    data.surfers.length + " of " + data.max_surfers + " surfers entered";
}

async function loadSurfers() {
  const data = await api("/api/surfers");
  if (data) drawSurfers(data);
}

document.getElementById("surferForm").onsubmit = async function (event) {
  event.preventDefault();
  const data = await api("/api/surfers", "POST", {
    name: document.getElementById("surferName").value,
    skill: Number(document.getElementById("surferSkill").value),
    group_name: document.getElementById("surferGroup").value
  });
  if (data) {
    drawSurfers(data);
    document.getElementById("surferForm").reset();
  }
};

// ---- Heat draw (SC3, SC4, SC5) ------------------------------------------

function fillRounds(select, rounds, selected) {
  select.innerHTML = "";
  rounds.forEach(function (number) {
    const option = document.createElement("option");
    option.value = number;
    option.textContent = "Round " + number;
    option.selected = number === selected;
    select.appendChild(option);
  });
}

function drawHeats(data) {
  currentRound = data.round_number;
  fillRounds(document.getElementById("roundSelect"), data.rounds, currentRound);

  const list = document.getElementById("heatList");
  list.innerHTML = "";
  data.heats.forEach(function (heat) {
    const panel = document.createElement("div");
    panel.className = "panel";
    let html = "<h3>Heat " + heat.heat_number + "</h3><ul>";
    heat.surfers.forEach(function (surfer) {
      html += "<li>" + surfer.name + " - " + surfer.group_name +
              " (skill " + surfer.skill + ")</li>";
    });
    panel.innerHTML = html + "</ul><p class='hint'>Click to enter scores</p>";
    panel.onclick = function () { openHeat(heat.id); };
    list.appendChild(panel);
  });
  if (data.heats.length === 0) list.innerHTML = "<p class='hint'>No heats drawn yet.</p>";
}

async function loadHeats(round) {
  const data = await api("/api/heats?round=" + round);
  if (data) drawHeats(data);
}

document.getElementById("drawBtn").onclick = async function () {
  const data = await api("/api/draw", "POST", {});
  if (data) drawHeats(data);
};

document.getElementById("roundSelect").onchange = function (event) {
  loadHeats(Number(event.target.value));
};

// SC9: the director picks how many surfers advance from each heat.
document.getElementById("advanceBtn").onclick = async function () {
  const data = await api("/api/advance", "POST", {
    round_number: currentRound,
    top_n: Number(document.getElementById("topN").value)
  });
  if (data) drawHeats(data);
};

// ---- Score entry (SC6, SC7, SC8) ----------------------------------------

function drawHeatScores(data) {
  document.getElementById("scoreTitle").textContent =
    "Round " + data.heat.round_number + ", heat " + data.heat.heat_number;

  const list = document.getElementById("scoreList");
  list.innerHTML = "";
  data.results.forEach(function (surfer) {
    const box = document.createElement("div");
    box.className = "surfer-scores";

    const waves = surfer.scores.map(function (score) {
      return score.raw_score + " x " + score.weight + " = " + score.weighted;
    }).join("  |  ") || "No waves yet";

    box.innerHTML =
      "<h3>" + surfer.place + ". " + surfer.name + " (" + surfer.group_name + ")</h3>" +
      "<p class='waves'>" + waves + "</p>" +
      "<p class='total'>Best two total: " + surfer.total.toFixed(2) + "</p>";

    const form = document.createElement("form");
    form.innerHTML =
      "<input type='number' step='0.1' min='0' max='10' placeholder='Score 0-10' required />" +
      "<input type='number' step='0.1' min='1' max='1.3' value='1.0' required />" +
      "<button type='submit'>Add wave</button>";
    form.onsubmit = async function (event) {
      event.preventDefault();
      const inputs = form.querySelectorAll("input");
      const updated = await api("/api/scores", "POST", {
        heat_id: openHeatId,
        surfer_id: surfer.id,
        raw_score: Number(inputs[0].value),
        weight: Number(inputs[1].value)
      });
      if (updated) {
        drawHeatScores(updated);
        loadLeaderboard();
      }
    };

    box.appendChild(form);
    list.appendChild(box);
  });
}

async function openHeat(heatId) {
  openHeatId = heatId;
  const data = await api("/api/heats/" + heatId);
  if (data) {
    showScreen("scores");
    drawHeatScores(data);
  }
}

document.getElementById("backToDraw").onclick = function () { showScreen("draw"); };

// ---- Leaderboard (SC11, SC12) -------------------------------------------

async function loadLeaderboard() {
  const data = await api("/api/leaderboard");
  if (!data) return;
  const body = document.querySelector("#leaderboardTable tbody");
  body.innerHTML = "";
  data.leaderboard.forEach(function (surfer) {
    const row = body.insertRow();
    row.insertCell().textContent = surfer.place;
    row.insertCell().textContent = surfer.name;
    row.insertCell().textContent = surfer.group_name;
    row.insertCell().textContent = surfer.skill;
    row.insertCell().textContent = surfer.heats_surfed;
    row.insertCell().textContent = surfer.wave_count;
    row.insertCell().textContent = surfer.best_wave.toFixed(2);
    row.insertCell().textContent = surfer.total.toFixed(2);
  });
}

// ---- Forecast (SC13) -----------------------------------------------------

function drawForecast(data) {
  const body = document.querySelector("#forecastTable tbody");
  body.innerHTML = "";
  data.slots.forEach(function (slot) {
    const row = body.insertRow();
    row.insertCell().textContent = slot.rank;
    row.insertCell().textContent = slot.slot_time;
    row.insertCell().textContent = slot.wave_height;
    row.insertCell().textContent = slot.tide_level;
    row.insertCell().textContent = slot.suitability.toFixed(3);
  });
}

async function loadForecast() {
  const data = await api("/api/forecast");
  if (data) drawForecast(data);
}

document.getElementById("forecastForm").onsubmit = async function (event) {
  event.preventDefault();
  const data = await api("/api/forecast", "POST", {
    slot_time: document.getElementById("slotTime").value,
    wave_height: Number(document.getElementById("waveHeight").value),
    tide_level: Number(document.getElementById("tideLevel").value)
  });
  if (data) {
    drawForecast(data);
    document.getElementById("forecastForm").reset();
  }
};

// ---- Printable heat sheet (SC14, SC15) ----------------------------------

async function loadSheet() {
  const rounds = await api("/api/heats?round=" + currentRound);
  if (rounds) fillRounds(document.getElementById("sheetRound"), rounds.rounds, currentRound);

  const data = await api("/api/sheet?round=" + currentRound);
  if (!data) return;

  let html = "<h2>Escola de Surf Peniche - Round " + data.round_number + "</h2>";
  data.heats.forEach(function (heat) {
    html += "<div class='sheet-heat'><h3>Heat " + heat.heat_number + "</h3>" +
            "<table><thead><tr><th>Name</th><th>Group</th><th>Skill</th>" +
            "<th>Wave 1</th><th>Wave 2</th><th>Total</th></tr></thead><tbody>";
    heat.surfers.forEach(function (surfer) {
      html += "<tr><td>" + surfer.name + "</td><td>" + surfer.group_name +
              "</td><td>" + surfer.skill + "</td><td></td><td></td><td></td></tr>";
    });
    html += "</tbody></table></div>";
  });
  document.getElementById("sheet").innerHTML = html;
}

document.getElementById("sheetRound").onchange = function (event) {
  currentRound = Number(event.target.value);
  loadSheet();
};

document.getElementById("printBtn").onclick = function () { window.print(); };

// ---- Login (SC16) --------------------------------------------------------

document.getElementById("loginForm").onsubmit = async function (event) {
  event.preventDefault();
  const data = await api("/api/login", "POST", {
    username: document.getElementById("username").value,
    password: document.getElementById("password").value
  });
  if (data) {
    applyRole(data.role, data.username);
    document.getElementById("loginForm").reset();
    showScreen("leaderboard");
  }
};

document.getElementById("logoutBtn").onclick = async function () {
  await api("/api/logout", "POST", {});
  applyRole("viewer", "");
  showScreen("leaderboard");
};

// ---- Start ---------------------------------------------------------------

document.querySelectorAll("#menu button[data-screen]").forEach(function (button) {
  button.onclick = function () { showScreen(button.dataset.screen); };
});

// SC12: the leaderboard redraws every 2 seconds without a page refresh.
setInterval(function () {
  if (document.getElementById("screen-leaderboard").classList.contains("visible")) {
    loadLeaderboard();
  }
}, 2000);

api("/api/session").then(function (data) {
  applyRole(data.role, data.username);
  showScreen("leaderboard");
});
