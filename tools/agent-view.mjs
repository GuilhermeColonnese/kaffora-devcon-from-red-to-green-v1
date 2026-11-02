// What does an agent that doesn't run JavaScript see? Fetches the raw HTML only.
// Usage: node tools/agent-view.mjs <url> [<url> ...]
const urls = process.argv.slice(2);

if (!urls.length) {
	console.error('usage: node tools/agent-view.mjs <url> [<url> ...]');
	process.exit(1);
}

const strip = (html) => html
	.replace(/<script[\s\S]*?<\/script>/gi, ' ')
	.replace(/<style[\s\S]*?<\/style>/gi, ' ')
	.replace(/<[^>]+>/g, ' ')
	.replace(/&nbsp;|&#160;/g, ' ')
	.replace(/&amp;/g, '&')
	.replace(/&#39;|&apos;/g, "'")
	.replace(/\s+/g, ' ')
	.trim();

for (const url of urls) {
	const response = await fetch(url, {headers: {'User-Agent': 'Mozilla/5.0 (compatible; KafforaAgentView/1.0; no-JS)'}});
	const html = await response.text();
	const title = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]?.trim() || '(none)';
	const description = html.match(/<meta[^>]+name=["']description["'][^>]*content=["']([^"']*)/i)?.[1] || '(none)';
	const headings = [...html.matchAll(/<h([1-3])[^>]*>([\s\S]*?)<\/h\1>/gi)].map((m) => `h${m[1]} ${strip(m[2])}`);
	const jsonLd = (html.match(/application\/ld\+json/gi) || []).length;
	const text = strip(html.replace(/<head[\s\S]*?<\/head>/i, ''));

	console.log(`\n${url}  (HTTP ${response.status}, ${html.length.toLocaleString()} bytes of HTML)`);
	console.log(`  title        ${title}`);
	console.log(`  description  ${description}`);
	console.log(`  headings     ${headings.length ? headings.join(' · ') : '(none)'}`);
	console.log(`  JSON-LD      ${jsonLd ? `${jsonLd} block(s)` : '(none)'}`);
	console.log(`  visible text ${text.length.toLocaleString()} chars: "${text.slice(0, 160)}${text.length > 160 ? '…' : ''}"`);
}
console.log('');
