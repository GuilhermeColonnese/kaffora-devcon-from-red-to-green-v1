// Print a compact terminal summary of one Lighthouse JSON report.
//   node tools/summary.mjs reports/baseline-mobile.report.json
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

const color = (s) => (s === null ? '\x1b[90m' : s >= 0.9 ? '\x1b[32m' : s >= 0.5 ? '\x1b[33m' : '\x1b[31m');
const reset = '\x1b[0m';

export function summarize(report) {
	const lines = [`\nLighthouse ${report.lighthouseVersion} · ${report.configSettings.formFactor} · ${report.finalDisplayedUrl}\n`];

	for (const [id, category] of Object.entries(report.categories)) {
		const scored = category.auditRefs.filter((ref) => ref.weight > 0);
		const failing = scored.filter((ref) => {
			const audit = report.audits[ref.id];

			return audit.score !== null && audit.score < 0.9 && audit.scoreDisplayMode !== 'notApplicable';
		});
		let value = category.score === null ? '  –' : String(Math.round(category.score * 100)).padStart(3);

		if (id === 'agentic-browsing') {
			const applicable = scored.filter((ref) => report.audits[ref.id].scoreDisplayMode !== 'notApplicable');

			value = `${applicable.length - failing.length}/${applicable.length}`.padStart(3);
		}

		lines.push(`${color(category.score)}${value}${reset}  ${category.title.padEnd(18)} ${failing.map((ref) => ref.id).join(', ')}`);
	}

	const metric = (id) => report.audits[id]?.displayValue ?? '–';

	lines.push(`\n     LCP ${metric('largest-contentful-paint')} · TBT ${metric('total-blocking-time')} · CLS ${metric('cumulative-layout-shift')} · FCP ${metric('first-contentful-paint')}\n`);

	return lines.join('\n');
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	console.log(summarize(JSON.parse(readFileSync(process.argv[2], 'utf8'))));
}
