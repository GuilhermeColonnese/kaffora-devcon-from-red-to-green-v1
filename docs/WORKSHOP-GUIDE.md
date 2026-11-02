# From Red to Green — Workshop Guide

**Improving SEO, Accessibility, Performance and Agentic Browsing scores with Liferay DXP**
Liferay DevCon 2026 · 40-minute build-along · Liferay DXP Free Tier 2026.Q3 · Lighthouse 13.5

> Kaffora Coffee is a fictional brand created for this workshop.
> Menu paths were checked against Liferay Learn for 2026.Q3. Labels can move slightly between quarterly updates, so if a label differs, look in the same area.

---

## The rules of the game

1. **Native levers first, code where it makes the right thing easy.** Most fixes are DXP configuration: Instance/Site Settings, Page settings, Style Books, Adaptive Media, fragment configuration, portal properties. When code is the answer, it lives in governed places: a fragment (with an author-facing option) or a client extension. Never in a free-text field.
2. **Measure like a crawler.** Always run Lighthouse **logged out** (Incognito window or the CLI). The admin Control Menu adds JavaScript that visitors never load.
3. **Same conditions, twice.** Mobile form factor, simulated throttling, same URL, same machine. Run 3 times and keep the median when you present numbers.

## Session timeline (40 min)

| Time | Stage | What happens |
|---|---|---|
| 00–06 | Concepts (slides) | Lighthouse 13 insights, the 5 categories, how Agentic Browsing is scored |
| 06–10 | **Stage 1: Baseline** | Everyone runs Lighthouse and writes down the red scores |
| 10–31 | **Stage 2: Fix the content in Liferay** | Performance → Accessibility → SEO → Best Practices → Agentic Browsing, then measure `content` |
| 31–36 | **Stage 3: The last mile** | Server profile + local CDN (Liferay restarts while we talk about layers), then `final` and the 3-column scoreboard |
| 36–40 | Wrap-up | Who owns what (SEO matrix), takeaways, checklist, Q&A. Bonus if ahead: headless SSR vs CSR |

---|---|---|
| 00–06 | Concepts (slides) | Lighthouse 13 insights, the 5 categories, how Agentic Browsing is scored |
| 06–10 | **Stage 1: Baseline** | Everyone runs Lighthouse and writes down the red scores |
| 10–12 | Architecture fix | Presenter swaps the Docker profile (Liferay restarts, about 2–3 min) and reads the report with the room |
| 12–32 | **Stage 2: Fix** | Performance → Accessibility → SEO → Best Practices → Agentic Browsing |
| 32–37 | **Stage 3: Re-run** | Lighthouse again, then the scoreboard |
| 37–40 | Wrap-up | Checklist handout, Q&A |

---

## Stage 0 — Setup (do this before the session)

Every command in this guide runs the same way on **macOS, Windows and Linux**, except where a table shows one variant per system. On Windows, use **PowerShell** (Windows Terminal). The full cheat sheet is in the [appendix](#appendix--command-cheat-sheet-by-os).

**You need:**

| | macOS | Windows 10/11 | Linux |
|---|---|---|---|
| Docker (8 GB RAM for containers) | Docker Desktop | Docker Desktop with the WSL 2 backend | Docker Engine + Compose plugin, or Docker Desktop |
| Node.js 22+ | `brew install node@22` | `winget install OpenJS.NodeJS.LTS` | `nvm install 22` (or your distro's package) |
| Google Chrome | `brew install --cask google-chrome` | `winget install Google.Chrome` | `google-chrome-stable` package from google.com/chrome |
| Liferay DXP **Free Tier** activation key (free) | `.xml` file | `.xml` file | `.xml` file |

> **Memory:** give Docker at least 8 GB. macOS and Windows: Docker Desktop → Settings → Resources. Windows with WSL 2: set `memory=8GB` under `[wsl2]` in `%UserProfile%\.wslconfig`, then run `wsl --shutdown`.

> **Everything in this workshop runs on Liferay DXP Free Tier.** Get your key once (free, about 2 minutes):
> 1. Sign in or create an account at **marketplace.liferay.com/p/liferay-dxp-free-tier** → **Get Activation Key**.
> 2. Domain: **`localhost`** (allowed for local development). The key is valid for 12 months.
> 3. The Free Tier covers the **initial release of each quarter**, so the kit uses `liferay/dxp:2026.q3.0`. To try another quarterly build: `LIFERAY_TAG=2026.q3.x docker compose up -d` (PowerShell: `$env:LIFERAY_TAG="2026.q3.x"`).
>
> Nothing here needs an Enterprise-only module (AI Hub, SAML/MFA, Search Blueprints, Analytics Cloud). The beta switches used in 2.5, `llms.txt` (`LPD-80518`) and the MCP Server (`LPD-63311`), are turned on by the kit's portal properties; check they're listed in **Control Panel → Instance Settings → Feature Flags** on your build during the dry run.

1. Install the workshop tools once, from the kit folder (same on every OS):
   ```bash
   npm install
   ```
2. Copy your Free Tier activation key into `docker/deploy/`. `kaffora-site-initializer.jar` is already there. The client extensions used in 2.1b and 2.1c (`kaffora-cx.zip`) ship inside both Docker profiles (`profiles/*/osgi/client-extensions/`), so Liferay installs them on every start. They do nothing until you attach them to the pages.

   | macOS / Linux | Windows (PowerShell) |
   |---|---|
   | `cp ~/Downloads/activation-key-*.xml docker/deploy/` | `Copy-Item $HOME\Downloads\activation-key-*.xml docker\deploy\` |

3. Start the **red** environment (same on every OS):
   ```bash
   cd docker
   docker compose up -d
   docker compose logs -f liferay    # wait for "Server startup in [...] milliseconds", then Ctrl+C
   ```
4. Sign in at `http://localhost:8080` (`test@liferay.com` / `test`, then set a new password).
5. Create the site: **Global Menu → Control Panel → Sites → Add (+)** → choose **Kaffora Coffee (DevCon red)** → name it `Kaffora Coffee`.
6. Give the site its own host name: **Site Menu → Configuration → Site Settings → Site URL → Virtual Hosts (Public Pages)** → `kaffora.localhost`.
   Chrome resolves every `*.localhost` name to your machine on all three systems, so no hosts-file edit is needed. The site-level `llms.txt` and `robots.txt` are served per virtual host.
7. Open `http://kaffora.localhost:8080/` in an Incognito window. You should see the Kaffora home page. Check that `llms.txt` returns two short lines:

   | macOS / Linux | Windows (PowerShell) |
   |---|---|
   | `curl http://kaffora.localhost:8080/llms.txt` | `curl.exe http://kaffora.localhost:8080/llms.txt` |

   On Windows type `curl.exe`, not `curl`: in Windows PowerShell 5, `curl` is an alias for `Invoke-WebRequest`. Opening the URL in Chrome works everywhere too.

> **Plan B (no Liferay available):** `replica/` contains a static copy of the page in both states. Run `npm run replica` (or `node replica/server.mjs`) and use `http://localhost:8101/` (red) and `http://localhost:8102/` (green).

---

## Stage 1 — Baseline: record the red state (4 min)

**Option A: Chrome DevTools.** Open the page in Incognito → DevTools (`Cmd+Option+I` on macOS, `F12` on Windows and Linux) → **Lighthouse** → Mode *Navigation*, Device *Mobile* (then again with *Desktop*), select all categories (including **Agentic Browsing**) → *Analyze page load*.

**Option B: CLI (recommended, same numbers for everybody, same command on every OS):**
```bash
node tools/lh.mjs baseline http://kaffora.localhost:8080/
```
It runs **mobile and desktop** one after the other (about 1–2 minutes) and saves `reports/baseline-mobile.report.html|json` and `reports/baseline-desktop.report.html|json`. It uses the same Lighthouse engine as PageSpeed Insights, pinned to 13.5.0.

- Only one form factor: `node tools/lh.mjs baseline http://kaffora.localhost:8080/ mobile` (or `desktop`)
- Open the HTML reports when done: add `--open`
- Chrome not found: set `CHROME_PATH` (see the [appendix](#appendix--command-cheat-sheet-by-os))

Write your scores down:

| Category | Baseline mobile | Baseline desktop | Final mobile | Final desktop |
|---|---|---|---|---|
| Performance | | | | |
| Accessibility | | | | |
| Best Practices | | | | |
| SEO | | | | |
| Agentic Browsing (passed/total) | | | | |

**Reference run (Liferay DXP Free Tier 2026.Q3.0, red profile, Lighthouse 13.5):**

| | Performance | Accessibility | Best Practices | SEO | Agentic | LCP | TBT | CLS | FCP |
|---|---|---|---|---|---|---|---|---|---|
| Mobile | 24 | 81 | 77 | 38 | 0/3 | 61.9 s | 2,430 ms | 0.102 | 10.7 s |
| Desktop | 43 | 81 | 81 | 38 | 1/3 | 10.6 s | 550 ms | 0.045 | 1.8 s |

Desktop scores higher on Performance because it has no mobile CPU and network throttling. Its layout shift (0.045) stays under the CLS threshold, so one agentic check already passes, and `notification-on-start` does not fire, so Best Practices is 81 instead of 77. Your numbers will vary by a few points from laptop to laptop: what matters is the list of failing audits, which should match.

### How to read the report in Lighthouse 13

- **Performance** now lists **insights** (the same ones DevTools' Performance panel shows) instead of the old opportunity audits. Expect `render-blocking-insight`, `image-delivery-insight`, `cache-insight`, `document-latency-insight`, `lcp-discovery-insight`, `cls-culprits-insight`, `font-display-insight` and `network-dependency-tree-insight`.
- **Agentic Browsing** isn't a 0–100 gauge. It shows **how many readiness checks pass**. Three checks count: `agent-accessibility-tree`, `cumulative-layout-shift` and `llms-txt`. The WebMCP checks and the new `ard-schema` (`ai-catalog.json`) check are informational, and they only apply when the feature is present.
- A **missing** `llms.txt` returns 404 and the check becomes *Not applicable*. That's why the red site ships a **broken** one (no H1, no links, too short), so the check fails for real.

---

## Stage 2 — Fix it with native Liferay DXP

Stage 2 runs on the **red server** on purpose: every fix here is content and authoring, done by the people who own the site. The server and the edge come last, in Stage 3.

### 2.1 Performance (6 min, with live code)

**a) Serve the images through Adaptive Media (the LCP element first)**
The images were inserted **by URL**, so Liferay renders a plain `<img>` pointing at the originals (the roastery image is 4000 px, 4.4 MB). Adaptive Media only applies to images selected from Documents and Media.

1. **Control Panel → Configuration → Adaptive Media → Add**, three resolutions (Max Width only):
   - `Card-400` → 400 · `Mobile-760` → 760 · `Desktop-1600` → 1600
   - Then ⋮ at the top of the list → **Adapt All Images**.

   > **The 2× trap.** Adaptive Media treats any resolution that is exactly twice another (±1 px) as its **high-density version** and adds it as `2x` in the same `<picture>` source. With `Mobile-800` + `Desktop-1600`, every phone with a DPR above 1 (Lighthouse mobile uses 1.75) downloads the **1600 px** file. Pick widths that aren't exact doubles (400 / 760 / 1600), or use the *High resolution* option on purpose.
2. Open **Home** in the Page Editor (✏️). Select the roastery image → Image Source **Direct** → pick `hero-coffee-4k.jpg` **from Documents and Media** (not by URL). Keep Resolution **Auto** and keep it **eagerly loaded** (never lazy-load the LCP image).
3. **Live code (the DevCon moment): give authors an LCP switch.** Lighthouse still flags *fetchpriority=high should be applied*. Liferay's image editable has no priority option, so we add one to the fragment, once, for every author:
   **Design → Fragments → Kaffora Coffee → Kaffora Hero → Edit.**
   - **Configuration** tab first (the HTML reads this field): paste
     ```json
     {
       "fieldSets": [{
         "label": "Performance",
         "fields": [{
           "name": "imagePriority",
           "label": "Roastery image priority (fetchpriority)",
           "description": "Set High only on the LCP image (the largest image above the fold).",
           "type": "select",
           "dataType": "string",
           "defaultValue": "auto",
           "typeOptions": {"validValues": [
             {"label": "Auto", "value": "auto"},
             {"label": "High (LCP image)", "value": "high"}
           ]}
         }]
       }]
     }
     ```
   - Then the **Code** tab, HTML: add one attribute to the roastery image. `!'auto'` is FreeMarker's default operator: the preview never breaks, even before the field exists
     ```html
     <img class="kaffora-hero__img"
          data-lfr-editable-id="hero-image"
          data-lfr-editable-type="image"
          fetchpriority="${configuration.imagePriority!'auto'}"
          src="…" />
     ```
   - **Publish**, then propagate to the pages that use it (**⋮ → View Usages → Propagate**, or confirm the propagation prompt).
   - Back in the Page Editor: select the hero → **Configuration → Roastery image priority → High (LCP image)** → Publish.

   **Talk track:** "A dozen lines of JSON and one attribute. From now on the author picks the LCP image from a dropdown: no developer, no ticket, no guessing."
4. The three product cards: same, from Documents and Media, **Enable Lazy Loading** on (they're below the fold), and **Resolution → Card-400**. The cards are small on every screen, so a fixed small rendition beats a viewport-based one. The Resolution is set **per viewport**: switch the Page Editor to the mobile viewport (device icons in the top bar) and set Card-400 there too, otherwise phones still get the Auto rendition (`mobile-760`).

Liferay now outputs a `<picture>` element with one `<source>` per resolution (`max-width` media queries) and a `data-fileentryid`, so each device downloads the rendition that fits.

**b) Brand fonts, the governed way: a CSS client extension**
The agency pasted an `@import` of **18 Google Fonts files with `display=block`** into the page set's CSS field: render-blocking, a third-party connection on the critical path, invisible text while it loads.

1. **Site Menu → Site Builder → Pages → ⚙ (Public Pages configuration) → Design → CSS** field: delete the `@import`.
2. Same **Design** screen → **CSS Client Extensions → Add CSS Client Extensions** → select **Kaffora Brand Fonts** → Save.
3. **Design → Style Books → Kaffora Accessible → Typography** (you switch to it in 2.2a): put the brand families first, keeping the system stack as fallback:
   - Font Family Base and Sans Serif: `'Source Sans 3', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`
   - Font Family Monospace: `'JetBrains Mono', ui-monospace, Menlo, Consolas, monospace`

What the client extension ships (`client-extensions/kaffora-cx/static/kaffora-brand-fonts.css`): **3 self-hosted woff2 files, latin subset, about 53 KB** (instead of 18 files from a third party), declared with `font-display: optional`, so text is never invisible and the font never causes a layout shift. Served by Liferay at `/o/kaffora-cx/…`, versioned in Git, attached per site.

> `optional` means a cold, slow first visit may keep the system font; the next page uses the brand font from cache. If the brand must always show, switch to `swap` and accept a possible small shift.

**c) Replace the "tag soup" with a JavaScript client extension**
Same configuration screen → **Advanced → JavaScript**. Read the snippets out loud, then delete them all:

| Snippet | Lighthouse finding |
|---|---|
| 600 ms synchronous "fingerprinting" loop | TBT, long main-thread tasks |
| jQuery 1.12, Moment and Lodash loaded from cdnjs, never used | unused/legacy JavaScript, third parties |
| Promo bar inserted at the top after 1.5 s | `cumulative-layout-shift`, `cls-culprits-insight` |
| Geolocation and notification prompts on load | `geolocation-on-start`, `notification-on-start` |
| Paste blocked on e-mail fields | `paste-preventing-inputs` |
| `window.legacyTracker.track()` | `errors-in-console` |

Then bring back what marketing actually needed, governed: **Design → JavaScript Client Extensions → Add JavaScript Client Extensions** → **Kaffora Tags** → load **In Page Bottom** → Save.

`kaffora-tags.js` (~1 KB, no dependencies) keeps the legitimate part, a `dataLayer` with page views and CTA clicks, and drops everything else: loaded `async` at the bottom, work deferred to `requestIdleCallback`, respects Do Not Track and Global Privacy Control, no permission prompts, no DOM injection (a promo banner is a fragment, with reserved space), no input hijacking. A free-text field has no review, no version and no owner; a client extension has all three.

**Talk track:** "We didn't ban JavaScript or fonts. We moved them from a text box anyone can paste into, to an artifact that's reviewed, versioned and attached on purpose."

Click **Publish** on the page whenever you finish a round of Page Editor changes.

### 2.2 Accessibility (4½ min)

**a) Contrast through the Style Book (one click, whole site)**
**Site Menu → Design → Style Books.** Two options:

- *Live, to show the concept:* edit **Kaffora Brand v1** → Color System → set **Primary** `#C2107F` (button pink), **Secondary** `#C7C9EA` (muted text) and **Brand Color 1** `#FF5CCB` (labels, prices, links) → watch the preview update → Publish.
- *Fast path:* on **Kaffora Accessible (WCAG AA)**, open ⋮ → **Mark as Default**. It already has AA colours and system font stacks.

The site follows the DevCon 2026 look (navy canvas, purple-magenta gradients, pink buttons). The red brand kit used a pastel pink `#FF8ADF` behind white button text (2.1:1), and dim purples for labels and body text on navy (2.3–3.3:1). The WCAG AA minimum for normal text is 4.5:1. The accessible palette scores 5.7:1 (buttons), 7.1:1 (labels) and 12:1 (muted text).

> **Why three tokens?** One colour can't be both a button background under white text *and* readable text on navy. So the Style Book splits the brand pink into *Primary* (dark enough for white text) and *Brand Color 1* (light enough for navy).

**b) Accessible names in the Page Editor (no HTML edits)**

| Element | Where | Value |
|---|---|---|
| Logo | select image → **Image Description** | `Kaffora Coffee home` |
| Search icon button | Kaffora Header → Configuration → *Search button accessible name* | `Search coffees` |
| Cart icon button | same → *Cart button accessible name* | `Open cart` |
| Navigation landmark | same → *Navigation landmark label* | `Main` |
| Roastery image (under the hero) | select → **Image Description** | `Latte in a white cup on a wooden table` |
| Card images | select → **Image Description** | one short sentence each |
| Social icons | Kaffora Footer → Configuration | `Kaffora Coffee on Instagram`, … |
| Newsletter input | Kaffora Newsletter → Configuration → *E-mail field label* | `E-mail address` |

> **Teaching moment:** an **empty** `alt=""` passes `image-alt` because it marks the image as decorative. Here the images have **no** `alt` at all, so they fail. Author intent matters, and the Page Editor is where authors express it.

**c) Heading order**
Select *This week's roasts* → Configuration → **Heading Level: H2** (it was H4 right after the H1).

### 2.3 SEO (3½ min)

**a) Page SEO:** **Site Builder → Pages → Home ⋮ → Configure → SEO**

- **HTML Title:** `Specialty coffee beans, roasted weekly | Kaffora Coffee`
- **Description:** `Single-origin specialty coffee from Brazil, Ethiopia and Colombia, roasted every Monday and delivered in 48 hours.`
- **Robots:** delete `noindex, nofollow`. The page was left with a staging directive, which is the most expensive SEO bug there is.
- Leave **Canonical URL** at the default. Liferay emits an absolute canonical on the virtual host. Use a custom canonical only for real duplicates.

**b) robots.txt:** **Pages → ⚙ → Advanced → Robots**. Replace the invalid content with:
```
User-Agent: *
Disallow:

Sitemap: [$PROTOCOL$]://[$HOST$]:[$PORT$]/sitemap.xml
```
Liferay replaces the `[$…$]` placeholders per virtual host. Check `http://kaffora.localhost:8080/robots.txt` and `/sitemap.xml`.

**c) Descriptive link text:** in the Page Editor, change each card's *Read more* to `Shop Cerrado Mineiro`, `Shop Yirgacheffe` and `Shop Huila`. In the footer, change "click here" to `Read our privacy policy`.

**d) Beyond Lighthouse (show, 30 s):**

- **Friendly URLs:** the virtual host already removed `/web/kaffora/`.
- **Site Menu → Configuration → Redirection:** create `/summer-sale-2025` → `/coffees` (301) and look at the 404 tracking.
- **Instance Settings → SEO → XML Sitemap:** choose which content types to include. In 2026.Q3 you can also schedule cached generation.
- **Instance Settings → Pages → SEO:** canonical URL strategy and hreflang for translated pages only.

### 2.4 Best Practices (1½ min)

Removing the tag soup (2.1c) already fixed `geolocation-on-start`, `notification-on-start`, `paste-preventing-inputs` and `errors-in-console`. Now harden the headers:

**Control Panel → Instance Settings → Security → Content Security Policy**

- Enable it with a nonce-based policy and keep **Report Only** checked during the workshop:
  ```
  default-src 'self'; script-src 'self' '[$NONCE$]' 'strict-dynamic'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; base-uri 'self'; frame-ancestors 'self'
  ```
- Lighthouse shows `csp-xss`, `has-hsts`, `origin-isolation` and `clickjacking-mitigation` under *Trust and Safety*. They're **unscored**, but they're what security teams read. HSTS and COOP belong on the reverse proxy or CDN. Liferay SaaS and PaaS set them at the edge.

### 2.5 Agentic Browsing + MCP (3½ min)

**a) llms.txt (native, 2026.Q3 beta):** **Site Menu → Configuration → Site Settings → SEO → llms.txt.** Keep *Enable llms.txt* checked and replace the content:
```markdown
# Kaffora Coffee

> Kaffora Coffee is a (fictional) specialty roaster selling single-origin beans and subscriptions, roasted every Monday and delivered within 48 hours.

## Coffees

- [All coffees](http://kaffora.localhost:8080/coffees): every coffee with tasting notes and price
- [Brazil Cerrado Mineiro](http://kaffora.localhost:8080/coffees): 250 g, from €14
- [Ethiopia Yirgacheffe](http://kaffora.localhost:8080/coffees): 250 g, from €18
- [Colombia Huila](http://kaffora.localhost:8080/coffees): 250 g, from €16

## Help

- [Newsletter](http://kaffora.localhost:8080/#newsletter): new roasts by e-mail
- [Sitemap](http://kaffora.localhost:8080/sitemap.xml): full list of public pages
```
The feature flag `LPD-80518` is already on in both Docker profiles.

**b) Agent-centric accessibility tree:** fixed by 2.2. Agents read the same accessibility tree as screen readers. An icon button with no name is invisible to both.

**c) Layout stability:** fixed by removing the injected promo bar in 2.1c. If marketing needs a banner, add it as a fragment in the page (its space is reserved at render time), or use the native cookie banner (**Instance Settings → Cookies**), which is an overlay and doesn't shift content.

**d) Bonus: WebMCP (informational, weight 0):** Kaffora Newsletter → Configuration → **Expose this form to AI agents** ✓. The form now carries `toolname`, `tooldescription` and `toolparamdescription`, following the WebMCP declarative API. The WebMCP audits only become applicable in a Chrome build with WebMCP enabled.

**e) Structured data (validated outside Lighthouse):** drag **Schema.org JSON-LD (Organization)** from the *Kaffora Coffee* fragment collection onto the page (or onto a Master Page for every page), set Name and URL, then Publish. Validate the snippet at validator.schema.org. On Display Page Templates, map the same fields to content structures so every article gets its own JSON-LD.

**f) The server side of agentic: Liferay as an MCP server (the WOW moment)**
**Control Panel → Instance Settings → Platform → MCP Server → Enabled → Save.** Endpoint: `http://localhost:8080/o/mcp`.
Connect an MCP client. Liferay Learn shows a direct HTTP configuration (`"type": "http"`, `"url"`, `"headers"`) for clients that support it. For Claude Desktop, use the `mcp-remote` bridge:
```json
{
  "mcpServers": {
    "liferay": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8080/o/mcp", "--header", "Authorization:${AUTH_HEADER}"],
      "env": { "AUTH_HEADER": "Basic <base64 user:password>" }
    }
  }
}
```
Build the Basic auth value for your user (replace `user@example.com:password`):

| macOS / Linux | Windows (PowerShell) |
|---|---|
| `printf '%s' 'user@example.com:password' \| base64` | `[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('user@example.com:password'))` |

The Claude Desktop config file lives in `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS and `%APPDATA%\Claude\claude_desktop_config.json` on Windows. Restart Claude Desktop after editing it.

Demo prompt: *"List the pages of the Kaffora Coffee site and tell me which ones are missing an SEO description."* The agent works with **your user's permissions**, so use a dedicated low-privilege user outside workshops.

### 2.6 Measure the content (1 min)

```bash
node tools/lh.mjs content http://kaffora.localhost:8080/ mobile
```
Everything in Stage 2 was content and authoring, still on the red server. Expect Accessibility, Best Practices, SEO and Agentic at or near the top, and Performance far better but not green yet: the server still serves unminified, uncompressed, uncached assets. That's the last mile.

---

## Stage 3 — The last mile: server and edge, then re-run (5 min)

Same commands on every OS. Run the swap **first** and talk while Liferay restarts.

### 3.1 The server (presenter, 30 s + restart)

**The setup:** when a site is slow, the first thing everybody blames is the server. The red profile gives them a real reason: it includes `include-and-override=portal-developer.properties` (the classic "dev config reached production") and nothing is compressed, because Liferay's `GZipFilter` is **off by default**.

**Fix the server:** go back to production defaults, turn on `GZipFilter=true`, start the local CDN, restart.
```bash
cd docker
docker compose -f docker-compose.yml -f docker-compose.green.yml up -d liferay cdn
docker compose logs -f liferay        # ~2–3 min; data is kept in the volumes
```
Identical on macOS, Windows and Linux: the override swaps the mounted `profiles/red` for `profiles/green` and starts a local CDN edge (Nginx) on port 8081, used in 3.2. Back to red later: clear the CDN Host field (3.2) and run `docker compose up -d --remove-orphans liferay`.

**Talk track while it restarts (2–3 min):** the three layers slide. Who owns what: infrastructure, the Liferay DXP application, development and third parties. Then the server myth, with the numbers from the dry run below.

**The server myth (dry run, not live):** if you fix only the server, on the red content, nothing moves. Measured once in the dry run:
```bash
node tools/lh.mjs arch http://kaffora.localhost:8080/ mobile
node tools/compare.mjs baseline arch mobile
```

**Reference dry run (Liferay DXP 2026.Q3, mobile, server only, before any content fix):**

| | baseline | arch |
|---|---|---|
| Performance | 25 | 25 |
| LCP | 63.4 s | 61.6 s |
| TBT | 2,407 ms | 2,350 ms |
| Transferred | 11,261 KiB | 10,932 KiB |
| JS | 1,114 KiB | 930 KiB |
| Unminified JS | 11 KiB | 0 KiB |
| Images | 9,109 KiB | 9,109 KiB |

The server got cleaner (minified JS, cache headers, compressed HTML) and **the score didn't move**. Liferay 2026 ships its frontend pre-built and minified, so developer mode costs far less than it used to. 81% of the bytes were images, and the TBT came from third-party tags: both **content and authoring** decisions. That's why the workshop fixes the content first and the server last.

**One more piece of evidence (DevTools → Network → CSS, *Disable cache* on, Content-Encoding column):** the dynamic responses (`main.css?plid=…`, `combo?…`) come back `gzip`, but `clay.(hash).css` arrives **724 kB uncompressed** and the theme `main.(hash).css` 84.5 kB. `GZipFilter` only compresses what flows through the portal's filter chain; static bundle resources don't. Compressing them is the web server's or the CDN's job, which is exactly why the filter is off by default.

**Line for the room:** "Fixing the server is necessary, not sufficient. And the last 724 kB is not the server's job either."

### 3.2 Put a CDN in front (presenter, 1–2 min)

The green override already started **`cdn`**: an Nginx edge on `:8081` that pulls from Liferay (origin pull), compresses static assets, caches them and adds `X-Cache: MISS/HIT`. Config: `docker/cdn/nginx.conf`. It simulates what a CDN does to the bytes; it can't simulate geographic proximity on `localhost`.

1. Check the edge: open `http://kaffora.localhost:8081/__cdn` → `kaffora-edge ok`.
2. **Control Panel → Instance Settings → Platform → Instance Configuration → General → CDN Host HTTP** = `http://127.0.0.1:8081` · keep **Enable CDN Dynamic Resources** on · Save.
   - Use the **IP**, not a `*.localhost` name: Liferay validates the field with Apache Commons `UrlValidator`, which rejects local TLDs such as `.localhost` and fails with a generic *"Your request failed to complete"* (nothing in the logs). In production this is your CDN's public hostname.
   - The fields are on the **General** tab of Instance Configuration (Liferay Learn calls it *Virtual Instance Scope → General*). If your build doesn't show them, use the portal properties instead: uncomment the three `cdn.*` lines in `docker/profiles/green/portal-ext.properties` and run the green command again.
3. Reload the site (`:8080`) with DevTools → Network → CSS, *Disable cache* on. Add the **Domain**, **Content-Encoding** and a custom **X-Cache** column (right-click the header → Response Headers → Manage Header Columns).
   - `clay.(hash).css` now comes from `127.0.0.1:8081`, `gzip`, ~90 kB instead of 724 kB.
   - First load `X-Cache: MISS`, reload → `HIT`: the edge served it without touching Liferay.
4. (Dry run) measure the edge alone:
   ```bash
   node tools/lh.mjs cdn http://kaffora.localhost:8080/ mobile
   node tools/compare.mjs arch cdn mobile
   ```

**Reference dry run (red content, server + edge, `node tools/compare.mjs arch cdn mobile`):**

| | arch | cdn |
|---|---|---|
| Performance | 25 | 33 |
| FCP | 9.1 s | 4.2 s |
| LCP | 61.6 s | 53.0 s |
| TBT | 2,350 ms | 2,427 ms |
| Transferred | 10,932 KiB | 9,758 KiB |
| CSS | 799 KiB | 106 KiB |
| JS | 930 KiB | 448 KiB |
| Images | 9,109 KiB | 9,109 KiB |

The edge did its job: CSS −87%, JS −52%, FCP −5 s. On the red content TBT (third-party tags) and LCP (9 MB of images) didn't move; after Stage 2 they're gone, so the edge is what takes the page the last mile.

**Watch Best Practices:** with the CDN Host set, static assets come from a second origin (`127.0.0.1:8081`), and Lighthouse may flag `inspector-issues` (cross-origin warnings such as the SVG `<use>` one Liferay documents): Best Practices went 77 → 73 in the dry run. Open the report's *Issues were logged* audit to see the exact one. On stage, show the CDN Host screen (A) for the story; for the `final` run use **B**: clear the CDN Host and test `http://kaffora.localhost:8081/`, so everything is same-origin and still compressed by the edge.

**Two ways to put the edge in front, compare them in your dry run:**

| | A. CDN Host (native Liferay setting) | B. Full-site edge |
|---|---|---|
| Lighthouse URL | `http://kaffora.localhost:8080/` | `http://kaffora.localhost:8081/` |
| Liferay setting | CDN Host HTTP = `http://127.0.0.1:8081` | none |
| What goes through the edge | static resources only (rewritten to the CDN host) | everything; pages compressed, never cached |
| Trade-off | shows the product screen; one extra origin, so one extra connection in Lighthouse | same origin, usually a bit faster; like a full-site CDN (Cloudflare-style) |

Show A on stage (it's a Liferay screen, not a container). If B scores clearly better in your dry run, run the `final` measurement on `:8081` and say so.

> **In production:** compress (gzip/Brotli) and cache at the CDN with origin pull, and point **CDN Host HTTP / HTTPS** at it. Liferay SaaS and PaaS include an integrated CDN. Never ship `portal-developer.properties`. Real CDN gains (latency by geography) only show in field data (CrUX / PageSpeed Insights), not on `localhost`.

**Line for the room:** "Content first, then the server, then the edge. Each layer owns its part of the score."

### 3.3 Re-run and compare

```bash
node tools/lh.mjs final http://kaffora.localhost:8080/ mobile
node tools/scoreboard.mjs baseline content final --open
```
The scoreboard (`reports/scoreboard.html`) shows **baseline → content → final** for every category, with a **Mobile / Desktop** switch when both form factors exist for all three runs. `--open` opens it in your default browser on every OS. With only two runs: `node tools/scoreboard.mjs baseline final --open`.

If the dry run showed `inspector-issues` from the CDN host (see 3.2), run `final` with option B instead: clear the CDN Host and use `http://kaffora.localhost:8081/`.

**Reference run (red measured on Liferay; green from the replica until the final Liferay dry run):**

| Category | Mobile red | Mobile green | Desktop red | Desktop green |
|---|---|---|---|---|
| Performance | 24 | 100 | 43 | 100 |
| Accessibility | 81 | 100 | 81 | 100 |
| Best Practices | 77 | 100 | 81 | 100 |
| SEO | 38 | 100 | 38 | 100 |
| Agentic Browsing | 0/3 | 3/3 | 1/3 | 3/3 |
| LCP | 61.9 s | 1.4 s | 10.6 s | 0.5 s |
| Page weight | 11,169 KiB | 128 KiB | 11,169 KiB | 327 KiB |

Desktop downloads bigger Adaptive Media renditions than mobile, which is why its green page weight is higher: that is `srcset` doing its job.

If Performance on Liferay lands in the 80s–90s instead of 100, that's expected on a laptop running Docker. Point out the **deltas and the insights that disappeared**, not the absolute number.

---

## Bonus — Headless: same content, two renderings (3 min, if you're ahead)

The SEO responsibility matrix has a **Full headless** column. This shows why: with your own front, rendering is your job, and Lighthouse alone won't tell you when you got it wrong.

`headless/server.mjs` is a small Node front (no framework, no build, works offline) that reads the **same Liferay content** through a BFF (`/api/coffees` → Liferay Objects `GET /o/c/coffees`) and renders it two ways with the **same code** (`headless/public/render.mjs`):

| | `/ssr` | `/csr` |
|---|---|---|
| Where the HTML is built | on the server | in the browser (empty shell + `app.js`) |
| What the first response contains | the whole page, meta, JSON-LD | `<div id="app">Loading…</div>` |

**Setup (once, in the dry run):**
```bash
# optional: create the Coffee object + 3 entries in Liferay (falls back to local JSON if skipped)
LIFERAY_AUTH="test@liferay.com:yourpassword" node tools/seed-headless.mjs      # macOS / Linux
$env:LIFERAY_AUTH="test@liferay.com:yourpassword"; node tools/seed-headless.mjs # Windows PowerShell
```
If the seed fails on your build, create it by hand: **Control Panel → Objects → +**, name `Coffee`, fields `name`, `origin`, `notes` (long text), `price` (integer), `weight`, `image`, **Publish**, and add the entries from `headless/data/coffees.json`.

**Live:**
```bash
node headless/server.mjs                     # same LIFERAY_AUTH as above; http://localhost:8090/
node tools/lh.mjs h-ssr http://localhost:8090/ssr mobile
node tools/lh.mjs h-csr http://localhost:8090/csr mobile
node tools/agent-view.mjs http://localhost:8090/csr http://localhost:8090/ssr
```
The footer of both pages says where the data came from (`Liferay Objects · /o/c/coffees` or `local fallback`).

**What you'll see (reference run on the kit):**

| | SSR | CSR |
|---|---|---|
| Lighthouse (mobile) | 100 · 100 · 100 · 100 · 3/3 | 98 · 100 · 100 · 100 · 3/3 |
| LCP / CLS | 1.4 s / 0 | 1.7 s / 0.081 |
| `agent-view`: title | Kaffora Coffee · This week's roasts | Kaffora |
| `agent-view`: headings | h1, h2, three h3 | none |
| `agent-view`: JSON-LD | 1 block | none |
| `agent-view`: visible text | 572 chars | 8 chars: "Loading…" |

**The point:** Lighthouse runs JavaScript, so it gives the CSR page a 98. An agent or crawler that only reads the HTML sees *"Loading…"*, and many AI crawlers don't execute JavaScript. In a headless architecture, Liferay delivers the content (Headless Delivery, Objects, `/o/c/...`); **rendering, SEO and agent readiness move to the front-end team**. That's the Full headless column of the matrix.

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Site template not listed under *Add Site* | The bundle isn't deployed. Check the logs for `kaffora-site-initializer` and make sure the `.jar` is in `docker/deploy/` **before** startup, or copy it into the running container's `/opt/liferay/deploy`. |
| `llms.txt` returns 404 | The virtual host isn't set (Stage 0, step 5), the feature flag is off, or *Enable llms.txt* is unchecked. |
| Scores vary ±5 between runs | Normal for simulated throttling. Close other apps, run 3 times and use the median. |
| Performance still 25 after the Docker swap on the red content | Expected: see 3.1. To confirm the swap worked, `docker compose exec liferay cat /opt/liferay/portal-ext.properties` must not contain `portal-developer` and must contain `GZipFilter=true`, and `node tools/compare.mjs baseline arch` must show Unminified JS at 0. |
| Saving CDN Host fails with "Your request failed to complete" | The URL failed validation (`WebsiteURLException`, not logged). `*.localhost` hosts are rejected: use `http://127.0.0.1:8081`. |
| Site loses its styles after going back to red | The CDN Host still points to `127.0.0.1:8081`, which is gone. Clear **Instance Settings → Platform → Instance Configuration → General → CDN Host HTTP**, or start green again. |
| CDN shows stale CSS/JS | Purge the edge cache: `docker compose -f docker-compose.yml -f docker-compose.green.yml exec cdn sh -c "rm -rf /var/cache/nginx/kaffora/*"`, then reload. |
| Console shows CORS errors from `127.0.0.1:8081` | Make sure you're on the kit's `docker/cdn/nginx.conf` (it adds `Access-Control-Allow-Origin`) and that the `cdn` container is running (`docker compose ps`). |
| Headless footer says `local fallback (HTTP 401)` or `(HTTP 404)` | 401: set `LIFERAY_AUTH` before `node headless/server.mjs`. 404: the Coffee object doesn't exist yet, run `node tools/seed-headless.mjs`. The demo works with the fallback anyway. |
| Fragment preview says *FreeMarker syntax is invalid … configuration.imagePriority evaluated to null* | The HTML uses the field before it exists. Add the Configuration JSON (2.1a step 3), or write `${configuration.imagePriority!'auto'}`. |
| *Kaffora Brand Fonts* / *Kaffora Tags* not listed in the Design screen | Check `curl.exe -I http://localhost:8080/o/kaffora-cx/kaffora-tags.js` (must be 200). If it's 404, hot-deploy without restarting, from `docker/`: `docker compose cp profiles/red/osgi/client-extensions/kaffora-cx.zip liferay:/opt/liferay/osgi/client-extensions/`, then look for `kaffora-cx` in `docker compose logs liferay`. |
| Changes don't show in Lighthouse | Publish the page, then run logged out (Incognito or CLI). |
| Agentic Browsing category missing | You're on Lighthouse 12 or on an old Chrome DevTools. Use `node tools/lh.mjs` (pins Lighthouse 13.5.0). |
| `Cannot find package 'lighthouse'` | Run `npm install` in the kit folder first. |
| `node` or `npm` not recognized (Windows) | Close and reopen PowerShell after installing Node.js, so `PATH` is refreshed. |
| `No Chrome installations found` | Install Google Chrome or set `CHROME_PATH` (see the appendix). |
| Chrome crashes in a Linux VM or container | Set `LH_CHROME_FLAGS="--headless=new --no-sandbox"`. |
| Port 8080 already in use | Find the process: `lsof -i :8080` (macOS/Linux) or `netstat -ano \| findstr :8080` (Windows). Stop it or change the port mapping in `docker-compose.yml`. |
| Image pull fails on Apple silicon | Add `platform: linux/amd64` under the `liferay` service in `docker-compose.yml` (runs under emulation, slower). |

---

## Appendix — Command cheat sheet by OS

Commands without a variant (`npm install`, `node tools/lh.mjs …`, `node tools/scoreboard.mjs …`, `docker compose …`) are identical everywhere.

| Task | macOS (zsh) | Linux (bash) | Windows (PowerShell) |
|---|---|---|---|
| Copy the Free Tier key | `cp ~/Downloads/activation-key-*.xml docker/deploy/` | `cp ~/Downloads/activation-key-*.xml docker/deploy/` | `Copy-Item $HOME\Downloads\activation-key-*.xml docker\deploy\` |
| Check llms.txt | `curl http://kaffora.localhost:8080/llms.txt` | `curl http://kaffora.localhost:8080/llms.txt` | `curl.exe http://kaffora.localhost:8080/llms.txt` |
| Set Chrome path (current session) | `export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"` | `export CHROME_PATH=/usr/bin/google-chrome` | `$env:CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"` |
| Extra Chrome flags | `export LH_CHROME_FLAGS="--headless=new"` | `export LH_CHROME_FLAGS="--headless=new --no-sandbox"` | `$env:LH_CHROME_FLAGS="--headless=new"` |
| Open a report manually | `open reports/scoreboard.html` | `xdg-open reports/scoreboard.html` | `start reports\scoreboard.html` |
| Basic auth value for MCP | `printf '%s' 'user:pass' \| base64` | `printf '%s' 'user:pass' \| base64` | `[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('user:pass'))` |
| Who is using port 8080 | `lsof -i :8080` | `lsof -i :8080` | `netstat -ano \| findstr :8080` |
| Claude Desktop config | `~/Library/Application Support/Claude/claude_desktop_config.json` | n/a | `%APPDATA%\Claude\claude_desktop_config.json` |

**Same on every OS:**

```bash
npm install                                                                   # once
node tools/lh.mjs baseline http://kaffora.localhost:8080/                     # mobile + desktop
node tools/lh.mjs final http://kaffora.localhost:8080/ mobile                 # one form factor
node tools/scoreboard.mjs baseline final --open                               # scoreboard with Mobile / Desktop switch
cd docker
docker compose up -d                                                          # red
docker compose -f docker-compose.yml -f docker-compose.green.yml up -d liferay cdn   # Stage 3: green + local CDN :8081
docker compose logs -f liferay
docker compose down -v                                                        # reset everything (deletes the data)
npm run replica                                                               # Plan B: static red :8101 / green :8102
```

