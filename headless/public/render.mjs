// Shared (isomorphic) renderer: the SSR server and the CSR app run exactly this code.
// The only difference between /ssr and /csr is WHERE it runs.

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'})[c]);

export const META = {
	description: 'Kaffora Coffee: single-origin beans roasted every Monday and delivered in 48 hours. Shop Brazil, Ethiopia and Colombia.',
	title: 'Kaffora Coffee · This week\'s roasts',
};

export function jsonLd(coffees, origin) {
	return {
		'@context': 'https://schema.org',
		'@type': 'ItemList',
		itemListElement: coffees.map((coffee, i) => ({
			'@type': 'ListItem',
			item: {
				'@type': 'Product',
				description: coffee.notes,
				image: `${origin}/img/${coffee.image}-1000.jpg`,
				name: coffee.name,
				offers: {'@type': 'Offer', price: String(coffee.price), priceCurrency: 'EUR'},
			},
			position: i + 1,
		})),
	};
}

export function renderApp(coffees, source) {
	const cards = coffees.map((coffee, i) => `
		<li class="card">
			<img src="/img/${esc(coffee.image)}-600.jpg"
				srcset="/img/${esc(coffee.image)}-600.jpg 600w, /img/${esc(coffee.image)}-1000.jpg 1000w"
				sizes="(min-width: 960px) 30vw, 92vw" width="600" height="400"
				alt="Bag of ${esc(coffee.name)} beans" ${i === 0 ? 'fetchpriority="high"' : 'loading="lazy"'}>
			<div class="body">
				<p class="eyebrow">${esc(coffee.weight)} · from €${esc(coffee.price)}</p>
				<h3>${esc(coffee.name)}</h3>
				<p>${esc(coffee.notes)}</p>
				<a class="btn" href="#${esc(coffee.externalReferenceCode)}">Add ${esc(coffee.name)} to cart</a>
			</div>
		</li>`).join('');

	return `
	<header class="top">
		<a class="logo" href="/"><img src="/img/kaffora-logo.png" width="128" height="32" alt="Kaffora Coffee home"></a>
	</header>
	<main>
		<section class="hero">
			<h1>Coffee worth waking up for</h1>
			<p>Single-origin beans, roasted every Monday, delivered in 48 hours.</p>
		</section>
		<section aria-labelledby="roasts">
			<h2 id="roasts">This week's roasts</h2>
			<ul class="grid">${cards}</ul>
		</section>
	</main>
	<footer class="foot">
		<p>Kaffora Coffee · headless front · data: <strong>${esc(source)}</strong></p>
	</footer>`;
}

export const CSS = `
	:root { --bg:#07082B; --ink:#fff; --muted:#C7C9EA; --pink:#C2107F; --card:#12144a; }
	* { box-sizing: border-box; }
	body { margin: 0; background: var(--bg); color: var(--ink); font: 16px/1.5 system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif; }
	.top { padding: 16px; max-width: 1080px; margin: 0 auto; }
	.top img { display: block; height: 32px; width: auto; }
	main { max-width: 1080px; margin: 0 auto; padding: 0 16px 48px; }
	.hero { padding: 48px 0 32px; text-align: center; background: linear-gradient(120deg, #2a0a6e, #7a00d6 60%, #c2107f); border-radius: 24px; margin-bottom: 40px; }
	.hero h1 { font-size: clamp(32px, 7vw, 64px); line-height: 1.05; margin: 0 16px 12px; letter-spacing: -0.02em; }
	.hero p { color: #fff; margin: 0 16px; }
	h2 { text-align: center; font-size: 28px; margin: 0 0 24px; }
	.grid { display: grid; gap: 20px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); list-style: none; margin: 0; padding: 0; }
	.card { background: var(--card); border-radius: 16px; overflow: hidden; }
	.card img { display: block; width: 100%; height: auto; aspect-ratio: 3 / 2; }
	.body { padding: 16px 18px 20px; }
	.eyebrow { color: var(--muted); font-size: 14px; margin: 0 0 4px; }
	h3 { margin: 0 0 8px; font-size: 20px; }
	.btn { display: inline-block; margin-top: 8px; background: var(--pink); color: #fff; padding: 10px 16px; border-radius: 8px; text-decoration: none; font-weight: 600; }
	.foot { text-align: center; color: var(--muted); padding: 24px 16px 40px; font-size: 14px; }
	.loading { text-align: center; padding: 120px 16px; color: var(--muted); }
`;
