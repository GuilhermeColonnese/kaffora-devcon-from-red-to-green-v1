// Build a stage-friendly scoreboard from two or three Lighthouse runs.
// Works the same on macOS, Windows and Linux.
//
//   node tools/scoreboard.mjs baseline content final [--open]
//   node tools/scoreboard.mjs baseline final [--open]
//       → uses reports/<label>-mobile.report.json and reports/<label>-desktop.report.json
//         (whichever exist for every label) and writes one scoreboard with a Mobile / Desktop switch
//   node tools/scoreboard.mjs <a.json> <b.json> [<c.json>] [--open]
//       → explicit report files
//
// Writes reports/scoreboard.html (self-contained, no network).
import {existsSync, readFileSync, writeFileSync} from 'node:fs';
import {basename, dirname, join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

import {openFile} from './open.mjs';

const args = process.argv.slice(2).filter((arg) => !arg.startsWith('--'));
const shouldOpen = process.argv.includes('--open');

if (args.length < 2 || args.length > 3) {
	console.error('usage: node tools/scoreboard.mjs <label> <label> [<label>] [--open]');
	console.error('   or: node tools/scoreboard.mjs <a.json> <b.json> [<c.json>] [--open]');
	process.exit(1);
}

const reportsDir = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'reports');
const load = (path) => JSON.parse(readFileSync(path, 'utf8'));
const title = (label) => label.charAt(0).toUpperCase() + label.slice(1);
const sets = [];

if (args[0].endsWith('.json')) {
	const runs = args.map((path) => ({label: title(basename(path).split('-')[0]), report: load(path)}));

	sets.push({id: runs[0].report.configSettings.formFactor, runs});
}
else {
	for (const formFactor of ['mobile', 'desktop']) {
		const paths = args.map((label) => join(reportsDir, `${label}-${formFactor}.report.json`));

		if (paths.every((path) => existsSync(path))) {
			sets.push({id: formFactor, runs: paths.map((path, i) => ({label: title(args[i]), report: load(path)}))});
		}
	}
}

if (!sets.length) {
	console.error(`No matching reports found in ${reportsDir}. Run node tools/lh.mjs first.`);
	process.exit(1);
}

const ORDER = ['performance', 'accessibility', 'best-practices', 'seo', 'agentic-browsing'];

function failing(report, categoryId) {
	const category = report.categories[categoryId];

	if (!category) {
		return [];
	}

	return category.auditRefs
		.filter((ref) => ref.weight > 0)
		.map((ref) => report.audits[ref.id])
		.filter((audit) => audit.score !== null && audit.score < 0.9 && audit.scoreDisplayMode !== 'notApplicable');
}

function agenticRatio(report) {
	const category = report.categories['agentic-browsing'];

	if (!category) {
		return null;
	}

	const applicable = category.auditRefs
		.filter((ref) => ref.weight > 0)
		.filter((ref) => report.audits[ref.id].scoreDisplayMode !== 'notApplicable');

	return {pass: applicable.length - failing(report, 'agentic-browsing').length, total: applicable.length};
}

const tone = (score) => (score === null || score === undefined ? 'na' : score >= 0.9 ? 'good' : score >= 0.5 ? 'avg' : 'bad');

function gauge(score, label) {
	const value = score === null || score === undefined ? 0 : score;
	const circumference = 2 * Math.PI * 42;

	return `<svg class="gauge ${tone(score)}" viewBox="0 0 100 100" role="img" aria-label="${label}">
		<circle cx="50" cy="50" r="42" class="track"/>
		<circle cx="50" cy="50" r="42" class="arc" stroke-dasharray="${circumference * value} ${circumference}" transform="rotate(-90 50 50)"/>
		<text x="50" y="50" dominant-baseline="central" text-anchor="middle">${label}</text>
	</svg>`;
}

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})[c]);

function panel(runs) {
	const reports = runs.map((run) => run.report);
	const before = reports[0];
	const after = reports[reports.length - 1];

	const rows = ORDER.filter((id) => reports.some((r) => r.categories[id])).map((id) => {
		const labels = reports.map((r) => {
			if (id === 'agentic-browsing') {
				const ratio = agenticRatio(r);

				return ratio ? `${ratio.pass}/${ratio.total}` : '–';
			}

			const c = r.categories[id];

			return !c || c.score === null ? '–' : Math.round(c.score * 100);
		});
		let delta = null;

		if (id === 'agentic-browsing') {
			const br = agenticRatio(before);
			const ar = agenticRatio(after);

			delta = br && ar ? ar.pass - br.pass : null;
		}
		else if (typeof labels[0] === 'number' && typeof labels[labels.length - 1] === 'number') {
			delta = labels[labels.length - 1] - labels[0];
		}

		const gauges = reports.map((r, k) => gauge(r.categories[id]?.score, labels[k]))
			.join('<span class="arrow" aria-hidden="true">→</span>');
		const fixedIds = failing(before, id).map((audit) => audit.id);
		const stillIds = new Set(failing(after, id).map((audit) => audit.id));
		const fixed = fixedIds.filter((auditId) => !stillIds.has(auditId));
		const chips = [
			...fixed.map((auditId) => `<li class="chip fixed" title="${esc(before.audits[auditId].title)}">✓ ${auditId}</li>`),
			...[...stillIds].map((auditId) => `<li class="chip open" title="${esc(after.audits[auditId].title)}">• ${auditId}</li>`),
		].join('');

		return `<section class="row">
			<h2>${esc((after.categories[id] || before.categories[id]).title)}</h2>
			<div class="pair n${reports.length}">${gauges}</div>
			<p class="steps">${runs.map((run) => esc(run.label)).join(' → ')}</p>
			<p class="delta ${delta > 0 ? 'up' : ''}">${delta === null ? '' : (delta > 0 ? '+' : '') + delta}</p>
			<ul class="chips">${chips}</ul>
		</section>`;
	});

	const METRICS = [
		['largest-contentful-paint', 'LCP'],
		['total-blocking-time', 'TBT'],
		['cumulative-layout-shift', 'CLS'],
		['first-contentful-paint', 'FCP'],
		['speed-index', 'Speed Index'],
	];

	const metricRows = METRICS.map(([id, label]) => `<tr><th scope="row">${label}</th>${reports.map((r) =>
		`<td class="${tone(r.audits[id]?.score)}">${esc(r.audits[id]?.displayValue ?? '–')}</td>`).join('')}</tr>`).join('');

	const bytes = (report) => Math.round((report.audits['total-byte-weight']?.numericValue ?? 0) / 1024);

	return `<p class="meta">Lighthouse ${esc(after.lighthouseVersion)} · ${esc(after.configSettings.formFactor)} · ${esc(after.finalDisplayedUrl)}<br>${runs.map((run) => `${esc(run.label)}: ${esc(new Date(run.report.fetchTime).toLocaleString())}`).join(' · ')}</p>
	<div class="grid">${rows.join('')}</div>
	<div class="lower">
		<div class="panel">
			<h2>Core metrics</h2>
			<table><thead><tr><th></th>${runs.map((run) => `<th>${esc(run.label)}</th>`).join('')}</tr></thead><tbody>${metricRows}</tbody></table>
		</div>
		<div class="panel">
			<h2>Page weight</h2>
			<p class="big">${reports.map((r) => `${bytes(r).toLocaleString()} KiB`).join(' → ')}</p>
			<p class="muted">${Math.max(0, Math.round((1 - bytes(after) / Math.max(1, bytes(before))) * 100))}% lighter, with native Liferay DXP configuration only.</p>
		</div>
	</div>`;
}

const LABELS = {desktop: 'Desktop', mobile: 'Mobile'};
const tabs = sets.length > 1
	? `<div class="tabs" role="tablist">${sets.map((p, i) => `<button role="tab" aria-selected="${i === 0}" data-tab="${p.id}">${LABELS[p.id] || p.id}</button>`).join('')}</div>`
	: '';
const panels = sets.map((p, i) => `<section class="tabpanel" data-panel="${p.id}"${i === 0 ? '' : ' hidden'}>${panel(p.runs)}</section>`).join('');

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>From Red to Green · Scoreboard</title>
<style>
	:root { --bg:#0e1117; --panel:#161b24; --ink:#e8ecf2; --muted:#93a0b4; --good:#0cce6b; --avg:#ffa400; --bad:#ff4e42; --line:#263041; }
	* { box-sizing: border-box; }
	body { background: var(--bg); color: var(--ink); font: 16px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 32px 16px 48px; }
	main { margin: 0 auto; max-width: 1180px; }
	header { align-items: end; display: flex; flex-wrap: wrap; gap: 8px 24px; justify-content: space-between; margin-bottom: 28px; }
	h1 { font-size: clamp(28px, 4vw, 44px); letter-spacing: -0.02em; margin: 0; }
	h1 .r { color: var(--bad); } h1 .g { color: var(--good); }
	.meta { color: var(--muted); font-size: 14px; margin: 0; }
	.grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); }
	.row { background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 18px 16px 16px; }
	.row h2 { font-size: 15px; font-weight: 600; letter-spacing: .02em; margin: 0 0 12px; text-align: center; }
	.pair { align-items: center; display: flex; gap: 6px; justify-content: center; }
	.arrow { color: var(--muted); font-size: 22px; }
	.gauge { height: 86px; width: 86px; }
	.pair.n3 .gauge { height: 64px; width: 64px; }
	.pair.n3 .gauge text { font-size: 26px; }
	.steps { color: var(--muted); font-size: 12px; letter-spacing: .04em; margin: 6px 0 0; text-align: center; text-transform: uppercase; }
	.big { overflow-wrap: anywhere; }
	.gauge .track { fill: none; stroke: var(--line); stroke-width: 8; }
	.gauge .arc { fill: none; stroke-linecap: round; stroke-width: 8; }
	.gauge text { fill: var(--ink); font-size: 24px; font-weight: 700; }
	.gauge.good .arc { stroke: var(--good); } .gauge.good text { fill: var(--good); }
	.gauge.avg .arc { stroke: var(--avg); } .gauge.avg text { fill: var(--avg); }
	.gauge.bad .arc { stroke: var(--bad); } .gauge.bad text { fill: var(--bad); }
	.delta { color: var(--muted); font-size: 20px; font-weight: 700; margin: 6px 0 10px; min-height: 1.4em; text-align: center; }
	.delta.up { color: var(--good); }
	.chips { display: flex; flex-wrap: wrap; gap: 6px; list-style: none; margin: 0; padding: 0; }
	.chip { border-radius: 999px; font: 12px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace; padding: 4px 8px; }
	.chip.fixed { background: rgba(12, 206, 107, .12); color: #7ff0b3; }
	.chip.open { background: rgba(255, 78, 66, .12); color: #ffb0aa; }
	.lower { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); margin-top: 16px; }
	.panel { background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 18px; }
	.panel h2 { font-size: 15px; margin: 0 0 10px; }
	table { border-collapse: collapse; width: 100%; }
	th, td { border-bottom: 1px solid var(--line); padding: 8px 6px; text-align: left; }
	thead th { color: var(--muted); font-size: 13px; font-weight: 600; }
	td.good { color: var(--good); } td.avg { color: var(--avg); } td.bad { color: var(--bad); }
	.big { font-size: clamp(22px, 3.2vw, 36px); font-weight: 800; letter-spacing: -0.02em; margin: 4px 0; }
	.muted { color: var(--muted); margin: 0; }
	.tabs { background: var(--panel); border: 1px solid var(--line); border-radius: 999px; display: inline-flex; gap: 4px; padding: 4px; }
	.tabs button { background: transparent; border: 0; border-radius: 999px; color: var(--muted); cursor: pointer; font: 600 15px/1 system-ui, sans-serif; padding: 10px 18px; }
	.tabs button[aria-selected="true"] { background: #e500bd; color: #fff; }
	.tabpanel > .meta { margin: -12px 0 20px; }
</style>
</head>
<body>
<main>
	<header>
		<h1>From <span class="r">Red</span> to <span class="g">Green</span></h1>
		${tabs}
	</header>
	${panels}
</main>
<script>
	document.querySelectorAll('[data-tab]').forEach((button) => button.addEventListener('click', () => {
		document.querySelectorAll('[data-tab]').forEach((b) => b.setAttribute('aria-selected', String(b === button)));
		document.querySelectorAll('[data-panel]').forEach((p) => { p.hidden = p.dataset.panel !== button.dataset.tab; });
	}));
</script>
</body>
</html>
`;

const out = join(reportsDir, 'scoreboard.html');

writeFileSync(out, html);
console.log(`Scoreboard written to ${out}`);

if (shouldOpen) {
	openFile(out);
}
