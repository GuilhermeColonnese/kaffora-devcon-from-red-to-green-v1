"""Fragment sources for the Kaffora Coffee collection (DevCon 2026 visual language).

Look: deep navy canvas, navy → purple → magenta gradients, monospace display
type, pink pill buttons, dark bordered cards and CSS-only "glass" 3D shapes.
Colours and fonts come from Style Book tokens so the red/green swap is one click:
  --primary          button background (white text on it)
  --brand-color-1    accent text: eyebrows, labels, prices, links
  --secondary        muted body text
  --font-family-base / --font-family-monospace

Design rule for the workshop: every accessibility/SEO/agentic attribute that a
content author must own is exposed as a fragment configuration or an editable
(image description, link text). The shipped defaults are empty, so the page
starts "red" and is fixed from the Page Editor, with no code edits.
"""

ICON_SEARCH = '<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="22" height="22"><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 20l-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
ICON_BAG = '<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="22" height="22"><path d="M5 8h14l-1 12H6z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M9 8V6a3 3 0 016 0v2" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
ICON_IG = '<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="20" height="20"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
ICON_YT = '<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="20" height="20"><rect x="2" y="5" width="20" height="14" rx="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M10 9l5 3-5 3z" fill="currentColor"/></svg>'
ICON_IN = '<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="20" height="20"><rect x="3" y="3" width="18" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 014 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'

PIXEL = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

# Shared design tokens used by every fragment (duplicated per fragment on purpose:
# Liferay loads fragment CSS once per fragment type on the page).
BASE = """:root {
	--kaffora-navy: #07082B;
	--kaffora-surface: #13153A;
	--kaffora-line: #3A3D78;
	--kaffora-purple: #7B1FFF;
	--kaffora-magenta: #E4169B;
	--kaffora-gradient: linear-gradient(100deg, #07082B 0%, #1B0B5E 40%, #6A12D6 72%, #C21BC0 100%);
}
"""

BTN = """.kaffora-btn {
	background: var(--primary, #C2107F);
	border: 0;
	border-radius: 8px;
	color: #FFFFFF;
	display: inline-block;
	font-family: var(--font-family-base, system-ui, sans-serif);
	font-size: 1rem;
	font-weight: 700;
	line-height: 1.2;
	padding: 0.7rem 1.5rem;
	text-decoration: none;
}

.kaffora-btn:hover,
.kaffora-btn:focus-visible {
	color: #FFFFFF;
	filter: brightness(1.1);
	text-decoration: none;
}

.kaffora-btn--light {
	background: #FFFFFF;
	color: var(--primary, #C2107F);
}

.kaffora-btn--light:hover,
.kaffora-btn--light:focus-visible {
	color: var(--primary, #C2107F);
}
"""


def text_field(name, label, default="", description=""):
    f = {"dataType": "string", "defaultValue": default, "label": label, "name": name, "type": "text"}
    if description:
        f["description"] = description
    return f


FRAGMENTS = {}

# --------------------------------------------------------------------------- header
FRAGMENTS["kaffora-header"] = {
    "name": "Kaffora Header",
    "html": f"""<header class="kaffora-header">
	<div class="kaffora-header__inner">
		<a class="kaffora-header__brand" href="/">
			<img class="kaffora-header__logo" data-lfr-editable-id="logo" data-lfr-editable-type="image" src="[resources:kaffora-logo.png]" />
		</a>

		<nav class="kaffora-header__nav"[#if configuration.navLabel?has_content] aria-label="${{htmlUtil.escape(configuration.navLabel)}}"[/#if]>
			<a data-lfr-editable-id="nav-1" data-lfr-editable-type="link" href="/coffees">Coffees</a>
			<a data-lfr-editable-id="nav-2" data-lfr-editable-type="link" href="/coffees">Subscriptions</a>
			<a data-lfr-editable-id="nav-3" data-lfr-editable-type="link" href="/coffees">About</a>
		</nav>

		<div class="kaffora-header__actions">
			<button class="kaffora-icon-btn" type="button"[#if configuration.searchButtonLabel?has_content] aria-label="${{htmlUtil.escape(configuration.searchButtonLabel)}}"[/#if]>
				{ICON_SEARCH}
			</button>
			<button class="kaffora-icon-btn" type="button"[#if configuration.cartButtonLabel?has_content] aria-label="${{htmlUtil.escape(configuration.cartButtonLabel)}}"[/#if]>
				{ICON_BAG}
			</button>
			<a class="kaffora-btn kaffora-header__cta" data-lfr-editable-id="cta" data-lfr-editable-type="link" href="/coffees">Shop now</a>
		</div>
	</div>
</header>""",
    "css": BASE + BTN + """.kaffora-header {
	background: linear-gradient(90deg, #07082B 0%, #1B0B5E 60%, #5B12C9 100%);
	color: #FFFFFF;
	font-family: var(--font-family-base, system-ui, sans-serif);
}

.kaffora-header__inner {
	align-items: center;
	display: flex;
	gap: 2rem;
	margin: 0 auto;
	max-width: 1280px;
	min-height: 64px;
	padding: 0 1.25rem;
}

.kaffora-header__logo {
	display: block;
	height: 36px;
	width: auto;
}

.kaffora-header__nav {
	display: flex;
	flex: 1;
	font-family: var(--font-family-monospace, ui-monospace, monospace);
	font-size: 0.875rem;
	gap: 1.5rem;
	justify-content: flex-end;
}

.kaffora-header__nav a {
	color: #FFFFFF;
	text-decoration: none;
}

.kaffora-header__nav a:hover,
.kaffora-header__nav a:focus-visible {
	text-decoration: underline;
}

.kaffora-header__actions {
	align-items: center;
	display: flex;
	gap: 0.25rem;
}

.kaffora-header__cta {
	font-size: 0.875rem;
	margin-left: 0.5rem;
	padding: 0.5rem 1rem;
}

.kaffora-icon-btn {
	align-items: center;
	background: transparent;
	border: 0;
	border-radius: 50%;
	color: #FFFFFF;
	display: inline-flex;
	height: 44px;
	justify-content: center;
	width: 44px;
}

.kaffora-icon-btn:hover,
.kaffora-icon-btn:focus-visible {
	background: rgba(255, 255, 255, 0.12);
}

@media (max-width: 767px) {
	.kaffora-header .kaffora-header__nav,
	.kaffora-header .kaffora-header__cta {
		display: none;
	}

	.kaffora-header__actions {
		margin-left: auto;
	}
}
""",
    "js": "",
    "config": {"fieldSets": [{"label": "Accessibility", "fields": [
        text_field("searchButtonLabel", "Search button accessible name", "", "Announced by screen readers and AI agents, e.g. 'Search coffees'."),
        text_field("cartButtonLabel", "Cart button accessible name", "", "e.g. 'Open cart'."),
        text_field("navLabel", "Navigation landmark label", "", "e.g. 'Main'."),
    ]}]},
}

# --------------------------------------------------------------------------- hero + roastery band
FRAGMENTS["kaffora-hero"] = {
    "name": "Kaffora Hero",
    "html": f"""<section class="kaffora-hero">
	<div class="kaffora-hero__intro">
		<div aria-hidden="true" class="kaffora-shape kaffora-shape--a"></div>
		<div aria-hidden="true" class="kaffora-shape kaffora-shape--b"></div>
		<div aria-hidden="true" class="kaffora-shape kaffora-shape--c"></div>

		<div class="kaffora-hero__copy">
			<h1 class="kaffora-hero__title" data-lfr-editable-id="title" data-lfr-editable-type="text">Coffee worth waking up for</h1>

			<p class="kaffora-hero__lead" data-lfr-editable-id="lead" data-lfr-editable-type="text">Single-origin beans | roasted every Monday | delivered in 48 hours</p>

			<a class="kaffora-btn" data-lfr-editable-id="cta" data-lfr-editable-type="link" href="/coffees">Shop coffee</a>
		</div>
	</div>

	<div class="kaffora-hero__band">
		<img class="kaffora-hero__img" data-lfr-editable-id="hero-image" data-lfr-editable-type="image" src="{PIXEL}" />

		<div class="kaffora-hero__panel">
			<h2 class="kaffora-hero__panel-title" data-lfr-editable-id="panel-title" data-lfr-editable-type="text">The roastery</h2>

			<p class="kaffora-hero__panel-name" data-lfr-editable-id="panel-name" data-lfr-editable-type="text">Kaffora Roastery &amp; Bar</p>

			<p class="kaffora-hero__panel-text" data-lfr-editable-id="panel-text" data-lfr-editable-type="text">Rua dos Pinheiros 1000, São Paulo, Brazil. Open daily, 8:00 to 18:00.</p>

			<a class="kaffora-btn kaffora-btn--light kaffora-hero__panel-btn" data-lfr-editable-id="panel-cta" data-lfr-editable-type="link" href="/coffees">Book a cupping</a>
		</div>
	</div>
</section>""",
    "css": BASE + BTN + """.kaffora-hero {
	background: var(--kaffora-navy);
	color: #FFFFFF;
	font-family: var(--font-family-base, system-ui, sans-serif);
}

.kaffora-hero__intro {
	background: var(--kaffora-gradient);
	overflow: hidden;
	padding: 5.5rem 1.25rem 6rem;
	position: relative;
	text-align: center;
}

.kaffora-hero__copy {
	margin: 0 auto;
	max-width: 880px;
	position: relative;
}

.kaffora-hero__title {
	font-family: var(--font-family-monospace, ui-monospace, monospace);
	font-size: clamp(2.25rem, 6vw, 4.5rem);
	font-weight: 800;
	letter-spacing: 0.02em;
	line-height: 1.05;
	margin: 0 0 1.25rem;
	text-transform: uppercase;
}

.kaffora-hero__lead {
	font-size: 1.125rem;
	margin: 0 0 1.75rem;
}

/* CSS-only "glass" shapes, echoing the DevCon 2026 key visual. Decorative, aria-hidden. */
.kaffora-shape {
	border-radius: 14px;
	pointer-events: none;
	position: absolute;
}

.kaffora-shape--a {
	background: linear-gradient(135deg, rgba(210, 212, 255, 0.95), rgba(120, 118, 220, 0.55));
	box-shadow: inset -18px -18px 40px rgba(40, 30, 120, 0.45);
	height: 150px;
	left: -30px;
	top: -40px;
	transform: rotate(38deg) skewX(-8deg);
	width: 150px;
}

.kaffora-shape--b {
	background: linear-gradient(135deg, rgba(200, 200, 255, 0.85), rgba(90, 80, 200, 0.4));
	height: 110px;
	left: 120px;
	top: -50px;
	transform: rotate(28deg);
	width: 180px;
}

.kaffora-shape--c {
	background: linear-gradient(160deg, #FFB8F5 0%, #E04CE8 45%, #9A10D8 100%);
	box-shadow: inset 20px 0 50px rgba(255, 255, 255, 0.35);
	height: 330px;
	right: 60px;
	top: -40px;
	transform: rotate(32deg) skewY(-6deg);
	width: 150px;
}

.kaffora-hero__band {
	min-height: 420px;
	position: relative;
}

.kaffora-hero__img {
	display: block;
	height: 420px;
	object-fit: cover;
	width: 100%;
}

.kaffora-hero__panel {
	background: rgba(12, 12, 52, 0.92);
	bottom: 12px;
	left: max(1.25rem, calc(50% - 400px));
	padding: 2.25rem 1.5rem;
	position: absolute;
	top: 12px;
	width: min(260px, calc(100% - 2.5rem));
}

.kaffora-hero__panel-title {
	font-size: 1.75rem;
	font-weight: 700;
	margin: 0 0 1.5rem;
}

.kaffora-hero__panel-name {
	font-size: 1.25rem;
	font-weight: 700;
	line-height: 1.3;
	margin: 0 0 0.75rem;
}

.kaffora-hero__panel-text {
	color: var(--secondary, #C7C9EA);
	font-size: 0.9375rem;
	margin: 0 0 1.5rem;
}

.kaffora-hero__panel-btn {
	font-size: 0.875rem;
	padding: 0.45rem 1.25rem;
}

@media (max-width: 767px) {
	.kaffora-shape--a,
	.kaffora-shape--b {
		display: none;
	}

	.kaffora-shape--c {
		height: 200px;
		right: -50px;
		width: 90px;
	}

	.kaffora-hero__band {
		min-height: 0;
	}

	.kaffora-hero__img {
		height: 260px;
	}

	.kaffora-hero__panel {
		bottom: auto;
		left: auto;
		position: relative;
		top: auto;
		width: auto;
	}
}
""",
    "js": "",
    "config": None,
}

# --------------------------------------------------------------------------- product card
FRAGMENTS["kaffora-product-card"] = {
    "name": "Kaffora Product Card",
    "html": f"""<article class="kaffora-card">
	<img class="kaffora-card__img" data-lfr-editable-id="card-image" data-lfr-editable-type="image" src="{PIXEL}" />

	<div class="kaffora-card__body">
		<p class="kaffora-card__meta" data-lfr-editable-id="meta" data-lfr-editable-type="text">250 g · from €15</p>

		<h3 class="kaffora-card__title" data-lfr-editable-id="title" data-lfr-editable-type="text">Coffee</h3>

		<p class="kaffora-card__text" data-lfr-editable-id="text" data-lfr-editable-type="text">Tasting notes.</p>

		<a class="kaffora-card__link" data-lfr-editable-id="link" data-lfr-editable-type="link" href="/coffees">Read more</a>
	</div>
</article>""",
    "css": BASE + """.kaffora-card {
	background: var(--kaffora-surface);
	border: 1px solid var(--kaffora-line);
	border-radius: 18px;
	color: #FFFFFF;
	font-family: var(--font-family-base, system-ui, sans-serif);
	height: 100%;
	overflow: hidden;
}

.kaffora-card__img {
	display: block;
	height: auto;
	width: 100%;
}

.kaffora-card__body {
	padding: 1.25rem 1.25rem 1.5rem;
	text-align: center;
}

.kaffora-card__meta {
	color: var(--brand-color-1, #FF5CCB);
	font-size: 0.875rem;
	font-weight: 700;
	margin: 0 0 0.5rem;
}

.kaffora-card__title {
	font-size: 1.375rem;
	font-weight: 700;
	margin: 0 0 0.5rem;
}

.kaffora-card__text {
	color: var(--secondary, #C7C9EA);
	margin: 0 0 1rem;
}

.kaffora-card__link {
	color: var(--brand-color-1, #FF5CCB);
	font-weight: 700;
}
""",
    "js": "",
    "config": None,
}

# --------------------------------------------------------------------------- subscription plan
FRAGMENTS["kaffora-plan"] = {
    "name": "Kaffora Subscription Plan",
    "html": """<section class="kaffora-plan">
	<div class="kaffora-plan__inner">
		<h2 class="kaffora-plan__title" data-lfr-editable-id="title" data-lfr-editable-type="text">Coffee subscription</h2>

		<p class="kaffora-plan__price" data-lfr-editable-id="price" data-lfr-editable-type="text">€12</p>

		<p class="kaffora-plan__rate" data-lfr-editable-id="rate" data-lfr-editable-type="text">Per 250 g bag, every two weeks</p>

		<p class="kaffora-plan__note" data-lfr-editable-id="note" data-lfr-editable-type="text">*Free shipping on subscriptions</p>

		<h3 class="kaffora-plan__subtitle" data-lfr-editable-id="subtitle" data-lfr-editable-type="text">Your subscription includes</h3>

		<ul class="kaffora-plan__grid">
			<li class="kaffora-plan__item">
				<p class="kaffora-plan__label" data-lfr-editable-id="label-1" data-lfr-editable-type="text">Monday</p>
				<p class="kaffora-plan__text" data-lfr-editable-id="text-1" data-lfr-editable-type="text">Roasted to order, in small batches</p>
			</li>
			<li class="kaffora-plan__item">
				<p class="kaffora-plan__label" data-lfr-editable-id="label-2" data-lfr-editable-type="text">48 hours</p>
				<p class="kaffora-plan__text" data-lfr-editable-id="text-2" data-lfr-editable-type="text">From the roaster to your door</p>
			</li>
			<li class="kaffora-plan__item">
				<p class="kaffora-plan__label" data-lfr-editable-id="label-3" data-lfr-editable-type="text">Any time</p>
				<p class="kaffora-plan__text" data-lfr-editable-id="text-3" data-lfr-editable-type="text">Pause, skip or swap origins</p>
			</li>
			<li class="kaffora-plan__item">
				<p class="kaffora-plan__label" data-lfr-editable-id="label-4" data-lfr-editable-type="text">Bonus</p>
				<p class="kaffora-plan__text" data-lfr-editable-id="text-4" data-lfr-editable-type="text">Brew guide and tasting card</p>
			</li>
		</ul>

		<a class="kaffora-btn" data-lfr-editable-id="cta" data-lfr-editable-type="link" href="/coffees">Start subscription</a>
	</div>
</section>""",
    "css": BASE + BTN + """.kaffora-plan {
	background: var(--kaffora-navy);
	color: #FFFFFF;
	font-family: var(--font-family-base, system-ui, sans-serif);
	padding: 3.5rem 1.25rem;
	text-align: center;
}

.kaffora-plan__inner {
	margin: 0 auto;
	max-width: 820px;
}

.kaffora-plan__title {
	font-size: 2rem;
	font-weight: 700;
	margin: 0 0 1rem;
}

.kaffora-plan__price {
	color: var(--brand-color-1, #FF5CCB);
	font-family: var(--font-family-monospace, ui-monospace, monospace);
	font-size: 3rem;
	font-weight: 800;
	line-height: 1;
	margin: 0 0 0.75rem;
}

.kaffora-plan__rate {
	font-weight: 700;
	margin: 0 0 0.25rem;
}

.kaffora-plan__note {
	color: var(--secondary, #C7C9EA);
	font-size: 0.875rem;
	font-style: italic;
	margin: 0 0 1.75rem;
}

.kaffora-plan__subtitle {
	font-size: 1.25rem;
	font-weight: 700;
	margin: 0 0 1.5rem;
}

.kaffora-plan__grid {
	display: grid;
	gap: 1.25rem;
	grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
	list-style: none;
	margin: 0 0 1.75rem;
	padding: 0;
}

.kaffora-plan__item {
	background: var(--kaffora-surface);
	border: 1px solid var(--kaffora-line);
	border-radius: 18px;
	padding: 1.5rem 1rem;
}

.kaffora-plan__label {
	color: var(--brand-color-1, #FF5CCB);
	font-size: 0.875rem;
	font-weight: 700;
	margin: 0 0 0.75rem;
}

.kaffora-plan__text {
	font-size: 0.9375rem;
	margin: 0;
}
""",
    "js": "",
    "config": None,
}

# --------------------------------------------------------------------------- newsletter
FRAGMENTS["kaffora-newsletter"] = {
    "name": "Kaffora Newsletter",
    "html": """<section class="kaffora-newsletter" id="newsletter">
	<div aria-hidden="true" class="kaffora-newsletter__shape"></div>

	<div class="kaffora-newsletter__inner">
		<div>
			<h2 class="kaffora-newsletter__title" data-lfr-editable-id="title" data-lfr-editable-type="text">Fresh roasts, once a month</h2>

			<p class="kaffora-newsletter__text" data-lfr-editable-id="text" data-lfr-editable-type="text">No spam. Unsubscribe any time.</p>
		</div>

		<form action="#" class="kaffora-newsletter__form"[#if configuration.exposeWebMCP] toolname="subscribeToNewsletter" tooldescription="${htmlUtil.escape(configuration.webMCPDescription)}"[/#if]>
			[#if configuration.fieldLabel?has_content]
				<label class="kaffora-newsletter__label" for="${fragmentEntryLinkNamespace}-email">${htmlUtil.escape(configuration.fieldLabel)}</label>
			[/#if]

			<div class="kaffora-newsletter__row">
				<input autocomplete="email" class="form-control kaffora-newsletter__input" id="${fragmentEntryLinkNamespace}-email" name="email" placeholder="name@example.com" required type="email"[#if configuration.exposeWebMCP] toolparamdescription="E-mail address that will receive the newsletter"[/#if] />

				<button class="kaffora-btn" type="submit">Subscribe</button>
			</div>

			<p aria-live="polite" class="kaffora-newsletter__status"></p>
		</form>
	</div>
</section>""",
    "css": BASE + BTN + """.kaffora-newsletter {
	background: linear-gradient(100deg, #07082B 0%, #3A0C8C 45%, #B0149E 78%, #6A12D6 100%);
	color: #FFFFFF;
	font-family: var(--font-family-base, system-ui, sans-serif);
	overflow: hidden;
	padding: 4rem 1.25rem;
	position: relative;
}

.kaffora-newsletter__shape {
	background: linear-gradient(160deg, #FFC4F7 0%, #D85BE9 50%, #8A12D0 100%);
	border-radius: 16px;
	bottom: -60px;
	height: 160px;
	position: absolute;
	right: -20px;
	transform: rotate(-24deg);
	width: 320px;
}

.kaffora-newsletter__inner {
	align-items: center;
	display: grid;
	gap: 1.5rem;
	margin: 0 auto;
	max-width: 1040px;
	position: relative;
}

@media (min-width: 992px) {
	.kaffora-newsletter__inner {
		grid-template-columns: 1fr 1fr;
	}
}

.kaffora-newsletter__title {
	font-family: var(--font-family-monospace, ui-monospace, monospace);
	font-size: 1.75rem;
	font-weight: 800;
	margin: 0 0 0.5rem;
}

.kaffora-newsletter__text {
	margin: 0;
}

.kaffora-newsletter__label {
	display: block;
	font-weight: 700;
	margin-bottom: 0.375rem;
}

.kaffora-newsletter__row {
	display: flex;
	gap: 0.5rem;
}

.kaffora-newsletter__input {
	background: #FFFFFF;
	border: 0;
	border-radius: 8px;
	color: #07082B;
}

.kaffora-newsletter__status {
	margin: 0.5rem 0 0;
	min-height: 1.5em;
}
""",
    "js": """const form = fragmentElement.querySelector('form');

if (form) {
	form.addEventListener('submit', (event) => {
		event.preventDefault();

		const status = form.querySelector('.kaffora-newsletter__status');

		if (status) {
			status.textContent = 'Thanks! Check your inbox to confirm.';
		}
	});
}
""",
    "config": {"fieldSets": [
        {"label": "Accessibility", "fields": [
            text_field("fieldLabel", "E-mail field label", "", "Visible label for the e-mail input, e.g. 'E-mail address'."),
        ]},
        {"label": "Agentic browsing (WebMCP)", "fields": [
            {"defaultValue": False, "label": "Expose this form to AI agents (WebMCP declarative API)", "name": "exposeWebMCP", "type": "checkbox", "typeOptions": {"displayType": "toggle"}},
            text_field("webMCPDescription", "Tool description for agents", "Subscribe an e-mail address to the Kaffora Coffee monthly roasts newsletter."),
        ]},
    ]},
}

# --------------------------------------------------------------------------- about (two columns)
FRAGMENTS["kaffora-about"] = {
    "name": "Kaffora About",
    "html": """<section class="kaffora-about">
	<div class="kaffora-about__inner">
		<div>
			<h2 class="kaffora-about__label" data-lfr-editable-id="label-1" data-lfr-editable-type="text">About Kaffora</h2>

			<div class="kaffora-about__text" data-lfr-editable-id="text-1" data-lfr-editable-type="rich-text"><p>Kaffora is a small specialty roaster in São Paulo. We buy green coffee directly from farms we visit every harvest and roast it in 15 kg batches every Monday.</p><p>Every bag carries the farm, the variety, the process and the roast date, so you always know what is in your cup.</p></div>
		</div>

		<div aria-hidden="true" class="kaffora-about__art">
			<span class="kaffora-about__disc"></span>
			<span class="kaffora-about__bar"></span>
			<span class="kaffora-about__dot"></span>
		</div>

		<div>
			<h2 class="kaffora-about__label" data-lfr-editable-id="label-2" data-lfr-editable-type="text">Our sourcing</h2>

			<div class="kaffora-about__text" data-lfr-editable-id="text-2" data-lfr-editable-type="rich-text"><p>We pay at least 40% above the commodity price and publish every contract. Our partner farms are in Minas Gerais, Huila and the Gedeo zone of Ethiopia.</p><p>Packaging is compostable, and shipping in Brazil is carbon-offset.</p></div>
		</div>
	</div>
</section>""",
    "css": BASE + """.kaffora-about {
	background: var(--kaffora-navy);
	color: #FFFFFF;
	font-family: var(--font-family-base, system-ui, sans-serif);
	padding: 3.5rem 1.25rem;
}

.kaffora-about__inner {
	align-items: start;
	display: grid;
	gap: 2rem;
	margin: 0 auto;
	max-width: 1040px;
}

@media (min-width: 992px) {
	.kaffora-about__inner {
		grid-template-columns: 1fr 260px 1fr;
	}
}

.kaffora-about__label {
	color: var(--brand-color-1, #FF5CCB);
	font-size: 1rem;
	font-weight: 700;
	margin: 0 0 1rem;
}

.kaffora-about__text p {
	font-size: 0.9375rem;
	margin: 0 0 1rem;
}

.kaffora-about__art {
	aspect-ratio: 1;
	justify-self: center;
	max-width: 260px;
	width: 100%;
	background: radial-gradient(circle at 70% 25%, #C21BC0 0%, #5B12C9 45%, #13153A 80%);
	border-radius: 4px;
	overflow: hidden;
	position: relative;
}

.kaffora-about__disc {
	background: linear-gradient(135deg, #E9E6FF, #8D86E8);
	border-radius: 50%;
	bottom: -30px;
	height: 150px;
	left: -20px;
	position: absolute;
	width: 150px;
}

.kaffora-about__bar {
	background: linear-gradient(160deg, #FFC4F7, #C43BDF);
	border-radius: 10px;
	height: 150px;
	position: absolute;
	right: 30px;
	top: 20px;
	transform: rotate(35deg);
	width: 44px;
}

.kaffora-about__dot {
	background: #FFFFFF;
	border-radius: 50%;
	height: 40px;
	left: 90px;
	position: absolute;
	top: 80px;
	width: 40px;
}
""",
    "js": "",
    "config": None,
}

# --------------------------------------------------------------------------- footer
FRAGMENTS["kaffora-footer"] = {
    "name": "Kaffora Footer",
    "html": f"""<footer class="kaffora-footer">
	<div class="kaffora-footer__inner">
		<h2 class="kaffora-footer__title" data-lfr-editable-id="title" data-lfr-editable-type="text">Questions?</h2>

		<a class="kaffora-btn" data-lfr-editable-id="contact" data-lfr-editable-type="link" href="/coffees">Contact us</a>

		<p class="kaffora-footer__legal" data-lfr-editable-id="legal" data-lfr-editable-type="rich-text">© 2026 Kaffora Coffee (fictional brand). To read our privacy policy, <a href="/coffees">click here</a>.</p>

		<div class="kaffora-footer__bottom">
			<span class="kaffora-footer__brand">Kaffora</span>

			<div class="kaffora-footer__social">
				<a href="https://www.instagram.com/"[#if configuration.instagramLabel?has_content] aria-label="${{htmlUtil.escape(configuration.instagramLabel)}}"[/#if]>{ICON_IG}</a>
				<a href="https://www.youtube.com/"[#if configuration.youtubeLabel?has_content] aria-label="${{htmlUtil.escape(configuration.youtubeLabel)}}"[/#if]>{ICON_YT}</a>
				<a href="https://www.linkedin.com/"[#if configuration.linkedinLabel?has_content] aria-label="${{htmlUtil.escape(configuration.linkedinLabel)}}"[/#if]>{ICON_IN}</a>
			</div>
		</div>
	</div>
</footer>""",
    "css": BASE + BTN + """.kaffora-footer {
	background: var(--kaffora-navy);
	color: #FFFFFF;
	font-family: var(--font-family-base, system-ui, sans-serif);
	padding: 3rem 1.25rem 2rem;
	text-align: center;
}

.kaffora-footer__inner {
	margin: 0 auto;
	max-width: 1040px;
}

.kaffora-footer__title {
	font-size: 2rem;
	font-weight: 700;
	margin: 0 0 1.25rem;
}

.kaffora-footer__legal {
	color: var(--secondary, #C7C9EA);
	font-size: 0.9375rem;
	margin: 1.5rem 0 2.5rem;
}

.kaffora-footer__legal a {
	color: var(--brand-color-1, #FF5CCB);
	text-decoration: underline;
}

.kaffora-footer__bottom {
	align-items: center;
	border-top: 1px solid var(--kaffora-line);
	display: flex;
	flex-wrap: wrap;
	gap: 1rem;
	justify-content: space-between;
	padding-top: 1.25rem;
}

.kaffora-footer__brand {
	font-family: var(--font-family-monospace, ui-monospace, monospace);
	font-size: 1.5rem;
	font-weight: 800;
}

.kaffora-footer__social {
	display: flex;
	gap: 0.25rem;
}

.kaffora-footer__social a {
	align-items: center;
	color: #FFFFFF;
	display: inline-flex;
	height: 44px;
	justify-content: center;
	width: 44px;
}
""",
    "js": "",
    "config": {"fieldSets": [{"label": "Accessibility", "fields": [
        text_field("instagramLabel", "Instagram link accessible name", "", "e.g. 'Kaffora Coffee on Instagram'."),
        text_field("youtubeLabel", "YouTube link accessible name", ""),
        text_field("linkedinLabel", "LinkedIn link accessible name", ""),
    ]}]},
}

# --------------------------------------------------------------------------- schema.org
FRAGMENTS["kaffora-schema-org"] = {
    "name": "Schema.org JSON-LD (Organization)",
    "html": """[#if layoutMode == "edit"]
	<div class="kaffora-schema-placeholder">
		Schema.org JSON-LD · ${htmlUtil.escape(configuration.schemaType)} · "${htmlUtil.escape(configuration.orgName)}" (invisible to visitors)
	</div>
[/#if]
<script type="application/ld+json">
{
	"@context": "https://schema.org",
	"@type": "${configuration.schemaType?json_string}",
	"name": "${configuration.orgName?json_string}",
	"description": "${configuration.orgDescription?json_string}",
	"url": "${configuration.orgUrl?json_string}",
	"logo": "${configuration.logoUrl?json_string}",
	"telephone": "${configuration.telephone?json_string}",
	"sameAs": ["https://www.instagram.com/", "https://www.youtube.com/"]
}
</script>""",
    "css": """.kaffora-schema-placeholder {
	background: repeating-linear-gradient(45deg, #13153A, #13153A 10px, #1B1E4A 10px, #1B1E4A 20px);
	border: 1px dashed #6B6FB0;
	border-radius: 0.5rem;
	color: #FFFFFF;
	font-family: monospace;
	font-size: 0.8125rem;
	padding: 0.75rem 1rem;
}
""",
    "js": "",
    "config": {"fieldSets": [{"label": "Structured data", "fields": [
        {"dataType": "string", "defaultValue": "Store", "label": "Schema.org type", "name": "schemaType", "type": "select",
         "typeOptions": {"validValues": [{"value": "Store"}, {"value": "Organization"}, {"value": "LocalBusiness"}]}},
        text_field("orgName", "Name", "Kaffora Coffee"),
        text_field("orgDescription", "Description", "Single-origin specialty coffee, roasted weekly and delivered in 48 hours."),
        text_field("orgUrl", "Canonical site URL", "http://kaffora.localhost:8080/"),
        text_field("logoUrl", "Logo URL", "http://kaffora.localhost:8080/logo.png"),
        text_field("telephone", "Telephone", "+55 11 0000-0000"),
    ]}]},
}
