# From Red to Green · Liferay DevCon 2026 workshop kit

**Improving SEO, Accessibility, Performance and Agentic Browsing scores with Liferay DXP Free Tier.**

A deliberately broken Liferay DXP site, **Kaffora Coffee** (a fictional specialty-coffee store), with real gaps in all five Lighthouse 13 categories, plus everything you need to take it from red to green with native Liferay features: Adaptive Media, Style Books, fragment configuration, client extensions, page SEO settings, `llms.txt`, the MCP Server, production properties and a CDN.

Built for a 40-minute, hands-on session at Liferay DevCon 2026. Everything runs locally on **Liferay DXP Free Tier 2026.Q3** with a free activation key, on macOS, Windows and Linux.

| | Performance | Accessibility | Best Practices | SEO | Agentic Browsing | LCP |
|---|---|---|---|---|---|---|
| **Red** (mobile) | 24 | 81 | 77 | 38 | 0/3 | 61.9 s |
| **Green** (mobile) | ~75 | 100 | 100 | 100 | 3/3 | 5.0 s |
| **Green** (desktop) | 98 | 100 | 100 | 100 | 3/3 | 1.1 s |

<sub>Reference dry run on a laptop, Lighthouse 13.5, simulated throttling. Your numbers will differ by a few points; compare deltas, not absolutes. What is left on mobile is the platform shell (Clay CSS, runtime JS) under simulated slow 4G.</sub>

## What you will practise

1. **Measure** the red site with a pinned Lighthouse 13.5 runner (mobile + desktop).
2. **Fix the content** in Liferay, one category at a time, still on the red server:
   - Performance: Adaptive Media (and the 2× trap), an LCP `fetchpriority` switch added to a fragment as an author option, self-hosted fonts and governed tags as **client extensions**.
   - Accessibility: Style Book tokens, accessible names through fragment configuration, Image Descriptions, heading order.
   - SEO: page SEO settings, robots.txt, descriptive link text, Redirection and XML Sitemap.
   - Best Practices: no tag soup, CSP with a nonce.
   - Agentic Browsing: native `llms.txt`, a WebMCP-exposed form, Schema.org JSON-LD, and **Liferay as an MCP server**.
3. **Fix the last mile**: production portal properties, GZip and a local CDN edge (Nginx), then re-measure and compare on a 3-column scoreboard.
4. **Bonus**: the same content rendered headless as SSR vs CSR, and what an agent that doesn't run JavaScript actually sees.

## Requirements

| | macOS | Windows 10/11 | Linux |
|---|---|---|---|
| Docker (8 GB RAM for containers) | Docker Desktop | Docker Desktop (WSL 2 backend) | Docker Engine + Compose plugin |
| Node.js 22+ | `brew install node@22` | `winget install OpenJS.NodeJS.LTS` | `nvm install 22` |
| Google Chrome | `brew install --cask google-chrome` | `winget install Google.Chrome` | `google-chrome-stable` |
| Liferay DXP Free Tier key | free at [marketplace.liferay.com/p/liferay-dxp-free-tier](https://marketplace.liferay.com/p/liferay-dxp-free-tier), domain `localhost` | same | same |

## Quick start

```bash
git clone <this repository> kaffora-devcon-kit
cd kaffora-devcon-kit
npm install                                   # Lighthouse 13.5 + chrome-launcher

# copy your Free Tier key into docker/deploy/
#   macOS/Linux: cp ~/Downloads/activation-key-*.xml docker/deploy/
#   Windows:     Copy-Item $HOME\Downloads\activation-key-*.xml docker\deploy\

cd docker
docker compose up -d                          # red profile, wait for "Server startup" in the logs
docker compose logs -f liferay
```

Then, in Liferay (`http://localhost:8080`, `test@liferay.com` / `test`):

1. **Control Panel → Sites → Add** → template **Kaffora Coffee (DevCon red)**.
2. **Site Settings → Site URL → Virtual Host:** `kaffora.localhost` (Chrome resolves `*.localhost` to your machine; no hosts file needed).
3. From the **repository root** (not from `tools/`), measure the baseline:

```bash
node tools/lh.mjs baseline http://kaffora.localhost:8080/
```

Follow [`docs/WORKSHOP-GUIDE.md`](docs/WORKSHOP-GUIDE.md) from there.

## Workshop flow (40 min)

| Time | Stage | What happens |
|---|---|---|
| 00–06 | Concepts | Lighthouse 13 insights, the five categories, how Agentic Browsing is scored |
| 06–10 | **Stage 1 · Baseline** | Everyone measures the red site |
| 10–31 | **Stage 2 · Fix the content** | Five checkpoints, one per category, on the red server; then measure `content` |
| 31–36 | **Stage 3 · Last mile** | Green profile + CDN, measure `final`, scoreboard baseline → content → final |
| 36–40 | Wrap-up | Who owns what (SEO responsibility matrix), takeaways, Q&A |

## Repository layout

```
.
├── docker/                 Liferay DXP Free Tier 2026.Q3 + PostgreSQL
│   ├── docker-compose.yml          red profile (developer mode leaked to production)
│   ├── docker-compose.green.yml    override: production profile + local CDN (Nginx) on :8081
│   ├── profiles/red|green/         portal-ext.properties + client extensions (osgi/client-extensions/)
│   ├── cdn/nginx.conf              gzip, edge cache (X-Cache MISS/HIT), CORS
│   └── deploy/                     kaffora-site-initializer.jar (+ your Free Tier key, git-ignored)
├── liferay/
│   ├── site-initializer/           readable sources of the site template (fragments, pages, Style Books…)
│   └── build-tools/                Python scripts that regenerate the bundle and the images
├── client-extensions/      CSS + JS client extensions (brand fonts, governed tags) and a Gradle-free build
├── fixes/                  ready-to-import fix pack, one folder per checkpoint
├── tools/                  Lighthouse runner, scoreboard, compare, agent view, headless seed
├── headless/               bonus: Node front reading Liferay Objects, rendered /ssr and /csr
├── replica/                static red/green copy of the page (plan B, no Liferay needed)
├── reports/                Lighthouse output (git-ignored)
└── docs/
    ├── WORKSHOP-GUIDE.md           step-by-step build-along guide
    ├── RUN-OF-SHOW.md              minute-by-minute presenter script
    └── CHECKLIST.md                Lighthouse 13 insight → Liferay DXP setting
```

## Tools

| Command | What it does |
|---|---|
| `node tools/lh.mjs <label> <url> [mobile\|desktop\|both] [--open]` | Runs Lighthouse 13.5 in a clean Chrome; saves `reports/<label>-<form factor>.report.html/json` and prints a summary |
| `node tools/scoreboard.mjs baseline content final --open` | Builds `reports/scoreboard.html` with 2 or 3 runs and a Mobile/Desktop switch |
| `node tools/compare.mjs <a> <b> [mobile]` | Two runs side by side beyond the score: requests, bytes, CSS/JS, unminified code |
| `node tools/agent-view.mjs <url> …` | What an agent without JavaScript sees: title, description, headings, JSON-LD, text |
| `node tools/seed-headless.mjs` | Creates the *Coffee* object and entries for the headless bonus |
| `npm run replica` | Static red (:8101) and green (:8102) copies of the page, no Liferay needed |

## What's seeded, and where it lives

| Gap | Seeded in | Fixed with |
|---|---|---|
| Developer mode + no compression | `docker/profiles/red/portal-ext.properties` | `docker-compose.green.yml` override (production defaults + `GZipFilter=true`). Done last, in Stage 3 (guide 3.1) |
| Static assets not compressed or edge-cached | `GZipFilter` only covers the portal filter chain | Local CDN edge `docker/cdn/nginx.conf` on :8081 + Instance Settings → Platform → Instance Configuration → General → CDN Host (guide 3.2) |
| 4.4 MB hero and 1.6 MB card images inserted by URL (no Adaptive Media) | `layouts/1_home/page-definition.json` | Page Editor → Image Source: Documents and Media + Adaptive Media resolutions |
| 18 render-blocking web fonts, `display=block` | `layout-set/public/css.css` | Pages ⚙ → Design → CSS, then the *Kaffora Brand Fonts* CSS client extension |
| Tag soup: long task, unused libraries, injected banner, permission prompts, paste blocker, console error | `layout-set/public/js.js` | Pages ⚙ → Advanced → JavaScript, then the *Kaffora Tags* JavaScript client extension |
| Low-contrast brand colours | `style-books/kaffora-brand-v1` | Style Book tokens or *Kaffora Accessible* |
| Missing alt text, icon buttons/links without names, input without label | fragment defaults | Page Editor → Image Description / fragment Configuration |
| Heading jump h1 → h4 | Home page definition | Heading fragment → Heading Level |
| `noindex, nofollow`, no meta description | `layouts/1_home/page.json` | Page → Configure → SEO |
| Invalid robots.txt | `layout-set/public/metadata.json` | Pages ⚙ → Advanced → Robots |
| "Read more" / "click here" links | fragments' editable text | Page Editor inline edit |
| Broken llms.txt (no H1, no links) | `site-settings.json` | Site Settings → SEO → llms.txt |
## Fix pack

[`fixes/`](fixes/) holds every change, ready to import or paste, in checkpoint order: the fragment collection with the LCP switch, the importable accessible Style Book, robots.txt, page SEO values, the CSP policy, `llms.txt` and the Claude Desktop MCP config. Use it to rehearse quickly or to catch up during the session.

## Rebuilding

```bash
cd liferay/build-tools
python3 gen_images.py     # optional: regenerate the procedural images
python3 build.py          # writes liferay/site-initializer/ and docker/deploy/kaffora-site-initializer.jar

cd ../../client-extensions
python3 build.py          # writes dist/kaffora-cx.zip and copies it into both Docker profiles
```

## Troubleshooting

The most common issues, all covered in the [guide's troubleshooting table](docs/WORKSHOP-GUIDE.md#troubleshooting):

- `Cannot find module …tools\tools\lh.mjs`: run the tools from the repository root, not from `tools/`.
- `llms.txt` returns an HTML redirect: the virtual host must be exactly `kaffora.localhost`.
- Liferay breaks after changing the image tag: a database upgraded by a newer DXP can't go back; `docker compose down -v` and start over.
- Saving **CDN Host** fails silently: use `http://127.0.0.1:8081`; Liferay's URL validator rejects `*.localhost` hosts.
- Mobile Performance far below desktop: expected under simulated slow 4G; check that cards use **Card-400** in every Page Editor viewport.

## Notes and known limits

- **Runs on Liferay DXP Free Tier** (`liferay/dxp:2026.q3.0`, the initial quarterly release the Free Tier covers; override with `LIFERAY_TAG`). No Enterprise-only module is used. The Free Tier is for learning, development and small-scale use under its own EULA.
- The site template is a resource-only OSGi **site initializer**, the same mechanism Liferay's own templates use. The client extension archive is built without Gradle, in the format Liferay Workspace produces.
- `llms.txt` (`LPD-80518`, beta) and the MCP Server (`LPD-63311`) are enabled through portal properties in both profiles. Check **Instance Settings → Feature Flags** on your build.
- Menu paths were checked for 2026.Q3. Labels can move between quarterly updates: if one differs, look in the same area.

## License

Code and documentation: [MIT](LICENSE). Fonts: SIL Open Font License 1.1. See [NOTICE.md](NOTICE.md).

Kaffora Coffee is a fictional brand. This is a community workshop kit, not an official Liferay product; Liferay DXP itself is licensed separately by Liferay, Inc.
