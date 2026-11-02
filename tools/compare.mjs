// Compare two Lighthouse runs beyond the score: requests, bytes, CSS/JS files, key metrics.
// Usage: node tools/compare.mjs baseline arch [mobile|desktop]
import {readFileSync, existsSync} from 'node:fs';

const [a = 'baseline', b = 'arch', ff = 'mobile'] = process.argv.slice(2);

function load(label) {
	const path = existsSync(label) ? label : `reports/${label}-${ff}.report.json`;
	if (!existsSync(path)) {
		console.error(`Not found: ${path}`);
		process.exit(1);
	}
	return JSON.parse(readFileSync(path, 'utf8'));
}

function facts(lhr) {
	const au = lhr.audits;
	const items = au['network-requests']?.details?.items ?? [];
	const byType = (t) => items.filter((i) => i.resourceType === t);
	const kib = (list) => Math.round(list.reduce((s, i) => s + (i.transferSize || 0), 0) / 1024);
	const num = (id) => au[id]?.numericValue;
	const wasted = (id) => {
		const v = au[id]?.details?.overallSavingsBytes;
		return v == null ? '-' : `${Math.round(v / 1024)} KiB`;
	};
	return {
		'Performance': Math.round((lhr.categories.performance?.score ?? 0) * 100),
		'FCP (s)': (num('first-contentful-paint') / 1000).toFixed(1),
		'LCP (s)': (num('largest-contentful-paint') / 1000).toFixed(1),
		'TBT (ms)': Math.round(num('total-blocking-time')),
		'Requests': items.length,
		'Transferred (KiB)': kib(items),
		'CSS files': byType('Stylesheet').length,
		'CSS (KiB)': kib(byType('Stylesheet')),
		'JS files': byType('Script').length,
		'JS (KiB)': kib(byType('Script')),
		'Images (KiB)': kib(byType('Image')),
		'Fonts (KiB)': kib(byType('Font')),
		'Unminified JS': wasted('unminified-javascript'),
		'Unminified CSS': wasted('unminified-css'),
	};
}

const A = facts(load(a));
const B = facts(load(b));
const pad = (s, n) => String(s).padEnd(n);
console.log(`\n${pad(`(${ff})`, 20)}${pad(a, 14)}${b}`);
for (const k of Object.keys(A)) {
	console.log(`${pad(k, 20)}${pad(A[k], 14)}${B[k]}`);
}
console.log('');
