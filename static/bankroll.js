const $ = (id) => document.getElementById(id);

let planData = null;

function pct(v) {
  return (v * 100).toFixed(1) + "%";
}

function pctInt(v) {
  return Math.round(v * 100) + "%";
}

function moneyInt(v) {
  return Number(v).toLocaleString(localeTag(), { maximumFractionDigits: 0 });
}

function riskLabel(risk) {
  const map = {
    conservative: "bankroll.riskConservative",
    moderate: "bankroll.riskModerate",
    aggressive: "bankroll.riskAggressive",
  };
  return t(map[risk] || map.moderate);
}

function showError(msg) {
  $("errorBox").textContent = msg;
  $("errorBox").classList.remove("hidden");
  $("planContent").classList.add("hidden");
}

function renderSummary(summary) {
  const cards = [
    { label: t("bankroll.summaryBankroll"), value: moneyInt(summary.bankroll), cls: "gold" },
    { label: t("bankroll.summaryPct"), value: pctInt(summary.allocation_pct), cls: "green" },
    { label: t("bankroll.summaryAllocated"), value: moneyInt(summary.allocated), cls: "" },
    { label: t("bankroll.summaryRemaining"), value: moneyInt(summary.remaining), cls: "" },
    { label: t("bankroll.summarySlate"), value: summary.slate_matches, cls: "" },
    { label: t("bankroll.summaryBets"), value: summary.recommended_bets, cls: "accent" },
  ];
  $("summaryCards").innerHTML = cards.map((c) =>
    `<div class="summary-card ${c.cls}">
      <span class="sc-label">${c.label}</span>
      <span class="sc-value">${c.value}</span>
    </div>`
  ).join("");
}

function renderRules(rules) {
  const items = [
    { k: "bankroll.ruleKelly", v: pct(rules.kelly_fraction) },
    { k: "bankroll.ruleMinEdge", v: pct(rules.min_edge) },
    { k: "bankroll.ruleMinProb", v: pct(rules.min_model_prob) },
    { k: "bankroll.ruleMaxSingle", v: pct(rules.max_single_pct) },
    { k: "bankroll.ruleMaxSlate", v: pct(rules.max_slate_pct) },
  ];
  $("rulesGrid").innerHTML = items.map((i) =>
    `<div class="rule-item"><span>${t(i.k)}</span><strong>${i.v}</strong></div>`
  ).join("");
}

function renderTable(recs) {
  const tbody = $("recBody");
  if (!recs.length) {
    tbody.innerHTML = "";
    $("emptyRecs").classList.remove("hidden");
    $("recTable").classList.add("hidden");
    return;
  }
  $("emptyRecs").classList.add("hidden");
  $("recTable").classList.remove("hidden");
  tbody.innerHTML = recs.map((r) => {
    const match = `${teamInline(r.home_team)} <span class="vs">vs</span> ${teamInline(r.away_team)}`;
    const dt = r.date ? `<time class="rec-date">${r.date}</time>` : "";
    const st = r.stage ? `<span class="rec-stage">${stageLabel(r.stage)}</span>` : "";
    const pick = r.pick_label || outcomeLabel(r.pick);
    const edgeCls = r.edge >= 0 ? "pos" : "neg";
    return `<tr>
      <td><div class="match-cell">${st}${match}${dt}</div></td>
      <td><span class="pick-tag">${pick}</span></td>
      <td>${pct(r.model_prob)}</td>
      <td class="edge ${edgeCls}">${r.edge >= 0 ? "+" : ""}${pct(r.edge)}</td>
      <td>${r.decimal_odds.toFixed(2)}${r.has_market_odds ? "" : "*"}</td>
      <td><strong>${pctInt(r.stake_pct)}</strong><br><small>${moneyInt(r.stake)}</small></td>
      <td class="${r.expected_value >= 0 ? "pos" : "neg"}">${moneyInt(r.expected_value)}</td>
    </tr>`;
  }).join("");
}

function renderPlan(d) {
  planData = d;
  $("loading").classList.add("hidden");
  $("planContent").classList.remove("hidden");
  $("errorBox").classList.add("hidden");

  $("riskBadge").textContent = riskLabel(d.risk_profile);
  $("oddsModeHint").textContent = d.odds_hint
    || (d.odds_mode === "market"
      ? t("bankroll.oddsMarket")
      : t("bankroll.oddsEstimate"));
  $("disclaimer").textContent = d.disclaimer || t("bankroll.disclaimer");

  renderSummary(d.summary);
  renderTable(d.recommendations || []);
  renderRules(d.rules || {});
}

async function fetchPlan() {
  const bankroll = parseFloat($("bankrollInput").value) || 1000;
  const risk = $("riskSelect").value;
  const fetchOdds = $("fetchOdds").checked;

  $("loading").classList.remove("hidden");
  $("errorBox").classList.add("hidden");

  const q = new URLSearchParams({
    bankroll: String(bankroll),
    risk,
    fetch_odds: String(fetchOdds),
    lang: getLang(),
  });

  try {
    const res = await fetch(`/api/bankroll/plan?${q}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || t("error.loadFailed"));
    }
    renderPlan(await res.json());
  } catch (e) {
    $("loading").classList.add("hidden");
    showError(e.message || t("error.loadFailed"));
  }
}

function init() {
  initLangSwitcher();

  $("generateBtn").addEventListener("click", fetchPlan);
  $("fetchOdds").addEventListener("change", () => {
    if (planData) fetchPlan();
  });

  window.addEventListener("langchange", () => {
    applyI18n();
    if (planData) {
      fetchPlan();
    } else {
      $("oddsModeHint").textContent = planData?.odds_hint
        || ($("fetchOdds").checked ? t("bankroll.oddsMarket") : t("bankroll.oddsEstimate"));
    }
  });

  fetchPlan();
}

init();
