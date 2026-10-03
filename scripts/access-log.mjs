// Turns my latest real commits into a server access log and renders it as an SVG.
// feat is a POST that creates something, fix is a PATCH, chore is a 204 nobody reads.

import { writeFileSync, mkdirSync } from "node:fs";

const USER = "Yeisonfjrd";
const LINES = 8;
const SKIP_REPOS = new Set([USER]); // the profile repo only has bot commits

const headers = {
  Accept: "application/vnd.github+json",
  "User-Agent": "access-log",
  ...(process.env.GITHUB_TOKEN && { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` }),
};

const gh = async (path) => {
  const res = await fetch(`https://api.github.com${path}`, { headers });
  if (!res.ok) throw new Error(`${res.status} ${path}`);
  return res.json();
};

const ROUTES = {
  feat: ["POST", 201],
  fix: ["PATCH", 200],
  perf: ["PATCH", 200],
  refactor: ["PUT", 200],
  docs: ["PUT", 200],
  test: ["GET", 200],
  ci: ["OPTIONS", 204],
  build: ["OPTIONS", 204],
  chore: ["OPTIONS", 204],
  revert: ["DELETE", 204],
};

// "fix(metrics): drop x" -> PATCH 200 /repo/metrics "drop x"
function parse(repo, message) {
  const m = message.match(/^(\w+)(?:\((.+?)\))?!?:\s*(.*)$/);
  const [method, status] = ROUTES[m?.[1].toLowerCase()] ?? ["POST", 200];
  const path = m?.[2] ? `/${repo}/${m[2]}` : `/${repo}`;
  return { method, status, path, subject: m ? m[3] : message };
}

function stamp(iso) {
  // Buenos Aires time, UTC-3
  const d = new Date(new Date(iso).getTime() - 3 * 3600 * 1000);
  return d.toISOString().slice(0, 16).replace("T", " ");
}

const cut = (s, n) => (s.length > n ? s.slice(0, n - 1) + "…" : s);
const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

async function collect() {
  const repos = await gh(`/users/${USER}/repos?sort=pushed&per_page=10&type=owner`);
  const commits = [];
  for (const repo of repos) {
    if (repo.fork || SKIP_REPOS.has(repo.name)) continue;
    const list = await gh(`/repos/${USER}/${repo.name}/commits?author=${USER}&per_page=${LINES}`).catch(() => []);
    for (const c of list) {
      const message = c.commit.message.split("\n")[0];
      if (message.startsWith("Merge ")) continue;
      commits.push({ repo: repo.name, message, date: c.commit.author.date });
    }
  }
  return commits.sort((a, b) => b.date.localeCompare(a.date)).slice(0, LINES);
}

const THEMES = {
  dark: { bg: "#0d1117", border: "#30363d", text: "#c9d1d9", dim: "#6e7681", prompt: "#7c3aed", ok: "#3fb950", created: "#58a6ff", empty: "#d29922", method: "#d2a8ff" },
  light: { bg: "#ffffff", border: "#d0d7de", text: "#1f2328", dim: "#8c959f", prompt: "#7c3aed", ok: "#1a7f37", created: "#0969da", empty: "#9a6700", method: "#8250df" },
};

function render(commits, t) {
  const W = 960, top = 64, step = 24;
  const H = top + commits.length * step + 30;
  const statusColor = (s) => (s === 201 ? t.created : s === 204 ? t.empty : t.ok);

  const rows = commits.map((c, i) => {
    const { method, status, path, subject } = parse(c.repo, c.message);
    const y = top + i * step;
    const delay = (0.35 + i * 0.12).toFixed(2);
    return `
  <g class="row" style="animation-delay:${delay}s">
    <text x="24" y="${y}" fill="${t.dim}">${stamp(c.date)}</text>
    <text x="172" y="${y}" fill="${t.method}">${method}</text>
    <text x="246" y="${y}" fill="${statusColor(status)}">${status}</text>
    <text x="290" y="${y}" fill="${t.text}">${esc(cut(path, 30))}</text>
    <text x="500" y="${y}" fill="${t.dim}">"${esc(cut(subject, 56))}"</text>
  </g>`;
  }).join("");

  const cursorY = top + commits.length * step + 4;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <style>
    text { font: 13px ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; white-space: pre; }
    .row { opacity: 0; animation: in .3s ease-out forwards; }
    .cursor { animation: blink 1.1s steps(1) infinite; }
    @keyframes in { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }
    @keyframes blink { 50% { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) { .row { animation: none; opacity: 1; } .cursor { animation: none; } }
  </style>
  <rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="8" fill="${t.bg}" stroke="${t.border}"/>
  <text x="24" y="32"><tspan fill="${t.prompt}">yeison@api</tspan><tspan fill="${t.dim}">:~$ </tspan><tspan fill="${t.text}">tail -n ${commits.length} /var/log/commits/access.log</tspan></text>${rows}
  <text x="24" y="${cursorY}"><tspan fill="${t.prompt}">yeison@api</tspan><tspan fill="${t.dim}">:~$ </tspan></text>
  <rect class="cursor" x="128" y="${cursorY - 12}" width="8" height="15" fill="${t.text}"/>
</svg>
`;
}

const commits = await collect();
mkdirSync("assets", { recursive: true });
for (const [name, theme] of Object.entries(THEMES)) {
  writeFileSync(`assets/access-log-${name}.svg`, render(commits, theme));
}
console.log(`access log: ${commits.length} commits`);
