/** 球队名 → ISO 3166-1 alpha-2（用于 flagcdn 国旗图） */
const TEAM_ISO = {
  Algeria: "dz",
  Argentina: "ar",
  Australia: "au",
  Austria: "at",
  Belgium: "be",
  "Bosnia and Herzegovina": "ba",
  Brazil: "br",
  Canada: "ca",
  "Cape Verde": "cv",
  Colombia: "co",
  Croatia: "hr",
  Curacao: "cw",
  "Czech Republic": "cz",
  Ecuador: "ec",
  Egypt: "eg",
  England: "gb-eng",
  France: "fr",
  Germany: "de",
  Ghana: "gh",
  Haiti: "ht",
  Iran: "ir",
  Iraq: "iq",
  "Ivory Coast": "ci",
  Japan: "jp",
  Jordan: "jo",
  Mexico: "mx",
  Morocco: "ma",
  Netherlands: "nl",
  "New Zealand": "nz",
  Norway: "no",
  Panama: "pa",
  Paraguay: "py",
  Portugal: "pt",
  Qatar: "qa",
  "RD Congo": "cd",
  "Saudi Arabia": "sa",
  Scotland: "gb-sct",
  Senegal: "sn",
  "South Africa": "za",
  "South Korea": "kr",
  Spain: "es",
  Sweden: "se",
  Switzerland: "ch",
  Tunisia: "tn",
  Turkey: "tr",
  USA: "us",
  Uruguay: "uy",
  Uzbekistan: "uz",
};

function teamIso(name) {
  if (!name || name === "TBD") return null;
  return TEAM_ISO[name] || null;
}

function teamFlagUrl(name, width = 40) {
  const iso = teamIso(name);
  if (!iso) return null;
  return `https://flagcdn.com/w${width}/${iso}.png`;
}

function teamFlagEmoji(name) {
  const iso = teamIso(name);
  if (!iso) return "⚽";
  const code = iso.split("-")[0].toUpperCase();
  if (code.length !== 2) return "⚽";
  return code.replace(/./g, (c) => String.fromCodePoint(127397 + c.charCodeAt(0)));
}

function teamFlagHtml(name, size = "md") {
  const url = teamFlagUrl(name, size === "lg" ? 80 : size === "sm" ? 20 : 40);
  const cls = `team-flag team-flag-${size}`;
  if (!url) {
    return `<span class="${cls} team-flag-fallback" title="${name || ""}">${teamFlagEmoji(name)}</span>`;
  }
  const w = size === "lg" ? 64 : size === "sm" ? 20 : 40;
  const h = size === "lg" ? 48 : size === "sm" ? 15 : 30;
  return `<img class="${cls}" src="${url}" alt="${name}" width="${w}" height="${h}" loading="lazy">`;
}

function teamInline(name) {
  return `<span class="team-inline">${teamFlagHtml(name, "sm")}<span>${name}</span></span>`;
}
