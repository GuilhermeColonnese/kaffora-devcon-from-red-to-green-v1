# Run of show — presenter script (40 min)

**Screens:** (1) slides, (2) browser with the Kaffora site + Liferay admin, (3) terminal. Keep the baseline HTML reports open in browser tabs from your dry run as a fallback.

**Platform:** Liferay DXP **Free Tier** 2026.Q3. Say it on stage: everything in this session runs on the free key, so the room can repeat it at home.

**The night before (same commands on macOS, Windows and Linux):**

1. `npm install` in the kit folder, and `docker pull liferay/dxp:2026.q3.0` (DXP Free Tier, initial Q3 release) and `docker pull nginx:1.27-alpine`.
2. Start red (`cd docker && docker compose up -d`), create the site and set the virtual host `kaffora.localhost`.
3. `node tools/lh.mjs dryrun-red http://kaffora.localhost:8080/` three times, note the median (mobile and desktop).
4. Apply checkpoints 1–5 on the red server, then `node tools/lh.mjs dryrun-content http://kaffora.localhost:8080/`.
5. Stage 3: `docker compose -f docker-compose.yml -f docker-compose.green.yml up -d liferay cdn`, set the CDN Host (guide 3.2), `node tools/lh.mjs dryrun-final …`. Compare option A (`:8080` + CDN Host) and B (`kaffora.localhost:8081`, CDN Host cleared) and keep the better one for `final`.
6. Bonus: `node tools/seed-headless.mjs`, `node headless/server.mjs`, run `h-ssr`, `h-csr` and `agent-view` (guide, Bonus).
7. Take the screenshots for slides 11, 22 and 27, and update the numbers on slides 12, 24, 26, 27 and 29.
8. Reset: clear the CDN Host, `docker compose down -v --remove-orphans`, start red again, create the site and set the virtual host.

| Clock | Slides | Say / do |
|---|---|---|
| 00:00 | 1–3 | Hook: "Your Lighthouse score is a contract with three readers." Agenda. |
| 01:00 | 4–8 | Three readers. Lighthouse 13: insights replace audits. Five categories. Agentic Browsing is a ratio. What agents look for. |
| 05:00 | 9 | Rules: no custom code, measure logged out, same conditions twice, read the insights. |
| 06:00 | 10–11 | Stage 1. Show the Kaffora site in incognito: "Looks fine, right?" Walk the five red callouts. |
| 06:30 | 12 · terminal | `node tools/lh.mjs baseline http://kaffora.localhost:8080/`. The room runs it too (mobile + desktop, ~2 min). Read the baseline report: LCP breakdown, render-blocking, image delivery (≈9 MB), llms.txt errors. |
| 10:00 | 13–14 | Stage 2: "content first, on the same red server". The lever map. |
| 11:00 | 15–16 · Liferay | Checkpoint 1, Performance (6 min). Adaptive Media without the 2× trap, cards on Card-400, then **live code** (slide 16): add the LCP switch to the Kaffora Hero fragment, publish, propagate, set it to High. Fonts and tags as client extensions. Publish. |
| 17:00 | 17 · Liferay | Checkpoint 2, Accessibility (4½ min). Style Book live, image descriptions, fragment configs, heading level. Publish. |
| 21:30 | 18 · Liferay | Checkpoint 3, SEO (3½ min). Page SEO, robots.txt, link text, 20 s tour of Redirection and XML Sitemap. |
| 25:00 | 19 · Liferay | Checkpoint 4, Best Practices (1½ min). CSP in Report Only. |
| 26:30 | 20–21 · Liferay | Checkpoint 5, Agentic (3½ min). llms.txt, WebMCP toggle, Schema.org fragment, MCP Server on, then the Claude prompt against `/o/mcp` (WOW). If it fails, unhide slide 22. |
| 30:00 | terminal | `node tools/lh.mjs content http://kaffora.localhost:8080/ mobile`. "Content done. What's left is not the author's job." |
| 31:00 | 23–24 · terminal | Stage 3, the last mile. Run `docker compose -f docker-compose.yml -f docker-compose.green.yml up -d liferay cdn`. Slide 24: the server myth with the dry-run numbers (server alone on red content: 25 → 25). |
| 31:30 | 25 | While Liferay restarts (2–3 min): the three layers. Who owns infrastructure, the DXP application, development and third parties. |
| 33:30 | 24 · Liferay + DevTools | Instance Settings → Instance Configuration → General → CDN Host = `http://127.0.0.1:8081`. Reload with *Disable cache*: clay.css from the CDN, `gzip`, `X-Cache` MISS → HIT. |
| 34:30 | 26–27 · terminal | `node tools/lh.mjs final … mobile`, then `node tools/scoreboard.mjs baseline content final --open`. Scoreboard full screen: baseline → content → final. Then the two real reports. |
| 36:30 | 28 | "Who owns each requirement?" The SEO responsibility matrix. |
| 37:30 | 29 (bonus) | Only if you're ahead: headless SSR vs CSR. Lighthouse 100 vs 98, then `agent-view`: "Loading…". Otherwise one sentence and move on. |
| 38:00 | 30–31 | Three takeaways. Checklist QR code. Q&A. |

**Three takeaways**

1. Most scores are lost in **content and authoring**, not in code: images, tag fields, labels, SEO settings. Fix those first.
2. Liferay gives authors **governed levers**: Style Books, Adaptive Media, fragment configuration, SEO settings. Design fragments so the right thing is the easy thing.
3. Then the **last mile is architecture**: production properties, compression and caching at the edge. And agent readiness is the same work you already know, plus two native switches: `llms.txt` and the MCP Server.

**If something breaks**

- Liferay doesn't come back after the swap: stay on the layers and matrix slides, show the pre-recorded `dryrun-final` report and scoreboard.
- The CDN breaks the styles (CORS or edge down): clear the CDN Host field and keep going; the evidence is on slide 24.
- Wi-Fi is down: after `npm install` the Lighthouse tools, the CDN and the headless front work offline. The MCP demo needs the network: use hidden slide 22.
- A score comes out lower than the dry run: "Lighthouse on a laptop in a conference hall: look at the deltas and the insights that vanished."
- A participant on Windows gets `curl` errors: use `curl.exe`, or open the URL in Chrome (appendix of the guide).
