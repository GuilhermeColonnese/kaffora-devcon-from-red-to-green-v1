"""Build the Kaffora Coffee "red" site initializer bundle for Liferay DXP 2026.Q3.

Output:
  kaffora-devcon-kit/liferay/site-initializer/          (readable sources)
  kaffora-devcon-kit/liferay/deploy/kaffora-site-initializer.jar  (drop into deploy/)

The bundle is a resource-only OSGi bundle picked up by Liferay's
site-initializer extender (same mechanism as Liferay's own Welcome/Masterclass
initializers). After deployment, create a site from the template
"Kaffora Coffee (DevCon red)".
"""
import copy
import json
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from fragments import FRAGMENTS  # noqa: E402

KIT = os.path.join(HERE, "..", "..")
SI = os.path.join(KIT, "liferay", "site-initializer")
MASTERCLASS_TOKENS = os.path.join(HERE, "base-classic-tokens.json")
DOC = "/site-initializer/documents/group/"


def dump(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(data, str):
            f.write(data)
        else:
            json.dump(data, f, indent="\t", ensure_ascii=False)
            f.write("\n")


# ----------------------------------------------------------------- page elements

def text(fid, value):
    return {"id": fid, "value": {"fragmentLink": {"value_i18n": {}}, "text": {"value_i18n": {"en_US": value}}}}


def link(fid, label, href):
    return {"id": fid, "value": {
        "fragmentLink": {"value_i18n": {"en_US": {"href": {"value": href}, "target": "Self"}}},
        "text": {"value_i18n": {"en_US": label}},
    }}


def image_url(fid, doc, alt=""):
    """Image referenced by URL: bypasses Adaptive Media (no data-fileentryid)."""
    return {"id": fid, "value": {
        "fragmentImage": {
            "description": {"value_i18n": {"en_US": alt}},
            "url": {"value_i18n": {"en_US": f"[$DOCUMENT_URL:{DOC}{doc}$]"}},
        },
        "fragmentLink": {"value_i18n": {}},
    }}


def frag(key, fields=None, config=None, style=None):
    d = {"fragment": {"key": key}, "fragmentConfig": config or {}, "fragmentFields": fields or []}
    if style:
        d["fragmentStyle"] = style
    return {"type": "Fragment", "definition": d}


def section(children, width="Fixed", style=None):
    d = {"layout": {"widthType": width}}
    if style:
        d["fragmentStyle"] = style
    return {"type": "Section", "definition": d, "pageElements": children}


def row(columns):
    n = len(columns)
    return {"type": "Row", "definition": {
        "gutters": True, "modulesPerRow": n, "numberOfColumns": n, "reverseOrder": False,
        "rowViewports": [
            {"id": "landscapeMobile", "rowViewportDefinition": {"modulesPerRow": 1}},
            {"id": "portraitMobile", "rowViewportDefinition": {"modulesPerRow": 1}},
            {"id": "tablet", "rowViewportDefinition": {"modulesPerRow": 1}},
        ],
        "verticalAlignment": "top",
    }, "pageElements": [
        {"type": "Column", "definition": {"size": 12 // n}, "pageElements": [c]} for c in columns
    ]}


def card(doc, meta, title, body, href="/coffees"):
    return frag("kaffora-product-card", [
        image_url("card-image", doc),
        text("meta", meta),
        text("title", title),
        text("text", body),
        link("link", "Read more", href),
    ])


HEADER = frag("kaffora-header", [
    link("nav-1", "Coffees", "/coffees"),
    link("nav-2", "Subscriptions", "/coffees"),
    link("nav-3", "About", "/coffees"),
    link("cta", "Shop now", "/coffees"),
])
FOOTER = frag("kaffora-footer")

CARDS = [
    card("coffee-cerrado.jpg", "250 g · from €14", "Brazil Cerrado Mineiro",
         "Chocolate, hazelnut and a round, sweet body. Our everyday espresso."),
    card("coffee-yirgacheffe.jpg", "250 g · from €18", "Ethiopia Yirgacheffe",
         "Jasmine, bergamot and lemon. Bright and tea-like, made for filter."),
    card("coffee-huila.jpg", "250 g · from €16", "Colombia Huila",
         "Red apple, panela and caramel with a juicy finish."),
]


def home():
    return {"pageElement": {"type": "Root", "pageElements": [
        HEADER,
        frag("kaffora-hero", [
            text("title", "Coffee worth waking up for"),
            text("lead", "Single-origin beans | roasted every Monday | delivered in 48 hours"),
            link("cta", "Shop coffee", "/coffees"),
            image_url("hero-image", "hero-coffee-4k.jpg"),
            text("panel-title", "The roastery"),
            text("panel-name", "Kaffora Roastery & Bar"),
            text("panel-text", "Rua dos Pinheiros 1000, São Paulo, Brazil. Open daily, 8:00 to 18:00."),
            link("panel-cta", "Book a cupping", "/coffees"),
        ]),
        section([
            # Seeded gap: heading level jumps from h1 (hero) to h4.
            frag("BASIC_COMPONENT-heading", [text("element-text", "This week's roasts")],
                 {"headingLevel": "h4"}, {"marginBottom": "5", "textAlign": "center"}),
            row(copy.deepcopy(CARDS)),
        ], style={"paddingBottom": "6", "paddingTop": "6"}),
        frag("kaffora-plan"),
        frag("kaffora-newsletter", [
            text("title", "Fresh roasts, once a month"),
            text("text", "No spam. Unsubscribe any time."),
        ]),
        frag("kaffora-about"),
        FOOTER,
    ]}}


def coffees():
    return {"pageElement": {"type": "Root", "pageElements": [
        HEADER,
        section([
            frag("BASIC_COMPONENT-heading", [text("element-text", "All coffees")],
                 {"headingLevel": "h1"}, {"marginBottom": "4"}),
            row(copy.deepcopy(CARDS)),
        ], style={"paddingBottom": "6", "paddingTop": "6"}),
        FOOTER,
    ]}}


# ----------------------------------------------------------------- red-state assets

RED_ROBOTS = """User-agent *
Disalow: /web/
Crawl-delay 10
Sitemap: /sitemap.xml
"""

RED_CSS = """/* Brand fonts pasted from the agency's handoff (render-blocking, 18 font files, display=block).
 * The Style Book "Kaffora Brand v1" references these families. */
@import url("https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@200;300;400;500;600;700;800;900;1000&family=JetBrains+Mono:wght@100;200;300;400;500;600;700;800;900&display=block");
"""

RED_JS = """/*
 * "Tag soup": snippets pasted into the site JavaScript field by different teams over the years.
 * Every line below is a real-world anti-pattern that Lighthouse 13 flags.
 */

// 1) Legacy "analytics" fingerprinting the visitor with synchronous work on the main thread.
window.addEventListener('load', function () {
	setTimeout(function () {
		var start = Date.now();
		var fingerprint = 0;

		while (Date.now() - start < 600) {
			fingerprint += Math.sqrt(Math.random() * 1e6);
		}

		window.__kafforaFingerprint = fingerprint;
	}, 50);
});

// 2) Vendor libraries nobody uses anymore (unused + legacy JavaScript, third parties).
['https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.4/jquery.min.js',
	'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.30.1/moment-with-locales.min.js',
	'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.min.js'].forEach(function (src) {
	var script = document.createElement('script');

	script.src = src;
	document.head.appendChild(script);
});

// 3) Promo bar injected at the top of the page after load (layout shift).
setTimeout(function () {
	var bar = document.createElement('div');

	bar.setAttribute('style', 'background:#ffe08a;color:#3b2f00;font-weight:600;padding:18px 16px;text-align:center;');
	bar.textContent = 'Flash sale: 40% off your first subscription. Ends Sunday!';

	var target = document.getElementById('main-content') || document.body;

	target.insertBefore(bar, target.firstChild);
}, 1500);

// 4) Permission prompts on page load.
if (navigator.geolocation) {
	navigator.geolocation.getCurrentPosition(function () {}, function () {});
}

if ('Notification' in window && Notification.permission === 'default') {
	Notification.requestPermission();
}

// 5) "Security" team asked to block pasting into e-mail fields.
document.addEventListener('DOMContentLoaded', function () {
	document.querySelectorAll('input[type="email"]').forEach(function (input) {
		input.addEventListener('paste', function (event) {
			event.preventDefault();
		});
	});
});

// 6) Tracker that was removed from the page years ago (console error).
setTimeout(function () {
	window.legacyTracker.track('pageview');
}, 0);
"""

RED_LLMS = """Kaffora Coffee
Coffee.
"""


def tokens(primary, secondary, accent, font_base, font_mono):
    """DevCon 2026 look: navy canvas, white text, pink buttons, magenta accents."""
    with open(MASTERCLASS_TOKENS, encoding="utf-8") as f:
        t = json.load(f)
    t["primaryColor"]["value"] = primary        # button background (white text)
    t["secondaryColor"]["value"] = secondary    # muted text on navy
    t["brandColor1"]["value"] = accent          # labels, prices, links on navy
    t["brandColor2"]["value"] = "#7B1FFF"       # purple
    t["brandColor3"]["value"] = "#13153A"       # card surface
    t["brandColor4"]["value"] = "#07082B"       # navy
    t["bodyBgColor"]["value"] = "#07082B"
    t["bodyColor"]["value"] = "#FFFFFF"
    t["fontFamilyBase"]["value"] = font_base
    t["fontFamilySansSerif"]["value"] = font_base
    t["fontFamilyMonospace"]["value"] = font_mono
    return t


def build_tree():
    if not os.path.isdir(os.path.join(HERE, "images")):
        import subprocess
        subprocess.run([sys.executable, os.path.join(HERE, "gen_images.py")], check=True)
    if os.path.exists(SI):
        shutil.rmtree(SI)
    os.makedirs(SI)

    # Documents (heavy originals)
    shutil.copytree(os.path.join(HERE, "images"), os.path.join(SI, "documents", "group"),
                    ignore=shutil.ignore_patterns("kaffora-logo.png"))

    # Fragment collection
    fdir = os.path.join(SI, "fragments", "group", "kaffora")
    dump(os.path.join(fdir, "collection.json"), {
        "description": "Kaffora Coffee fragments for the DevCon 2026 Lighthouse workshop. "
                       "Accessibility and agentic attributes are exposed as configuration.",
        "name": "Kaffora Coffee",
    })
    os.makedirs(os.path.join(fdir, "resources"), exist_ok=True)
    shutil.copy(os.path.join(HERE, "images", "kaffora-logo.png"), os.path.join(fdir, "resources"))
    for key, fr in FRAGMENTS.items():
        d = os.path.join(fdir, "fragments", key)
        meta = {"cssPath": "index.css", "htmlPath": "index.html", "jsPath": "index.js",
                "name": fr["name"], "type": "component"}
        if fr["config"]:
            meta["configurationPath"] = "index.json"
            dump(os.path.join(d, "index.json"), fr["config"])
        dump(os.path.join(d, "fragment.json"), dict(sorted(meta.items())))
        dump(os.path.join(d, "index.html"), fr["html"] + "\n")
        dump(os.path.join(d, "index.css"), fr["css"])
        dump(os.path.join(d, "index.js"), fr["js"])

    # Style books
    sb_red = os.path.join(SI, "style-books", "kaffora-brand-v1")
    dump(os.path.join(sb_red, "style-book.json"), {
        "defaultStyleBookEntry": True, "frontendTokensValuesPath": "frontend-tokens-values.json",
        "name": "Kaffora Brand v1 (agency handoff)", "themeId": "classic_WAR_classictheme",
    })
    dump(os.path.join(sb_red, "frontend-tokens-values.json"),
         tokens("#FF8ADF", "#5E6190", "#8E2D7A", "'Source Sans 3', sans-serif", "'JetBrains Mono', monospace"))
    sb_green = os.path.join(SI, "style-books", "kaffora-accessible")
    dump(os.path.join(sb_green, "style-book.json"), {
        "defaultStyleBookEntry": False, "frontendTokensValuesPath": "frontend-tokens-values.json",
        "name": "Kaffora Accessible (WCAG AA)", "themeId": "classic_WAR_classictheme",
    })
    dump(os.path.join(sb_green, "frontend-tokens-values.json"),
         tokens("#C2107F", "#C7C9EA", "#FF5CCB",
                "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                "ui-monospace, 'SF Mono', 'Cascadia Mono', 'Segoe UI Mono', Menlo, Consolas, monospace"))

    # Page set (public): theme settings, robots.txt, CSS, JS
    ls = os.path.join(SI, "layout-set", "public")
    dump(os.path.join(ls, "metadata.json"), {
        "settings": {
            "false-robots.txt": RED_ROBOTS,
            "lfr-theme:regular:show-footer": False,
            "lfr-theme:regular:show-header": False,
            "lfr-theme:regular:show-header-search": False,
            "lfr-theme:regular:show-maximize-minimize-application-links": False,
            "lfr-theme:regular:wrap-widget-page-content": False,
        },
        "themeName": "Classic",
    })
    dump(os.path.join(ls, "css.css"), RED_CSS)
    dump(os.path.join(ls, "js.js"), RED_JS)

    # Site-level configuration: llms.txt enabled with poor content (fails, instead of N/A)
    dump(os.path.join(SI, "site-settings.json"), [{
        "pid": "com.liferay.site.internal.configuration.LLMSGroupConfiguration",
        "properties": {"content": RED_LLMS, "enabled": "true"},
    }])

    # Pages
    dump(os.path.join(SI, "layouts", "1_home", "page.json"), {
        "friendlyURL": "/home", "hidden": False, "name": "Home", "name_i18n": {"en_US": "Home"},
        "private": False, "priority": 0,
        # Seeded gap: page left with the staging robots directive.
        "robots_i18n": {"en_US": "noindex, nofollow"},
        "system": False, "type": "Content",
    })
    dump(os.path.join(SI, "layouts", "1_home", "page-definition.json"), home())
    dump(os.path.join(SI, "layouts", "2_coffees", "page.json"), {
        "friendlyURL": "/coffees", "hidden": False, "name": "Coffees",
        "name_i18n": {"en_US": "Coffees"}, "private": False, "priority": 1,
        "system": False, "type": "Content",
    })
    dump(os.path.join(SI, "layouts", "2_coffees", "page-definition.json"), coffees())

    shutil.copy(os.path.join(HERE, "thumbnail.png"), os.path.join(SI, "thumbnail.png"))


MANIFEST = """Manifest-Version: 1.0
Bundle-ManifestVersion: 2
Bundle-Name: Kaffora Coffee Site Initializer (DevCon 2026 red)
Bundle-SymbolicName: com.liferay.devcon.kaffora.site.initializer
Bundle-Version: 1.0.0
Liferay-Site-Initializer-Name: Kaffora Coffee (DevCon red)
Provide-Capability: liferay.site.initializer
Web-ContextPath: /site-initializer-kaffora

"""


def build_jar():
    out_dir = os.path.join(KIT, "docker", "deploy")
    os.makedirs(out_dir, exist_ok=True)
    jar = os.path.join(out_dir, "kaffora-site-initializer.jar")
    with zipfile.ZipFile(jar, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("META-INF/MANIFEST.MF", MANIFEST.replace("\n", "\r\n"))
        z.write(os.path.join(SI, "thumbnail.png"), "META-INF/resources/thumbnail.png")
        for root, _, files in os.walk(SI):
            for fn in sorted(files):
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, os.path.dirname(SI))
                z.write(full, rel.replace(os.sep, "/"))
    print("built", jar, os.path.getsize(jar) // 1024, "KB")


if __name__ == "__main__":
    build_tree()
    build_jar()
