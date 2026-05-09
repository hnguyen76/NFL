const dashboard = window.NFL_BETTING_DASHBOARD;

const state = {
  market: "Under",
  patternMode: "positive",
  teamMetric: "ats",
  teamSearch: "",
};

const markets = ["Home ATS", "Away ATS", "Favorite ATS", "Underdog ATS", "Over", "Under"];

const $ = (selector) => document.querySelector(selector);

function formatPct(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return "--";
  return `${(value * 100).toFixed(digits)}%`;
}

function formatUnits(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "--";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(1)}u`;
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function outcomeClass(value) {
  return value >= 0 ? "positive" : "negative";
}

function metricSummary(row) {
  return `${row.wins}-${row.losses}-${row.pushes} | ${formatNumber(row.bets)} bets`;
}

function renderMeta() {
  const meta = dashboard.meta;
  $("#metaStats").innerHTML = [
    ["Games", formatNumber(meta.game_count)],
    ["Seasons", `${meta.season_min}-${meta.season_max}`],
    ["Latest game", meta.latest_game.game_id.replaceAll("_", " ")],
  ]
    .map(
      ([label, value]) => `
        <div class="meta-card">
          <span>${label}</span>
          <strong>${value}</strong>
        </div>
      `,
    )
    .join("");

  $("#sourceLine").textContent = `${meta.source} | Generated ${new Date(
    meta.generated_at,
  ).toLocaleDateString("en-US")}`;
}

function renderKpis() {
  const overall = Object.fromEntries(dashboard.overall.map((row) => [row.market, row]));
  const topPattern = dashboard.patterns[0];
  const bestMarket = dashboard.overall
    .slice()
    .sort((a, b) => (b.roi ?? -99) - (a.roi ?? -99))[0];

  const cards = [
    {
      label: "Best baseline market",
      value: bestMarket.market,
      foot: `${formatPct(bestMarket.roi)} ROI at -110 | ${metricSummary(bestMarket)}`,
      color: "#00766d",
    },
    {
      label: "Top historical signal",
      value: formatPct(topPattern.roi),
      foot: `${topPattern.name} | ${metricSummary(topPattern)}`,
      color: "#c28a24",
    },
    {
      label: "Underdog ATS",
      value: formatPct(overall["Underdog ATS"].win_pct),
      foot: `${formatPct(overall["Underdog ATS"].roi)} ROI | ${metricSummary(
        overall["Underdog ATS"],
      )}`,
      color: "#13805f",
    },
    {
      label: "Over market",
      value: formatPct(overall.Over.win_pct),
      foot: `${formatPct(overall.Over.roi)} ROI | ${metricSummary(overall.Over)}`,
      color: "#b23a32",
    },
  ];

  $("#kpiGrid").innerHTML = cards
    .map(
      (card) => `
        <article class="metric-card" style="--accent:${card.color}">
          <span class="metric-label">${escapeHtml(card.label)}</span>
          <strong class="metric-value">${escapeHtml(card.value)}</strong>
          <p class="metric-foot">${escapeHtml(card.foot)}</p>
        </article>
      `,
    )
    .join("");
}

function renderOverallBars() {
  const rows = dashboard.overall;
  const maxAbs = Math.max(...rows.map((row) => Math.abs(row.roi || 0)), 0.01);
  $("#overallBars").innerHTML = rows
    .map((row) => {
      const width = Math.min(50, (Math.abs(row.roi || 0) / maxAbs) * 50);
      const isNegative = (row.roi || 0) < 0;
      return `
        <div class="bar-row">
          <span class="bar-label">${row.market}</span>
          <span class="bar-track" aria-label="${row.market} ROI ${formatPct(row.roi)}">
            <span
              class="bar-fill ${isNegative ? "negative" : ""}"
              style="width:${width}%; --bar-color:${isNegative ? "#b23a32" : "#00766d"}"
            ></span>
          </span>
          <span class="bar-value ${outcomeClass(row.roi || 0)}">${formatPct(row.roi)}</span>
        </div>
      `;
    })
    .join("");
}

function renderMarketToggle() {
  $("#marketToggle").innerHTML = markets
    .map(
      (market) => `
        <button type="button" class="${market === state.market ? "active" : ""}" data-market="${market}">
          ${market.replace(" ATS", "")}
        </button>
      `,
    )
    .join("");

  $("#marketToggle").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-market]");
    if (!button) return;
    state.market = button.dataset.market;
    renderMarketToggle();
    renderSeasonChart();
    renderWeekHeat();
  });
}

function renderSeasonChart() {
  const rows = dashboard.season_market[state.market].filter((row) => row.bets > 0);
  const values = rows.map((row) => row.roi || 0);
  const min = Math.min(-0.1, ...values, 0);
  const max = Math.max(0.1, ...values, 0);
  const width = 820;
  const height = 300;
  const margin = { top: 22, right: 18, bottom: 36, left: 48 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;
  const x = (index) => margin.left + (index / Math.max(rows.length - 1, 1)) * innerWidth;
  const y = (value) => margin.top + ((max - value) / (max - min)) * innerHeight;
  const points = rows.map((row, index) => `${x(index)},${y(row.roi || 0)}`).join(" ");
  const zeroY = y(0);
  const labels = rows.filter((_, index) => index % 5 === 0 || index === rows.length - 1);

  $("#seasonChart").innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${state.market} season ROI trend">
      <line x1="${margin.left}" x2="${width - margin.right}" y1="${zeroY}" y2="${zeroY}" stroke="#bfb6a7" stroke-width="1" />
      <line x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height - margin.bottom}" stroke="#d8d0c3" />
      <polyline points="${points}" fill="none" stroke="#00766d" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" />
      ${rows
        .map(
          (row, index) => `
            <circle cx="${x(index)}" cy="${y(row.roi || 0)}" r="4" fill="${
              (row.roi || 0) >= 0 ? "#00766d" : "#b23a32"
            }">
              <title>${row.group}: ${formatPct(row.roi)} ROI</title>
            </circle>
          `,
        )
        .join("")}
      <text x="8" y="${y(max) + 4}" class="axis-label">${formatPct(max)}</text>
      <text x="8" y="${zeroY + 4}" class="axis-label">0%</text>
      <text x="8" y="${y(min) + 4}" class="axis-label">${formatPct(min)}</text>
      ${labels
        .map(
          (row, index) => {
            const rowIndex = rows.indexOf(row);
            return `<text x="${x(rowIndex)}" y="${height - 10}" text-anchor="${index === 0 ? "start" : "middle"}" class="axis-label">${row.group}</text>`;
          },
        )
        .join("")}
    </svg>
  `;
}

function heatColor(roi) {
  const value = Math.max(-0.08, Math.min(0.08, roi || 0));
  const alpha = 0.18 + Math.min(Math.abs(value) / 0.08, 1) * 0.58;
  if (value >= 0) return `rgba(0, 118, 109, ${alpha})`;
  return `rgba(178, 58, 50, ${alpha})`;
}

function renderWeekHeat() {
  const rows = dashboard.week_market[state.market].filter((row) => Number(row.group) <= 18);
  $("#weekHeat").innerHTML = rows
    .map(
      (row) => `
        <div class="heat-cell" style="--heat-color:${heatColor(row.roi)}">
          <strong>Week ${row.group}</strong>
          <span class="${outcomeClass(row.roi || 0)}">${formatPct(row.roi)}</span>
          <small>${formatNumber(row.bets)} bets</small>
        </div>
      `,
    )
    .join("");
}

function renderCompactTable(selector, rows, labelKey) {
  $(selector).innerHTML = rows
    .map(
      (row) => `
        <div class="compact-row">
          <span class="table-label">${escapeHtml(row[labelKey])}</span>
          <strong class="${outcomeClass(row.roi || 0)}">${formatPct(row.roi)}</strong>
          <span>${formatNumber(row.bets)}</span>
        </div>
      `,
    )
    .join("");
}

function renderDiagnostics() {
  renderCompactTable("#spreadTable", dashboard.spread_buckets, "bucket");
  renderCompactTable("#totalTable", dashboard.total_buckets, "bucket");
  renderCompactTable("#weatherTable", dashboard.weather_buckets, "bucket");
}

function renderYearFocus() {
  $("#yearGrid").innerHTML = dashboard.year_focus
    .map((year) => {
      const signal = year.signals[0];
      const trap = year.traps[0];
      const marketRows = year.markets
        .map(
          (row) => `
            <div class="year-market-row">
              <span>${escapeHtml(row.market)}</span>
              <strong class="${outcomeClass(row.roi || 0)}">${formatPct(row.roi)}</strong>
            </div>
          `,
        )
        .join("");
      return `
        <article class="year-card">
          <div class="year-head">
            <span class="year-number">${year.season}</span>
            <span>${formatNumber(year.games)} REG games</span>
          </div>
          <div class="year-split">
            <span>
              <small>Best market</small>
              <strong class="${outcomeClass(year.best_market.roi || 0)}">${escapeHtml(
                year.best_market.market,
              )} ${formatPct(year.best_market.roi)}</strong>
            </span>
            <span>
              <small>Worst market</small>
              <strong class="${outcomeClass(year.worst_market.roi || 0)}">${escapeHtml(
                year.worst_market.market,
              )} ${formatPct(year.worst_market.roi)}</strong>
            </span>
          </div>
          <div class="year-market-table">${marketRows}</div>
          <div class="year-angle">
            <span class="table-label">Signal</span>
            <strong>${signal ? escapeHtml(signal.name) : "No positive sample"}</strong>
            <small>${signal ? `${formatPct(signal.roi)} ROI | ${formatNumber(signal.bets)} bets` : "Pass broad filters"}</small>
          </div>
          <div class="year-angle warning">
            <span class="table-label">Trap</span>
            <strong>${trap ? escapeHtml(trap.name) : "No major trap"}</strong>
            <small>${trap ? `${formatPct(trap.roi)} ROI | ${formatNumber(trap.bets)} bets` : "Still require price discipline"}</small>
          </div>
          <ul class="year-advice">
            ${year.advice.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
          </ul>
        </article>
      `;
    })
    .join("");
}

function renderPatternTable() {
  const rows =
    state.patternMode === "positive"
      ? dashboard.patterns.filter((row) => (row.roi || 0) > 0).slice(0, 8)
      : dashboard.patterns
          .slice()
          .sort((a, b) => (a.roi || 0) - (b.roi || 0))
          .slice(0, 8);

  const body = rows
    .map(
      (row) => `
        <div class="pattern-row">
          <span class="pattern-name">
            <strong>${escapeHtml(row.name)}</strong>
            <span>${escapeHtml(row.thesis)}</span>
          </span>
          <span>${row.market}</span>
          <strong>${formatNumber(row.bets)}</strong>
          <span>${formatPct(row.win_pct)}</span>
          <strong class="${outcomeClass(row.roi || 0)}">${formatPct(row.roi)}</strong>
          <span>${escapeHtml(row.confidence)} | ${formatUnits(row.profit_units)}</span>
        </div>
      `,
    )
    .join("");

  $("#patternTable").innerHTML = `
    <div class="pattern-row header">
      <span>Angle</span>
      <span>Market</span>
      <span>Bets</span>
      <span>Win</span>
      <span>ROI</span>
      <span>Confidence</span>
    </div>
    ${body}
  `;
}

function wirePatternToggle() {
  $("#patternToggle").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-mode]");
    if (!button) return;
    state.patternMode = button.dataset.mode;
    document
      .querySelectorAll("#patternToggle button")
      .forEach((item) => item.classList.toggle("active", item.dataset.mode === state.patternMode));
    renderPatternTable();
  });
}

function renderTeams() {
  const metric = state.teamMetric;
  const query = state.teamSearch.trim().toLowerCase();
  const rows = dashboard.teams
    .filter((team) => {
      if (!query) return true;
      return [team.team, team.name, team.short, team.division]
        .join(" ")
        .toLowerCase()
        .includes(query);
    })
    .sort((a, b) => ((b[metric] || {}).roi ?? -99) - ((a[metric] || {}).roi ?? -99))
    .slice(0, query ? 35 : 16);

  $("#teamGrid").innerHTML = rows
    .map((team) => {
      const selected = team[metric] || team.ats;
      const logo = team.logo
        ? `<img src="${escapeHtml(team.logo)}" alt="" loading="lazy" onerror="this.replaceWith(document.createTextNode('${team.team}'))" />`
        : `<span>${team.team}</span>`;
      return `
        <article class="team-card" style="--accent:${escapeHtml(team.color)}">
          <div class="team-head">
            <span class="team-logo">${logo}</span>
            <span class="team-title">
              <strong>${escapeHtml(team.name)}</strong>
              <span>${escapeHtml(team.division || team.conference || team.team)}</span>
            </span>
          </div>
          <div class="team-stats">
            <span class="team-stat">
              <span>${metric.replaceAll("_", " ")}</span>
              <strong class="${outcomeClass(selected.roi || 0)}">${formatPct(selected.roi)}</strong>
            </span>
            <span class="team-stat">
              <span>Win rate</span>
              <strong>${formatPct(selected.win_pct)}</strong>
            </span>
            <span class="team-stat">
              <span>Bets</span>
              <strong>${formatNumber(selected.bets)}</strong>
            </span>
            <span class="team-stat">
              <span>Over ROI</span>
              <strong class="${outcomeClass(team.over.roi || 0)}">${formatPct(team.over.roi)}</strong>
            </span>
          </div>
        </article>
      `;
    })
    .join("");
}

function wireTeamControls() {
  $("#teamSearch").addEventListener("input", (event) => {
    state.teamSearch = event.target.value;
    renderTeams();
  });
  $("#teamMetric").addEventListener("change", (event) => {
    state.teamMetric = event.target.value;
    renderTeams();
  });
}

function init() {
  renderMeta();
  renderKpis();
  renderOverallBars();
  renderMarketToggle();
  renderSeasonChart();
  renderWeekHeat();
  renderDiagnostics();
  renderYearFocus();
  renderPatternTable();
  wirePatternToggle();
  wireTeamControls();
  renderTeams();
}

init();
