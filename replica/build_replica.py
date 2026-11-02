"""Static replica of the Kaffora Coffee home page in its RED and GREEN states.
# Rebuild (optional): npm i bootstrap@4.6.2 jquery@3.7.1 lodash@4.17.21 && python3 build_replica.py

Purpose: (1) verify with real Lighthouse 13.5 runs that every seeded gap is
flagged and every fix clears it; (2) Plan B on stage if the Liferay instance
misbehaves.

The page is rendered from the SAME fragment sources as the Liferay bundle
(liferay/site-initializer/fragments): a tiny FreeMarker subset is evaluated and
editables are filled the way the Page Editor would, so markup and CSS match.
"""
import json
import os
import re
import shutil
import sys

from bs4 import BeautifulSoup
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, "..", "liferay", "build-tools")
SI = os.path.join(HERE, "..", "liferay", "site-initializer")
FRAG = os.path.join(SI, "fragments", "group", "kaffora", "fragments")
IMG = os.path.join(SI, "documents", "group")
OUT = os.path.join(HERE, "sites")
NM = os.path.join(HERE, "node_modules")
sys.path.insert(0, TOOLS)

from build import RED_CSS, RED_JS, RED_LLMS, RED_ROBOTS  # noqa: E402

GREEN_LLMS = """# Kaffora Coffee

> Kaffora Coffee is a (fictional) specialty roaster in São Paulo selling single-origin beans and subscriptions, roasted every Monday and delivered within 48 hours.

## Coffees

- [All coffees](/coffees): every coffee with tasting notes and price
- [Brazil Cerrado Mineiro](/coffees): 250 g, from €14
- [Ethiopia Yirgacheffe](/coffees): 250 g, from €18
- [Colombia Huila](/coffees): 250 g, from €16

## Help

- [Coffee subscription](/#newsletter): €12 per bag, every two weeks
- [Sitemap](/sitemap.xml): full list of public pages
"""

GREEN_ROBOTS = """User-Agent: *
Disallow:

Sitemap: http://localhost:8102/sitemap.xml
"""


def tokens_css(state):
    name = "kaffora-brand-v1" if state == "red" else "kaffora-accessible"
    t = json.load(open(os.path.join(SI, "style-books", name, "frontend-tokens-values.json")))
    return ":root{" + ";".join(f"--{v['cssVariableMapping']}:{v['value']}" for v in t.values()) + "}"


# ---------------------------------------------------------------- mini FreeMarker

def ftl(html, config, ns="frag"):
    def cond(m):
        expr, body = m.group(1).strip(), m.group(2)
        key = re.match(r"configuration\.(\w+)(\?has_content)?", expr).group(1)
        return body if config.get(key) else ""

    prev = None
    while prev != html:
        prev = html
        html = re.sub(r"\[#if ([^\]]+)\]((?:(?!\[#if).)*?)\[/#if\]", cond, html, flags=re.S)
    html = re.sub(r"\$\{htmlUtil\.escape\(configuration\.(\w+)\)\}",
                  lambda m: str(config.get(m.group(1), "")).replace('"', "&quot;"), html)
    html = re.sub(r"\$\{configuration\.(\w+)\}", lambda m: str(config.get(m.group(1), "")), html)
    html = html.replace("${fragmentEntryLinkNamespace}", ns)
    html = html.replace("[resources:kaffora-logo.png]", "/kaffora-logo.png")
    return html


def render(key, config=None, fields=None, ns="frag"):
    """fields: id -> str (text) | ("link", text, href) | ("img", html)."""
    raw = open(os.path.join(FRAG, key, "index.html"), encoding="utf-8").read()
    defaults = {}
    cfg_path = os.path.join(FRAG, key, "index.json")
    if os.path.exists(cfg_path):
        for fs in json.load(open(cfg_path))["fieldSets"]:
            for f in fs["fields"]:
                defaults[f["name"]] = f.get("defaultValue", "")
    defaults.update(config or {})
    soup = BeautifulSoup(ftl(raw, defaults, ns), "html.parser")
    for el in soup.select("[data-lfr-editable-id]"):
        fid = el["data-lfr-editable-id"]
        val = (fields or {}).get(fid)
        del el["data-lfr-editable-id"]
        del el["data-lfr-editable-type"]
        if val is None:
            continue
        if isinstance(val, tuple) and val[0] == "link":
            el.string = val[1]
            el["href"] = val[2]
        elif isinstance(val, tuple) and val[0] == "img":
            el.replace_with(BeautifulSoup(val[1], "html.parser"))
        else:
            el.string = val
    return str(soup)


CARDS = [
    ("coffee-cerrado", "250 g · from €14", "Brazil Cerrado Mineiro",
     "Chocolate, hazelnut and a round, sweet body. Our everyday espresso.",
     "Bag of Cerrado Mineiro beans on a caramel background", "Shop Cerrado Mineiro"),
    ("coffee-yirgacheffe", "250 g · from €18", "Ethiopia Yirgacheffe",
     "Jasmine, bergamot and lemon. Bright and tea-like, made for filter.",
     "Bag of Yirgacheffe beans on a light straw background", "Shop Yirgacheffe"),
    ("coffee-huila", "250 g · from €16", "Colombia Huila",
     "Red apple, panela and caramel with a juicy finish.",
     "Bag of Huila beans on a rose-brown background", "Shop Huila"),
]


def img_tag(state, name, cls, alt, lazy, big_w, big_h):
    if state == "red":
        return f'<img class="{cls}" src="/documents/{name}.jpg">'
    srcs = [(600, 575), (1000, 991)] if big_w < 3000 else [(800, 575), (1280, 991), (1600, 1920)]
    sources = "".join(f'<source media="(max-width:{mq}px)" srcset="/o/adaptive-media/{name}-{w}.jpg">' for w, mq in srcs)
    w0 = srcs[-1][0]
    h0 = round(w0 * big_h / big_w)
    lz = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return (f'<picture>{sources}<img class="{cls}" src="/o/adaptive-media/{name}-{w0}.jpg" '
            f'alt="{alt}" width="{w0}" height="{h0}"{lz} data-fileentryid="1"></picture>')


def page(state):
    g = state == "green"
    head = ['<meta charset="utf-8">', '<meta content="initial-scale=1.0, width=device-width" name="viewport">']
    if g:
        head += [
            "<title>Specialty coffee beans, roasted weekly | Kaffora Coffee</title>",
            '<meta name="description" content="Single-origin specialty coffee from Brazil, Ethiopia and Colombia, roasted every Monday and delivered in 48 hours. Subscribe or buy by the bag.">',
            '<link href="http://localhost:8102/" rel="canonical">',
            '<link href="/o/classic-theme/css/main.min.css" rel="stylesheet">',
            """<script type="application/ld+json">{"@context":"https://schema.org","@type":"Store","name":"Kaffora Coffee","url":"http://localhost:8102/","telephone":"+55 11 0000-0000"}</script>""",
        ]
    else:
        head += ["<title>Home - Kaffora Coffee</title>", '<meta content="noindex, nofollow" name="robots">',
                 '<link href="http://localhost:8101/home" rel="canonical">']
        for f in ["clay.css", "main.css", "portal.css", "taglib.css"]:
            head.append(f'<link href="/o/classic-theme/css/{f}" rel="stylesheet">')
        for f in ["aui.js", "liferay.js", "loader.js"]:
            head.append(f'<script src="/o/frontend-js-web/{f}"></script>')
    frag_css = "".join(open(os.path.join(FRAG, k, "index.css")).read() for k in sorted(os.listdir(FRAG)))
    base = f"""{tokens_css(state)}
body{{background:var(--body-bg);color:var(--body-color);font-family:var(--font-family-base);margin:0}}
.kaffora-section{{margin:0 auto;max-width:1040px;padding:4.5rem 1.25rem}}
.kaffora-section .component-heading{{font-weight:700;margin-bottom:3rem;text-align:center}}
.kaffora-grid{{display:grid;gap:1.5rem;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}}
.sr-only{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}}
{frag_css}"""
    head.append(f"<style>{base}</style>")
    if not g:
        head.append("<style>" + RED_CSS.replace("https://fonts.googleapis.com/css2", "http://127.0.0.1:8103/css2") + "</style>")

    L = (lambda v: v) if g else (lambda v: "")
    header = render("kaffora-header", {"searchButtonLabel": L("Search coffees"), "cartButtonLabel": L("Open cart"), "navLabel": L("Main")},
                    {"logo": ("img", '<img class="kaffora-header__logo" src="/kaffora-logo.png"' + (' alt="Kaffora Coffee home" width="144" height="36">' if g else ">"))})
    hero = render("kaffora-hero", fields={"hero-image": ("img", img_tag(
        state, "hero-coffee-4k", "kaffora-hero__img", "Latte with milk art in a white cup on a wooden table with coffee beans", False, 4000, 2667))})
    cards = "".join(
        render("kaffora-product-card", fields={
            "card-image": ("img", img_tag(state, n, "kaffora-card__img", alt, True, 2400, 1600)),
            "meta": meta, "title": title, "text": body, "link": ("link", lt if g else "Read more", "/coffees")})
        for n, meta, title, body, alt, lt in CARDS)
    lvl = "h2" if g else "h4"
    products = f'<div class="kaffora-section"><{lvl} class="component-heading">This week\'s roasts</{lvl}><div class="kaffora-grid">{cards}</div></div>'
    news = render("kaffora-newsletter", {"fieldLabel": L("E-mail address"), "exposeWebMCP": g}, ns="nl")
    footer = render("kaffora-footer", {"instagramLabel": L("Kaffora Coffee on Instagram"), "youtubeLabel": L("Kaffora Coffee on YouTube"),
                                       "linkedinLabel": L("Kaffora Coffee on LinkedIn")})
    if g:
        footer = footer.replace('To read our privacy policy, <a href="/coffees">click here</a>.', '<a href="/coffees">Read our privacy policy</a>.')
    body = (f'<a class="sr-only" href="#main-content">Skip to main content</a><div id="wrapper"><section id="content"><div id="main-content" role="main">'
            f'{header}{hero}{products}{render("kaffora-plan")}{news}{render("kaffora-about")}{footer}</div></section></div>')
    if g:
        body += "<script>document.querySelector('form').addEventListener('submit',function(e){e.preventDefault();});</script>"
    else:
        js = RED_JS.replace("https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.4/jquery.min.js", "http://127.0.0.1:8103/libs/jquery.js") \
            .replace("https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.30.1/moment-with-locales.min.js", "http://127.0.0.1:8103/libs/lodash.js?m") \
            .replace("https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.min.js", "http://127.0.0.1:8103/libs/lodash.js")
        body += f"<script>{js}</script>"
    return f'<!DOCTYPE html>\n<html class="ltr" dir="ltr" lang="en-US"><head>{"".join(head)}</head><body>{body}</body></html>\n'


def build():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    logo = os.path.join(SI, "fragments", "group", "kaffora", "resources", "kaffora-logo.png")
    for state in ["red", "green"]:
        root = os.path.join(OUT, state)
        for d in ["o/adaptive-media", "o/classic-theme/css", "o/frontend-js-web"]:
            os.makedirs(os.path.join(root, d))
        html = page(state)
        open(f"{root}/index.html", "w").write(html)
        open(f"{root}/coffees.html", "w").write(html)
        shutil.copy(logo, f"{root}/kaffora-logo.png")
        shutil.copy(logo, f"{root}/favicon.ico")
        if state == "green":
            for f in os.listdir(IMG):
                name = f[:-4]
                im = Image.open(os.path.join(IMG, f))
                for w in ([800, 1280, 1600] if "hero" in name else [600, 1000]):
                    im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(
                        f"{root}/o/adaptive-media/{name}-{w}.jpg", "JPEG", quality=78, optimize=True, progressive=True)
        bs = open(f"{NM}/bootstrap/dist/css/bootstrap.css").read()
        if state == "red":
            for f in ["clay.css", "main.css", "portal.css", "taglib.css"]:
                open(f"{root}/o/classic-theme/css/{f}", "w").write(bs if f == "clay.css" else bs[: len(bs) // 3])
            shutil.copy(f"{NM}/jquery/dist/jquery.js", f"{root}/o/frontend-js-web/aui.js")
            shutil.copy(f"{NM}/lodash/lodash.js", f"{root}/o/frontend-js-web/liferay.js")
            shutil.copy(f"{NM}/jquery/dist/jquery.js", f"{root}/o/frontend-js-web/loader.js")
            open(f"{root}/robots.txt", "w").write(RED_ROBOTS)
            open(f"{root}/llms.txt", "w").write(RED_LLMS)
        else:
            shutil.copy(f"{NM}/bootstrap/dist/css/bootstrap.min.css", f"{root}/o/classic-theme/css/main.min.css")
            open(f"{root}/robots.txt", "w").write(GREEN_ROBOTS)
            open(f"{root}/llms.txt", "w").write(GREEN_LLMS)
            open(f"{root}/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>http://localhost:8102/</loc></url><url><loc>http://localhost:8102/coffees</loc></url></urlset>')
    tp = os.path.join(OUT, "thirdparty")
    os.makedirs(f"{tp}/fonts")
    os.makedirs(f"{tp}/libs")
    faces = ""
    fonts = sorted(f for f in os.listdir("/usr/share/fonts/truetype/google-fonts") if f.startswith("Poppins-") and "Italic" not in f)[:9] \
        if os.path.isdir("/usr/share/fonts/truetype/google-fonts") else []
    for i, fn in enumerate(fonts):
        shutil.copy(os.path.join("/usr/share/fonts/truetype/google-fonts", fn), f"{tp}/fonts/f{i}.ttf")
        wt = 100 * (i + 1)
        faces += f"@font-face{{font-family:'Source Sans 3';font-weight:{wt};font-display:block;src:url(http://127.0.0.1:8103/fonts/f{i}.ttf)}}\n"
        faces += f"@font-face{{font-family:'JetBrains Mono';font-weight:{wt};font-display:block;src:url(http://127.0.0.1:8103/fonts/f{i}.ttf?m)}}\n"
    open(f"{tp}/css2", "w").write(faces)
    shutil.copy(f"{NM}/jquery/dist/jquery.min.js", f"{tp}/libs/jquery.js")
    shutil.copy(f"{NM}/lodash/lodash.min.js", f"{tp}/libs/lodash.js")
    print("replica built")


if __name__ == "__main__":
    build()
