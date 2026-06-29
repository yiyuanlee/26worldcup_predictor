const $ = (id) => document.getElementById(id);

let homeData = null;

function toast(msg) {
  const el = $("toast");
  el.textContent = msg;
  el.className = "toast";
  setTimeout(() => el.classList.add("hidden"), 3000);
}

function goAnalysis(home, away, stage = "", date = "") {
  const p = withLang(new URLSearchParams({ home, away }));
  if (stage) p.set("stage", stage);
  if (date) p.set("date", date);
  window.location.href = `/analysis?${p}`;
}

function renderMatches(matches) {
  const grid = $("matchGrid");
  const playable = (matches || []).filter((m) => m.home_team !== "TBD");
  if (!playable.length) {
    grid.innerHTML = `<p class="empty">${t("match.empty")}</p>`;
    return;
  }
  grid.innerHTML = playable.map((m) => {
    const dt = m.date
      ? new Date(m.date).toLocaleString(localeTag(), { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
      : "";
    const st = stageLabel(m.stage);
    return `<article class="match-card" data-home="${m.home_team}" data-away="${m.away_team}" data-stage="${m.stage || ""}" data-date="${m.date || ""}">
      <span class="match-stage">${st}</span>
      <div class="match-teams">${m.home_team}<span>vs</span>${m.away_team}</div>
      <time>${dt}</time>
      <span class="match-cta">${t("match.analysis")}</span>
    </article>`;
  }).join("");
}

function renderGroups(groups) {
  $("groupsGrid").innerHTML = Object.keys(groups || {}).sort().map((g) => {
    const rows = groups[g].map((team) =>
      `<div class="gr-row"><span>${team.position}. ${team.team}</span><span>${t("group.pts", { n: team.points })}</span></div>`
    ).join("");
    return `<div class="gr-card"><h4>${t("group.label", { g })}</h4>${rows}</div>`;
  }).join("");
}

function renderTeams(teams) {
  const opts = teams.map((team) => `<option value="${team.name}">${team.name}</option>`).join("");
  $("homePick").innerHTML = `<option value="">${t("pick.home")}</option>${opts}`;
  $("awayPick").innerHTML = `<option value="">${t("pick.away")}</option>${opts}`;
}

function renderStatus(s) {
  $("statusBar").textContent = t("status.line", {
    name: t("status.compName"),
    stage: t("status.stageDefault"),
    upcoming: s.upcoming_matches || 0,
    finished: s.finished_matches || s.history_matches || 0,
  });
}

function renderAll() {
  if (!homeData) return;
  applyI18n();
  renderStatus(homeData.status || {});
  renderMatches(homeData.upcoming);
  renderGroups(homeData.groups);
  renderTeams(homeData.teams || []);
}

async function load() {
  homeData = await fetch("/api/home").then((r) => r.json());
  renderAll();
}

async function init() {
  initLangSwitcher();

  $("matchGrid").addEventListener("click", (e) => {
    const card = e.target.closest(".match-card");
    if (!card) return;
    goAnalysis(card.dataset.home, card.dataset.away, card.dataset.stage, card.dataset.date);
  });

  $("goAnalysis").addEventListener("click", () => {
    const h = $("homePick").value;
    const a = $("awayPick").value;
    if (!h || !a) return toast(t("toast.pickTeams"));
    if (h === a) return toast(t("toast.sameTeam"));
    goAnalysis(h, a);
  });

  $("refreshBtn").addEventListener("click", async () => {
    $("refreshBtn").disabled = true;
    try {
      await fetch("/api/refresh-schedule", { method: "POST" });
      toast(t("toast.updated"));
      await load();
    } catch {
      toast(t("toast.failed"));
    } finally {
      $("refreshBtn").disabled = false;
    }
  });

  window.addEventListener("langchange", renderAll);
  await load();
}

init();
