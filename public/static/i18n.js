const I18N = {
  zh: {
    "meta.homeTitle": "世界杯 2026 · 赛事中心",
    "meta.analysisTitle": "专业分析 · 世界杯预测",
    "nav.back": "← 返回赛事中心",
    "nav.odds": "拉取实时赔率",
    "hero.badge": "FIFA WORLD CUP 2026",
    "hero.title": "🏆 世界杯预测中心",
    "hero.desc": "世界杯专属模型 · 2018–2026 数据 · 选择比赛进入专业分析",
    "status.loading": "加载中...",
    "section.schedule": "32 强及后续赛程",
    "section.custom": "自定义对阵分析",
    "section.groups": "小组最终排名",
    "btn.refresh": "更新赛程",
    "btn.analysis": "进入专业分析 →",
    "pick.home": "选择主队",
    "pick.away": "选择客队",
    "match.analysis": "专业分析 →",
    "match.empty": "暂无待赛赛程",
    "group.label": "{g} 组",
    "group.pts": "{n}分",
    "footer": "World Cup Predictor · 仅供学习研究",
    "toast.pickTeams": "请选择两支球队",
    "toast.sameTeam": "请选择不同球队",
    "toast.updated": "赛程已更新",
    "toast.failed": "更新失败",
    "status.line": "{name} · {stage} · {upcoming} 场待赛 · {finished} 场已赛",
    "status.stageDefault": "32强阶段",
    "status.compName": "世界杯 2026",
    "loading.analysis": "正在生成专业分析报告...",
    "error.missingParams": "缺少比赛参数",
    "error.loadFailed": "加载失败",
    "error.sameTeam": "主客队不能相同",
    "error.backHome": "返回首页",
    "analysis.titleSuffix": "专业分析",
    "analysis.predict": "预测：{outcome}",
    "analysis.probTitle": "胜率预测",
    "analysis.modelTag": "WC 专属模型",
    "analysis.insights": "核心洞察",
    "analysis.form": "近期状态（近5场）",
    "analysis.h2h": "历史交手",
    "analysis.market": "模型 vs 市场",
    "analysis.features": "特征雷达",
    "outcome.home_win": "主胜",
    "outcome.draw": "平局",
    "outcome.away_win": "客胜",
    "outcome.home_short": "主胜",
    "outcome.draw_short": "平",
    "outcome.away_short": "客胜",
    "form.ppg": "PPG",
    "form.scored": "进球",
    "form.conceded": "失球",
    "form.winRate": "胜率",
    "h2h.summary": "共 {total} 场 · 主 {hw} 胜 {d} 平 {aw} 负 · 场均 {hg}-{ag}",
    "h2h.none": "暂无历史交手记录",
    "profile.group": "{g}组 · 第{pos} · {pts}分",
    "market.model": "模型",
    "market.market": "市场",
    "stage.group": "小组赛",
    "stage.round32": "32强",
    "stage.round16": "16强",
    "stage.quarter": "8强",
    "stage.semi": "半决赛",
    "stage.final": "决赛",
    "stage.third": "季军赛",
    "stage.default": "世界杯",
    "feat.h2h_home_win_rate": "H2H主胜率",
    "feat.home_ppg": "主队PPG",
    "feat.away_ppg": "客队PPG",
    "feat.home_knockout_rate": "主淘汰赛经验",
    "feat.away_knockout_rate": "客淘汰赛经验",
    "feat.standings_points_diff": "积分差",
    "feat.standings_gd_diff": "净胜球差",
    "feat.home_clean_sheet_rate": "主零封率",
    "feat.away_clean_sheet_rate": "客零封率",
    "feat.odds_home_implied": "市场主胜",
    "feat.form_diff_ppg": "状态差",
    "insight.favorite": "模型最看好：{name}（{pct}%）",
    "insight.h2h_home": "历史交手中 {team} 占优（{n} 场）",
    "insight.h2h_away": "历史交手中 {team} 占优（{n} 场）",
    "insight.form": "近期状态 {team} 更出色（PPG 差 {diff}）",
    "insight.edge_above": "模型认为{outcome}概率高于市场 {pct} 个百分点",
    "insight.edge_below": "模型认为{outcome}概率低于市场 {pct} 个百分点",
    "meta.bankrollTitle": "预算管理 · 世界杯预测",
    "nav.bankroll": "预算管理 →",
    "bankroll.title": "💰 投资预算管理",
    "bankroll.desc": "基于 WC 专属模型概率与 Kelly 分数法，为待赛场次生成预算分配方案",
    "bankroll.bankrollLabel": "总预算",
    "bankroll.riskLabel": "风险偏好",
    "bankroll.riskConservative": "保守",
    "bankroll.riskModerate": "稳健",
    "bankroll.riskAggressive": "进取",
    "bankroll.generate": "生成方案",
    "bankroll.loading": "正在计算预算方案...",
    "bankroll.recommendations": "推荐分配",
    "bankroll.colMatch": "对阵",
    "bankroll.colPick": "推荐",
    "bankroll.colModel": "模型概率",
    "bankroll.colEdge": "边际",
    "bankroll.colOdds": "赔率",
    "bankroll.colStake": "建议投入",
    "bankroll.colEV": "期望收益",
    "bankroll.noRecs": "当前参数下暂无满足条件的推荐场次",
    "bankroll.rulesTitle": "当前规则参数",
    "bankroll.ruleKelly": "Kelly 分数",
    "bankroll.ruleMinEdge": "最低边际",
    "bankroll.ruleMinProb": "最低模型概率",
    "bankroll.ruleMaxSingle": "单场上限",
    "bankroll.ruleMaxSlate": "单期总上限",
    "bankroll.summaryBankroll": "总预算",
    "bankroll.summaryAllocated": "已分配",
    "bankroll.summaryRemaining": "保留资金",
    "bankroll.summaryPct": "分配比例",
    "bankroll.summarySlate": "待赛场次",
    "bankroll.summaryBets": "推荐场次",
    "bankroll.oddsMarket": "赔率来源：实时市场数据",
    "bankroll.oddsEstimate": "赔率来源：模型估算（未拉取市场赔率）",
    "bankroll.disclaimer": "仅供学习研究，不构成投资建议。请理性管理资金，切勿超出承受能力。",
  },
  en: {
    "meta.homeTitle": "World Cup 2026 · Match Center",
    "meta.analysisTitle": "Analysis · World Cup Predictor",
    "nav.back": "← Back to Match Center",
    "nav.odds": "Fetch live odds",
    "hero.badge": "FIFA WORLD CUP 2026",
    "hero.title": "🏆 World Cup Predictor",
    "hero.desc": "WC-only model · 2018–2026 data · Pick a match for pro analysis",
    "status.loading": "Loading...",
    "section.schedule": "Round of 32 & Beyond",
    "section.custom": "Custom Match Analysis",
    "section.groups": "Group Standings",
    "btn.refresh": "Refresh Schedule",
    "btn.analysis": "Open Analysis →",
    "pick.home": "Select home team",
    "pick.away": "Select away team",
    "match.analysis": "Analysis →",
    "match.empty": "No upcoming fixtures",
    "group.label": "Group {g}",
    "group.pts": "{n} pts",
    "footer": "World Cup Predictor · For research only",
    "toast.pickTeams": "Please select two teams",
    "toast.sameTeam": "Please select different teams",
    "toast.updated": "Schedule updated",
    "toast.failed": "Update failed",
    "status.line": "{name} · {stage} · {upcoming} upcoming · {finished} played",
    "status.stageDefault": "Round of 32",
    "status.compName": "World Cup 2026",
    "loading.analysis": "Generating analysis report...",
    "error.missingParams": "Missing match parameters",
    "error.loadFailed": "Failed to load",
    "error.sameTeam": "Home and away teams must differ",
    "error.backHome": "Back to Home",
    "analysis.titleSuffix": "Analysis",
    "analysis.predict": "Pick: {outcome}",
    "analysis.probTitle": "Win Probability",
    "analysis.modelTag": "WC Model",
    "analysis.insights": "Key Insights",
    "analysis.form": "Recent Form (Last 5)",
    "analysis.h2h": "Head-to-Head",
    "analysis.market": "Model vs Market",
    "analysis.features": "Feature Radar",
    "outcome.home_win": "Home Win",
    "outcome.draw": "Draw",
    "outcome.away_win": "Away Win",
    "outcome.home_short": "Home",
    "outcome.draw_short": "Draw",
    "outcome.away_short": "Away",
    "form.ppg": "PPG",
    "form.scored": "Scored",
    "form.conceded": "Conceded",
    "form.winRate": "Win Rate",
    "h2h.summary": "{total} meetings · Home {hw}W {d}D {aw}L · Avg {hg}-{ag}",
    "h2h.none": "No head-to-head history",
    "profile.group": "Group {g} · #{pos} · {pts} pts",
    "market.model": "Model",
    "market.market": "Market",
    "stage.group": "Group Stage",
    "stage.round32": "Round of 32",
    "stage.round16": "Round of 16",
    "stage.quarter": "Quarter-finals",
    "stage.semi": "Semi-finals",
    "stage.final": "Final",
    "stage.third": "Third Place",
    "stage.default": "World Cup",
    "feat.h2h_home_win_rate": "H2H Home Win %",
    "feat.home_ppg": "Home PPG",
    "feat.away_ppg": "Away PPG",
    "feat.home_knockout_rate": "Home KO Exp.",
    "feat.away_knockout_rate": "Away KO Exp.",
    "feat.standings_points_diff": "Points Diff",
    "feat.standings_gd_diff": "GD Diff",
    "feat.home_clean_sheet_rate": "Home CS Rate",
    "feat.away_clean_sheet_rate": "Away CS Rate",
    "feat.odds_home_implied": "Market Home",
    "feat.form_diff_ppg": "Form Diff",
    "insight.favorite": "Model favors {name} ({pct}%)",
    "insight.h2h_home": "{team} leads H2H ({n} matches)",
    "insight.h2h_away": "{team} leads H2H ({n} matches)",
    "insight.form": "{team} in better form (PPG diff {diff})",
    "insight.edge_above": "Model {outcome} prob. {pct}pp above market",
    "insight.edge_below": "Model {outcome} prob. {pct}pp below market",
    "meta.bankrollTitle": "Bankroll · World Cup Predictor",
    "nav.bankroll": "Bankroll →",
    "bankroll.title": "💰 Bankroll Management",
    "bankroll.desc": "Kelly-based allocation from WC model probabilities for upcoming fixtures",
    "bankroll.bankrollLabel": "Total Bankroll",
    "bankroll.riskLabel": "Risk Profile",
    "bankroll.riskConservative": "Conservative",
    "bankroll.riskModerate": "Moderate",
    "bankroll.riskAggressive": "Aggressive",
    "bankroll.generate": "Generate Plan",
    "bankroll.loading": "Calculating allocation plan...",
    "bankroll.recommendations": "Recommendations",
    "bankroll.colMatch": "Match",
    "bankroll.colPick": "Pick",
    "bankroll.colModel": "Model",
    "bankroll.colEdge": "Edge",
    "bankroll.colOdds": "Odds",
    "bankroll.colStake": "Stake",
    "bankroll.colEV": "Exp. Value",
    "bankroll.noRecs": "No fixtures meet the current criteria",
    "bankroll.rulesTitle": "Active Rules",
    "bankroll.ruleKelly": "Kelly Fraction",
    "bankroll.ruleMinEdge": "Min Edge",
    "bankroll.ruleMinProb": "Min Model Prob.",
    "bankroll.ruleMaxSingle": "Max Single Bet",
    "bankroll.ruleMaxSlate": "Max Slate Exposure",
    "bankroll.summaryBankroll": "Bankroll",
    "bankroll.summaryAllocated": "Allocated",
    "bankroll.summaryRemaining": "Reserve",
    "bankroll.summaryPct": "Allocation %",
    "bankroll.summarySlate": "Upcoming",
    "bankroll.summaryBets": "Recommended",
    "bankroll.oddsMarket": "Odds: live market data",
    "bankroll.oddsEstimate": "Odds: model estimate (market odds not fetched)",
    "bankroll.disclaimer": "For research only. Not financial advice. Never risk more than you can afford to lose.",
  },
};

function getLang() {
  const urlLang = new URLSearchParams(location.search).get("lang");
  if (urlLang && I18N[urlLang]) {
    localStorage.setItem("wc_lang", urlLang);
    return urlLang;
  }
  return localStorage.getItem("wc_lang") || "zh";
}

function setLang(lang) {
  if (!I18N[lang]) return;
  localStorage.setItem("wc_lang", lang);
  document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
  applyI18n();
  syncLangButtons();
  if (location.pathname.includes("analysis") || location.pathname.includes("bankroll")) {
    const p = new URLSearchParams(location.search);
    p.set("lang", lang);
    history.replaceState(null, "", `${location.pathname}?${p}`);
  }
  window.dispatchEvent(new CustomEvent("langchange", { detail: { lang } }));
}

function t(key, vars = {}) {
  const lang = getLang();
  let str = I18N[lang][key] ?? I18N.zh[key] ?? key;
  Object.entries(vars).forEach(([k, v]) => {
    str = str.replace(new RegExp(`\\{${k}\\}`, "g"), String(v));
  });
  return str;
}

function stageLabel(stage) {
  if (!stage) return "";
  const key = `stage.${stage}`;
  return I18N[getLang()][key] ? t(key) : stage;
}

function outcomeLabel(key, short = false) {
  return t(short ? `outcome.${key}_short` : `outcome.${key}`);
}

function featLabel(key) {
  return t(`feat.${key}`);
}

function localeTag() {
  return getLang() === "zh" ? "zh-CN" : "en-US";
}

function applyI18n() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  const titleEl = document.querySelector("title[data-i18n-key]");
  if (titleEl) document.title = t(titleEl.dataset.i18nKey);
}

function syncLangButtons() {
  document.querySelectorAll("[data-lang]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === getLang());
  });
}

function initLangSwitcher() {
  document.querySelectorAll("[data-lang]").forEach((btn) => {
    btn.addEventListener("click", () => setLang(btn.dataset.lang));
  });
  document.documentElement.lang = getLang() === "zh" ? "zh-CN" : "en";
  applyI18n();
  syncLangButtons();
}

function withLang(params) {
  params.set("lang", getLang());
  return params;
}
