# Lighthouse 13 → Liferay DXP checklist

Map every Lighthouse 13 insight or audit to a native Liferay DXP (2026.Q3) configuration. ✅ = practised in the DevCon 2026 workshop.


## Performance

| | Lighthouse | What it means | Liferay DXP fix | Where |
|---|---|---|---|---|
| ✅ | `render-blocking-insight` | Render-blocking CSS/JS delays first paint | Production defaults: theme.css.fast.load on, minifier on (never include portal-developer.properties in prod). Remove @import from page-set CSS. | portal-ext.properties · Pages ⚙ → Design → CSS |
| ✅ | `image-delivery-insight` | Images are oversized or not compressed | Select images from Documents and Media so Adaptive Media serves &lt;picture&gt;/srcset renditions. Define resolutions that match your breakpoints, avoid exact 2× pairs (they become the HD source, so phones get the big file), run Adapt All Images, and pin small images (cards, thumbnails) to a small Resolution. | Control Panel → Adaptive Media · Page Editor → Image Source: Direct → Resolution |
| ✅ | `lcp-discovery-insight` | LCP image not discoverable, lazy-loaded or not prioritized | Keep the LCP image eager (Enable Lazy Loading off), in the initial HTML (fragment editable, not injected by JS), with fetchpriority="high" exposed as a fragment configuration option (one attribute + a select field in the fragment, so authors choose the LCP image). | Page Editor → image → Enable Lazy Loading · fragment Configuration |
| ☐ | `lcp-breakdown-insight` | Where LCP time goes (TTFB, load delay, render delay) | Reduce TTFB with fragment caching ("cacheable" fragments), production caches and the Page Audit panel's render times per fragment. | Page Editor → Page Audit · fragment.json cacheable |
| ✅ | `cache-insight` | Static resources have short or no cache lifetime | Don't disable the Header/ETag filters (developer mode does). Put a CDN with origin pull in front. | portal-ext.properties · Instance Settings → Platform → Instance Configuration → General → CDN Host |
| ✅ | `document-latency-insight` | Slow document: redirects, server response, no compression | Compress at the proxy/CDN. GZipFilter (off by default) only compresses what goes through the portal filter chain (pages, combo, dynamic CSS), not static bundle resources such as clay.css. Serve the site on its virtual host to avoid redirect hops. | portal-ext.properties · Site Settings → Site URL |
| ✅ | `font-display-insight` | Web fonts block text rendering | Self-host the few weights you use (woff2, latin subset) in a CSS client extension with font-display: optional (or swap), and reference the families in the Style Book tokens with a system fallback. | Pages ⚙ → Design → CSS Client Extensions · Style Books → Typography |
| ✅ | `network-dependency-tree-insight` | Long critical request chains | Avoid CSS @import chains and JS that loads more JS. Use preconnect only for real third parties. | Pages ⚙ → CSS / JavaScript |
| ✅ | `cls-culprits-insight` | Layout shifts: unsized images, injected content, web fonts | Adaptive Media outputs width/height. Never inject banners at the top via JS. Use a page fragment (reserved space) or the native cookie banner (overlay). | Page Editor · Instance Settings → Cookies |
| ✅ | `third-parties-insight` | Third-party code blocks the main thread | Move tags from the free-text JavaScript field to a JavaScript client extension: async, In Page Bottom, work in requestIdleCallback, versioned and scoped per site. | Client extensions → Global JS |
| ✅ | `legacy-javascript-insight · duplicated-javascript-insight` | Polyfills/legacy or duplicated JS bundles | Build custom JS as client extensions that share Liferay's import maps (React, Clay) instead of bundling their own copies. | Client extensions · import maps |
| ☐ | `dom-size-insight` | Excessive DOM size | Paginate collections and Asset Publishers. Limit items per page and avoid nested grids inside collection items. | Page Editor → Collection Display → Pagination |
| ☐ | `modern-http-insight` | Resources not served over HTTP/2+ | Terminate TLS with HTTP/2 or HTTP/3 at the reverse proxy or CDN (Liferay SaaS/PaaS do this at the edge). | Web server / CDN |
| ☐ | `viewport-insight` | Tap delay because the viewport isn't optimized for mobile | Keep the theme's width=device-width viewport meta tag. Don't override it in themes or client extensions. | Theme |

## Accessibility

| | Lighthouse | What it means | Liferay DXP fix | Where |
|---|---|---|---|---|
| ✅ | `color-contrast` | Text contrast below WCAG AA (4.5:1) | Fix colours once in the Style Book (Primary/Secondary tokens) so every fragment inherits them. | Design → Style Books |
| ✅ | `image-alt` | Images without alt text | Fill in Image Description on image editables and D&M files. Leave it empty only for decorative images (alt=""). | Page Editor → image → Image Description |
| ✅ | `button-name · link-name` | Icon-only buttons/links without an accessible name | Expose aria-label as fragment configuration so authors set it without touching HTML. | Page Editor → fragment → Configuration |
| ✅ | `label` | Form fields without labels | Use Liferay Forms or Object form fragments (labels by default). In custom fragments, make the label configurable. | Page Editor · Forms · Objects |
| ✅ | `heading-order` | Heading levels skip (h1 → h4) | Set the Heading fragment's level for document structure. Control visual size with styles, not levels. | Heading fragment → Configuration → Heading Level |
| ☐ | `html-has-lang · valid-lang` | Missing or invalid document language | Configure site languages. Liferay writes lang on &lt;html&gt; per locale. | Site Settings → Localization |
| ☐ | `frame-title · video-caption` | Embeds without titles/captions | Give External Video fragments a title. Provide captions on hosted video. | Page Editor → Video fragment |
| ✅ | `bypass (skip link) · landmarks` | No way to skip repeated content | Keep the theme's skip-to-content link and main landmark. Label nav landmarks via fragment configuration. | Theme · fragment configuration |

## Best Practices

| | Lighthouse | What it means | Liferay DXP fix | Where |
|---|---|---|---|---|
| ✅ | `errors-in-console` | Errors logged to the console | Remove dead snippets from the page-set JavaScript field. Monitor client extensions in each release. | Pages ⚙ → Advanced → JavaScript |
| ✅ | `geolocation-on-start · notification-on-start` | Permission prompts on page load | Ask for permissions only after a user action, inside a client extension. Never in the global JS field. | Client extensions |
| ✅ | `paste-preventing-inputs` | Inputs block pasting | Remove paste blockers. Use Liferay Forms validation and CAPTCHA instead. | Pages ⚙ → JavaScript · Forms |
| ✅ | `csp-xss (unscored)` | No effective Content Security Policy | Enable CSP with the [$NONCE$] placeholder. Start in Report Only mode, then enforce. | Instance Settings → Security → Content Security Policy |
| ☐ | `has-hsts · origin-isolation · clickjacking-mitigation (unscored)` | Missing HSTS/COOP/frame protections | Keep http.header.secure.x.frame.options on. Set HSTS/COOP at the proxy or CDN. | portal-ext.properties · web server |
| ☐ | `is-on-https · redirects-http` | Not served over HTTPS | Terminate TLS at the proxy and set web.server.protocol=https so Liferay generates https URLs. | portal-ext.properties · proxy |
| ☐ | `image-aspect-ratio · image-size-responsive` | Distorted or low-resolution images | Let Adaptive Media pick resolutions per viewport. Define a high-density (2x) resolution where needed. | Control Panel → Adaptive Media |
| ☐ | `third-party-cookies` | Third-party cookies in use | Use the native cookie consent banner and categorize cookies. Load tags only after consent. | Instance Settings → Cookies |

## SEO

| | Lighthouse | What it means | Liferay DXP fix | Where |
|---|---|---|---|---|
| ✅ | `is-crawlable` | Page blocked from indexing (noindex / robots) | Clear staging robots directives before go-live. Audit Robots per page and in robots.txt. | Pages → Configure → SEO → Robots |
| ✅ | `meta-description · document-title` | Missing description / generic title | Set HTML Title and Description per page. On Display Page Templates, map them to content fields. | Pages → Configure → SEO · Display Page Template → SEO |
| ✅ | `robots-txt` | robots.txt is invalid | Maintain robots.txt per page set with [$PROTOCOL$]/[$HOST$]/[$PORT$] placeholders and a Sitemap line. | Pages ⚙ → Advanced → Robots |
| ✅ | `link-text` | Links like "click here" / "read more" | Make link text editable in fragments and write descriptive text in the Page Editor. | Page Editor |
| ☐ | `canonical` | Invalid or conflicting canonical URL | Keep Liferay's default absolute canonical. Use a custom canonical only for real duplicates. Pick the localized-URL strategy per instance. | Pages → Configure → SEO · Instance Settings → Pages → SEO |
| ☐ | `hreflang` | Invalid alternate language links | Liferay generates hreflang per available language. Enable translated-pages-only to avoid pointing at untranslated pages. | Instance Settings → Pages → SEO |
| ☐ | `http-status-code · crawlable-anchors` | Error status or non-crawlable links | Use real &lt;a href&gt; links in navigation fragments. Track 404s and create 301s in Redirection. | Site Menu → Configuration → Redirection |
| ✅ | `structured-data (manual)` | No machine-readable entity data | Reusable JSON-LD fragment (Organization/Product/Article), mapped to structure fields on Display Page Templates. | Fragments · Display Page Templates |
| ✅ | `(sitemap, not audited)` | Search engines can't discover all URLs | Enable the XML sitemap per content type. In 2026.Q3, schedule cached generation for large sites. | Instance Settings → SEO → XML Sitemap |

## Agentic Browsing

| | Lighthouse | What it means | Liferay DXP fix | Where |
|---|---|---|---|---|
| ✅ | `llms-txt` | llms.txt missing required H1, links or length | Enable the native llms.txt (2026.Q3 beta, flag LPD-80518) per site or instance and write curated Markdown: H1, summary, sections with links. | Site Settings → SEO → llms.txt |
| ✅ | `agent-accessibility-tree` | Accessibility tree not well-formed for agents | Same levers as accessibility: names, labels, landmarks and ARIA validity through Style Books and fragment configuration. | Page Editor · Style Books |
| ✅ | `cumulative-layout-shift` | Layout moves under an agent taking screenshots | Reserve space for all content at render time. No JS-injected banners. | Page Editor · Cookies banner |
| ✅ | `webmcp-form-coverage · webmcp-registered-tools · webmcp-schema-validity (weight 0)` | Forms not exposed as agent tools | Offer a fragment configuration toggle that adds WebMCP declarative attributes (toolname, tooldescription, toolparamdescription). | Page Editor → fragment → Configuration |
| ☐ | `ard-schema (weight 0, Lighthouse 13.5)` | No ai-catalog.json for agent resource discovery | Keep an eye on the Agentic Resource Discovery spec. There's no native DXP feature yet. | Watch item |
| ✅ | `(server-side, not audited)` | Agents need structured, permissioned access to content | Enable Liferay's MCP Server (/o/mcp, flag LPD-63311). Agents act with the authenticated user's permissions. | Instance Settings → Platform → MCP Server |
