// Serves the replica: RED on :8101, GREEN on :8102, fake third-party origin on :8103.
import {createServer} from 'node:http';
import {readFile, stat} from 'node:fs/promises';
import {extname, join} from 'node:path';
import {gzipSync} from 'node:zlib';

const ROOT = new URL('./sites/', import.meta.url).pathname;
const TYPES = {
	'.css': 'text/css; charset=utf-8', '.html': 'text/html; charset=utf-8', '.jpg': 'image/jpeg',
	'.js': 'text/javascript; charset=utf-8', '.png': 'image/png', '.ttf': 'font/ttf',
	'.txt': 'text/plain; charset=utf-8', '.xml': 'application/xml',
};

function serve(dir, mode, port) {
	createServer(async (req, res) => {
		let path = decodeURIComponent(new URL(req.url, 'http://x').pathname);
		if (path === '/' || path === '/home') path = '/index.html';
		if (path === '/coffees') path = '/coffees.html';
		if (path === '/css2') path = '/css2';
		// red serves the heavy originals straight from the site initializer (no duplicate copy)
		const file = dir === 'red' && path.startsWith('/documents/')
			? join(ROOT, '..', '..', 'liferay', 'site-initializer', 'documents', 'group', path.slice('/documents/'.length))
			: join(ROOT, dir, path);
		try {
			await stat(file);
		} catch {
			res.writeHead(404, {'Content-Type': 'text/plain'});
			return res.end('not found');
		}
		let body = await readFile(file);
		const type = path === '/css2' ? 'text/css; charset=utf-8' : TYPES[extname(path)] || 'application/octet-stream';
		const headers = {'Content-Type': type, 'Access-Control-Allow-Origin': '*'};
		if (mode === 'red') {
			headers['Cache-Control'] = 'no-cache, no-store, must-revalidate';
		} else if (mode === 'green') {
			headers['Cache-Control'] = path.startsWith('/o/') || path.endsWith('.png')
				? 'public, max-age=31536000, immutable' : 'private, no-cache';
			headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'self'";
			headers['X-Content-Type-Options'] = 'nosniff';
			headers['X-Frame-Options'] = 'SAMEORIGIN';
			headers['Cross-Origin-Opener-Policy'] = 'same-origin';
			if (/text|javascript|xml|svg/.test(type) && (req.headers['accept-encoding'] || '').includes('gzip')) {
				body = gzipSync(body);
				headers['Content-Encoding'] = 'gzip';
				headers['Vary'] = 'Accept-Encoding';
			}
		} else {
			headers['Cache-Control'] = 'public, max-age=86400';
		}
		// simulate a slow origin for the red (dev-mode, uncached) server
		const delay = mode === 'red' && type.startsWith('text/html') ? 350 : 0;
		setTimeout(() => {
			res.writeHead(200, headers);
			res.end(body);
		}, delay);
	}).listen(port, () => console.log(`${mode} on http://localhost:${port}`));
}

serve('red', 'red', 8101);
serve('green', 'green', 8102);
serve('thirdparty', 'thirdparty', 8103);
