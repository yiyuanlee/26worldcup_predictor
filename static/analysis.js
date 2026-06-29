const $ = (id) => document.getElementById(id);
const params = new URLSearchParams(location.search);

let analysisData = null;

const FEATURE_KEYS = [
  "h2h_home_win_rate", "home_ppg", "away_ppg",
  "home_knockout_rate", "away_knockout_rate",
  "standings_points_diff", "standings_gd_diff",
  "home_clean_sheet_rate", "away_clean_sheet_rate",
  "odds_home_implied", "form_diff_ppg",
];

function pct(v) { return (v * 100).toFixed(1) + "%"; }

function initial(name) {
  return (name || "?").split(" ").map((w) => w[0]).join("").slice(0, 3).toUpperCase();
}

function showError(msg) {
  $("loading").classList.add("hidden");
  $("errorScreen").classList.remove("hidden");
  $("errorMsg").textContent = msg;
}

function renderInsights(insights) {
  $("insightsList").innerHTML = (insights || [])
    .map((text) => `<li>${text}</li>`).join("");
}

function render(d) {
  $("loading").classList.add("hidden");
  $("analysisMain").classList.remove("hidden");
  applyI18n();

  document.title = `${d.home_team} vs ${d.away_team} · ${t("analysis.titleSuffix")}`;

  const stage = stageLabel(d.stage || params.get("stage")) || t("stage.default");
  $("stageBadge").textContent = stage;

  $("homeName").textContent = d.home_team;
  $("awayName").textContent = d.away_team;
  $("homeInitial").textContent = initial(d.home_team);
  $("awayInitial").textContent = initial(d.away_team);

  const hp = d.team_profiles?.home;
  const ap = d.team_profiles?.away;
  $("homeProfile").textContent = hp?.group
    ? t("profile.group", { g: hp.group, pos: hp.position, pts: hp.points }) : "";
  $("awayProfile").textContent = ap?.group
    ? t("profile.group", { g: ap.group, pos: ap.position, pts: ap.points }) : "";

  const outcomeKey = d.predicted_key || "home_win";
  $("predBadge").textContent = t("analysis.predict", {
    outcome: outcomeLabel(outcomeKey),
  });

  const p = d.probabilities;
  $("homeProb").textContent = pct(p.home_win);
  $("drawProb").textContent = pct(p.draw);
  $("awayProb").textContent = pct(p.away_win);
  $("homeBar").style.width = pct(p.home_win);
  $("drawBar").style.width = pct(p.draw);
  $("awayBar").style.width = pct(p.away_win);

  renderInsights(d.insights);

  const f = d.form;
  $("formCompare").innerHTML = `
    <div class="form-col"><h4>${d.home_team}</h4>
      <div class="stat"><span>${t("form.ppg")}</span><strong>${f.home.ppg}</strong></div>
      <div class="stat"><span>${t("form.scored")}</span><strong>${f.home.scored}</strong></div>
      <div class="stat"><span>${t("form.conceded")}</span><strong>${f.home.conceded}</strong></div>
      <div class="stat"><span>${t("form.winRate")}</span><strong>${pct(f.home.win_rate)}</strong></div>
    </div>
    <div class="form-col"><h4>${d.away_team}</h4>
      <div class="stat"><span>${t("form.ppg")}</span><strong>${f.away.ppg}</strong></div>
      <div class="stat"><span>${t("form.scored")}</span><strong>${f.away.scored}</strong></div>
      <div class="stat"><span>${t("form.conceded")}</span><strong>${f.away.conceded}</strong></div>
      <div class="stat"><span>${t("form.winRate")}</span><strong>${pct(f.away.win_rate)}</strong></div>
    </div>`;

  const h = d.h2h;
  $("h2hStats").innerHTML = h.total
    ? `<p>${t("h2h.summary", { total: h.total, hw: h.home_wins, d: h.draws, aw: h.away_wins, hg: h.home_goals_avg, ag: h.away_goals_avg })}</p>`
    : `<p>${t("h2h.none")}</p>`;

  $("meetingsList").innerHTML = (d.recent_meetings || [])
    .map((m) => {
      const oc = m.outcome_key ? outcomeLabel(m.outcome_key, true) : m.outcome;
      return `<li><span>${m.date}</span> ${m.score} <em>${oc}</em></li>`;
    })
    .join("") || "<li>—</li>";

  if (d.market_implied && d.model_vs_market) {
    $("marketPanel").classList.remove("hidden");
    const m = d.market_implied;
    const e = d.model_vs_market;
    $("marketCompare").innerHTML = ["home_win", "draw", "away_win"].map((k) => {
      const edge = e[k] * 100;
      const sign = edge >= 0 ? "+" : "";
      return `<div class="mc-row"><span>${outcomeLabel(k)}</span>
        <span>${t("market.model")} ${pct(p[k])}</span><span>${t("market.market")} ${pct(m[k])}</span>
        <span class="edge ${edge >= 0 ? "pos" : "neg"}">${sign}${edge.toFixed(1)}%</span></div>`;
    }).join("");
  } else {
    $("marketPanel").classList.add("hidden");
  }

  $("featuresGrid").innerHTML = Object.entries(d.features || {})
    .filter(([k]) => FEATURE_KEYS.includes(k))
    .map(([k, v]) => `<div class="feat"><span>${featLabel(k)}</span><strong>${Number(v).toFixed(3)}</strong></div>`)
    .join("");
}

async function loadAnalysis() {
  const home = params.get("home");
  const away = params.get("away");
  if (!home || !away) {
    showError(t("error.missingParams"));
    return;
  }

  const q = withLang(new URLSearchParams({
    home, away,
    fetch_odds: $("fetchOdds").checked,
  }));
  const stage = params.get("stage");
  const date = params.get("date");
  if (stage) q.set("stage", stage);
  if (date) q.set("date", date);

  try {
    const res = await fetch(`/api/analysis?${q}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || t("error.loadFailed"));
    analysisData = data;
    render(data);
  } catch (e) {
    showError(e.message);
  }
}

initLangSwitcher();

$("fetchOdds").addEventListener("change", () => {
  $("loading").classList.remove("hidden");
  $("analysisMain").classList.add("hidden");
  loadAnalysis();
});

window.addEventListener("langchange", () => {
  applyI18n();
  if (analysisData) {
    $("loading").classList.remove("hidden");
    $("analysisMain").classList.add("hidden");
    loadAnalysis();
  }
});

loadAnalysis();
