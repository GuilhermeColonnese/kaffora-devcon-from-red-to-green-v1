// Run Lighthouse 13.5 (pinned) on mobile and/or desktop and save HTML + JSON reports.
// Works the same on macOS, Windows and Linux.
//
//   node tools/lh.mjs <label> <url> [mobile|desktop|both] [--open]
//
//   node tools/lh.mjs baseline http://kaffora.localhost:8080/            → both form factors
//   node tools/lh.mjs final    http://kaffora.localhost:8080/ mobile --open
//
// Output: reports/<label>-mobile.report.{html,json} and reports/<label>-desktop.report.{html,json}
// First time only: run `npm install` in the kit folder.
//
// Environment variables (optional):
//   CHROME_PATH      path to Chrome/Chromium if it isn't found automatically
//   LH_CHROME_FLAGS  extra Chrome flags, e.g. "--headless=new --no-sandbox" (Linux containers)
import {mkdirSync, writeFileSync} from 'node:fs';
import {dirname, join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

import * as chromeLauncher from 'chrome-launcher';
import lighthouse from 'lighthouse';
import desktopConfig from 'lighthouse/core/config/desktop-config.js';

import {openFile} from './open.mjs';
import {summarize} from './summary.mjs';

const args = process.argv.slice(2).filter((arg) => !arg.startsWith('--'));
const shouldOpen = process.argv.includes('--open');
const [label, url, mode = 'both'] = args;

if (!label || !url || !['mobile', 'desktop', 'both'].includes(mode)) {
	console.error('usage: node tools/lh.mjs <label> <url> [mobile|desktop|both] [--open]');
	process.exit(1);
}

const reportsDir = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'reports');

mkdirSync(reportsDir, {recursive: true});

const CATEGORIES = ['performance', 'accessibility', 'best-practices', 'seo', 'agentic-browsing'];
const formFactors = mode === 'both' ? ['mobile', 'desktop'] : [mode];
const chromeFlags = (process.env.LH_CHROME_FLAGS || '--headless=new').split(/\s+/).filter(Boolean);

const chrome = await chromeLauncher.launch({chromeFlags});

try {
	for (const formFactor of formFactors) {
		console.log(`\nRunning Lighthouse (${formFactor}) on ${url} ...`);

		const result = await lighthouse(
			url,
			{logLevel: 'error', onlyCategories: CATEGORIES, output: ['html', 'json'], port: chrome.port},
			formFactor === 'desktop' ? desktopConfig : undefined
		);

		const base = join(reportsDir, `${label}-${formFactor}.report`);

		writeFileSync(`${base}.html`, result.report[0]);
		writeFileSync(`${base}.json`, result.report[1]);

		console.log(summarize(result.lhr));
		console.log(`Saved ${base}.html`);

		if (shouldOpen) {
			openFile(`${base}.html`);
		}
	}
}
finally {
	await chrome.kill();
}
