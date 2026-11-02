# Fix pack: every change that turns Kaffora from red to green

Ready-to-import files and copy-paste values for each checkpoint of the workshop, in the same order as the deck and `docs/WORKSHOP-GUIDE.md`.

| Folder | Checkpoint | What's inside | How to apply |
|---|---|---|---|
| `01-performance` | 1 · Performance | `kaffora-fragments-lcp-switch.zip` (the Kaffora fragment collection with the LCP switch already in Kaffora Hero), `kaffora-hero/` (HTML and configuration JSON for the live-code moment), Adaptive Media resolutions | Design → Fragments → Import (overwrite), then propagate; or paste the HTML/JSON live |
| `02-accessibility` | 2 · Accessibility | Importable Style Book *Kaffora Brand v2* (WCAG AA colours + brand fonts), accessible names and descriptions | Design → Style Books → Import; paste the values in the Page Editor |
| `03-seo` | 3 · SEO | `robots.txt`, page title/description, link texts | Paste in the screens listed |
| `04-best-practices` | 4 · Best Practices | Nonce-based CSP policy | Instance Settings → Security → Content Security Policy (Report Only) |
| `05-agentic` | 5 · Agentic + MCP | `llms.txt`, Claude Desktop config for the MCP Server | Site Settings → SEO → llms.txt; Instance Settings → MCP Server |
| `../docker` | Stage 3 · last mile | Green profile, green compose override, Nginx CDN | `docker compose -f docker-compose.yml -f docker-compose.green.yml up -d liferay cdn` |

The client extensions (`kaffora-cx.zip`: self-hosted brand fonts and governed tags) already ship inside both Docker profiles (`docker/profiles/*/osgi/client-extensions/`).

## Final checklist

- [ ] Roastery and card images selected from Documents and Media; cards on **Card-400** in **every** viewport, with lazy loading
- [ ] Kaffora Hero → Configuration → Roastery image priority = **High (LCP image)**
- [ ] Page-set CSS without the `@import`; page-set JavaScript empty; *Kaffora Brand Fonts* and *Kaffora Tags* attached
- [ ] Accessible Style Book set as default
- [ ] Accessible names, Image Descriptions and the H2 heading
- [ ] Home SEO without `noindex`, with title and description; valid robots.txt; descriptive links (footer included)
- [ ] CSP in Report Only
- [ ] llms.txt, WebMCP toggle, Schema.org fragment and MCP Server
- [ ] Green profile + CDN; final measurement on `http://kaffora.localhost:8081/`

Measure: `node tools/lh.mjs final http://kaffora.localhost:8081/` (run 3 times, keep the median), then `node tools/scoreboard.mjs baseline content final --open`.

> The fragment and Style Book archives follow Liferay's export format (checked against the 2026.Q3 source). If an import is refused on your build, use the manual path described in each folder.
