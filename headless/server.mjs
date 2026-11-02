// Kaffora headless front: the SAME content from Liferay, rendered two ways.
//
//   node headless/server.mjs            → http://localhost:8090/  (index)
//     /ssr   server-side rendering: the HTML already contains the page
//     /csr   client-side rendering: an empty shell, the browser builds the page
//     /api/coffees  BFF: reads Liferay Objects (/o/c/coffees) server-side
//
// Env: LIFERAY_URL (default http://localhost:8080), LIFERAY_AUTH="user@liferay.com:password",
//      PORT (default 8090). Without Liferay (or without the Coffee object) it falls back to
//      headless/data/coffees.json, so the demo also works offline.
import {readFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import {dirname, extname, join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {gzipSync} from 'node:zlib';

import {CSS, META, jsonLd, renderApp} from './public/render.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const PUBLIC = join(HERE, 'public');
const PORT = Number(process.env.PORT || 8090);
const LIFERAY_URL = (process.env.LIFERAY_URL || 'http://localhost:8080').replace(/\/$/, '');
const LIFERAY_AUTH = process.env.LIFERAY_AUTH || '';
const TYPES = {'.jpg': 'image/jpeg', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8', '.png': 'image/png'};

let cache = {at: 0, value: null};

async function coffees() {
	if (cache.value && Date.now() - cache.at < 30_000) {
		return cache.value;
	}

	let value;

	try {
		const headers = {Accept: 'application/json'};

		if (LIFERAY_AUTH) {
			headers.Authorization = `Basic ${Buffer.from(LIFERAY_AUTH).toString('base64')}`;
		}

		const response = await fetch(`${LIFERAY_URL}/o/c/coffees?pageSize=20&sort=price:asc`, {headers, signal: AbortSignal.timeout(2000)});

		if (!response.ok) {
			throw new Error(`HTTP ${response.status}`);
		}

		const {items} = await response.json();

		if (!items?.length) {
			throw new Error('no entries');
		}

		value = {
			coffees: items.map(({externalReferenceCode, image, name, notes, origin, price, weight}) => ({externalReferenceCode, image, name, notes, origin, price, weight})),
			source: 'Liferay Objects · /o/c/coffees',
		};
	}
	catch (error) {
		value = {coffees: JSON.parse(await readFile(join(HERE, 'data', 'coffees.json'), 'utf8')), source: `local fallback (${error.message})`};
	}

	cache = {at: Date.now(), value};

	return value;
}

const page = ({body, head = '', origin}) => `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
${head}
<link rel="icon" href="data:,">
</head>
<body>
<div id="app">${body}</div>
</body>
</html>`;

function send(req, res, status, type, body, extra = {}) {
	let payload = Buffer.isBuffer(body) ? body : Buffer.from(body);
	const headers = {'Content-Type': type, ...extra};

	if (/text|javascript|json/.test(type) && /gzip/.test(req.headers['accept-encoding'] || '')) {
		payload = gzipSync(payload);
		headers['Content-Encoding'] = 'gzip';
		headers.Vary = 'Accept-Encoding';
	}

	res.writeHead(status, headers);
	res.end(payload);
}

createServer(async (req, res) => {
	const url = new URL(req.url, `http://${req.headers.host}`);
	const origin = `http://${req.headers.host}`;
	const path = url.pathname.replace(/\/$/, '') || '/';

	try {
		if (path === '/ssr') {
			const {coffees: list, source} = await coffees();

			return send(req, res, 200, 'text/html; charset=utf-8', page({
				body: renderApp(list, source),
				head: `<title>${META.title}</title>
<meta name="description" content="${META.description}">
<style>${CSS}</style>
<script type="application/ld+json">${JSON.stringify(jsonLd(list, origin))}</script>`,
				origin,
			}), {'Cache-Control': 'no-cache', 'X-Rendering': 'SSR'});
		}

		if (path === '/csr') {
			return send(req, res, 200, 'text/html; charset=utf-8', page({
				body: '<p class="loading">Loading…</p>',
				head: '<title>Kaffora</title>\n<script type="module" src="/app.js"></script>',
				origin,
			}), {'Cache-Control': 'no-cache', 'X-Rendering': 'CSR'});
		}

		if (path === '/api/coffees') {
			return send(req, res, 200, 'application/json; charset=utf-8', JSON.stringify(await coffees()), {'Cache-Control': 'no-cache'});
		}

		if (path === '/llms.txt') {
			const {coffees: list} = await coffees();

			return send(req, res, 200, 'text/plain; charset=utf-8',
				`# Kaffora Coffee\n\n> Single-origin specialty coffee, roasted every Monday and delivered in 48 hours.\n\n## Coffees\n\n${list.map((c) => `- [${c.name}](${origin}/ssr#${c.externalReferenceCode}): ${c.notes} 250 g from €${c.price}.`).join('\n')}\n`);
		}

		if (path === '/robots.txt') {
			return send(req, res, 200, 'text/plain; charset=utf-8', `User-agent: *\nAllow: /\n`);
		}

		if (path === '/') {
			return send(req, res, 200, 'text/html; charset=utf-8', page({
				body: `<main style="max-width:640px;margin:0 auto;padding:48px 16px"><h1>Kaffora headless front</h1>
<p>Same Liferay content, same code, two renderings:</p>
<ul><li><a href="/ssr">Server-side rendering (/ssr)</a></li><li><a href="/csr">Client-side rendering (/csr)</a></li></ul>
<p>Data: ${(await coffees()).source}</p></main>`,
				head: `<title>Kaffora headless front</title><meta name="description" content="Kaffora headless demo: SSR vs CSR."><style>${CSS}</style>`,
				origin,
			}));
		}

		const file = join(PUBLIC, path.replace(/\.\.+/g, ''));
		const type = TYPES[extname(file)];

		if (!type) {
			return send(req, res, 404, 'text/plain', 'not found');
		}

		return send(req, res, 200, type, await readFile(file), {'Cache-Control': 'public, max-age=31536000, immutable'});
	}
	catch {
		return send(req, res, 404, 'text/plain', 'not found');
	}
}).listen(PORT, () => {
	console.log(`Kaffora headless front on http://localhost:${PORT}/  (/ssr and /csr)`);
	console.log(`Liferay: ${LIFERAY_URL}${LIFERAY_AUTH ? ' (with auth)' : ' (no auth: set LIFERAY_AUTH="user:password")'}`);
});
