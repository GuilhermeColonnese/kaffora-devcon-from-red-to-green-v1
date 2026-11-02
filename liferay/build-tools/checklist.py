"""Single source for the Lighthouse 13 -> Liferay DXP checklist (Markdown + JSON)."""
import json
import os

# (category, lighthouse audit id(s), what Lighthouse says, Liferay DXP native lever, where, seeded-in-workshop)
ROWS = [
    # ------------------------------------------------------------------ Performance
    ("Performance", "render-blocking-insight", "Render-blocking CSS/JS delays first paint",
     "Production defaults: theme.css.fast.load on, minifier on (never include portal-developer.properties in prod). Remove @import from page-set CSS.",
     "portal-ext.properties · Pages ⚙ → Look and Feel → CSS", True),
    ("Performance", "image-delivery-insight", "Images are oversized or not compressed",
     "Select images from Documents and Media so Adaptive Media serves <picture>/srcset renditions. Define resolutions that match your breakpoints and run Adapt All Images.",
     "Control Panel → Adaptive Media · Page Editor → Image Source: Direct", True),
    ("Performance", "lcp-discovery-insight", "LCP image not discoverable, lazy-loaded or not prioritized",
     "Keep the LCP image eager (Enable Lazy Loading off). Put it in the initial HTML (fragment editable, not injected by JS).",
     "Page Editor → image → Enable Lazy Loading", True),
    ("Performance", "lcp-breakdown-insight", "Where LCP time goes (TTFB, load delay, render delay)",
     "Reduce TTFB with fragment caching (\"cacheable\" fragments), production caches and the Page Audit panel's render times per fragment.",
     "Page Editor → Page Audit · fragment.json cacheable", False),
    ("Performance", "cache-insight", "Static resources have short or no cache lifetime",
     "Don't disable the Header/ETag filters (developer mode does). Put a CDN with origin pull in front.",
     "portal-ext.properties · Instance Settings → General → CDN Host", True),
    ("Performance", "document-latency-insight", "Slow document: redirects, server response, no compression",
     "Compress at the proxy/CDN, or turn on com.liferay.portal.servlet.filters.gzip.GZipFilter (it's off by default). Serve the site on its virtual host to avoid redirect hops.",
     "portal-ext.properties · Site Settings → Site URL", True),
    ("Performance", "font-display-insight", "Web fonts block text rendering",
     "Declare fonts through Style Book tokens. Self-host with font-display: swap, or use a system font stack.",
     "Design → Style Books → Typography", True),
    ("Performance", "network-dependency-tree-insight", "Long critical request chains",
     "Avoid CSS @import chains and JS that loads more JS. Use preconnect only for real third parties.",
     "Pages ⚙ → CSS / JavaScript", True),
    ("Performance", "cls-culprits-insight", "Layout shifts: unsized images, injected content, web fonts",
     "Adaptive Media outputs width/height. Never inject banners at the top via JS. Use a page fragment (reserved space) or the native cookie banner (overlay).",
     "Page Editor · Instance Settings → Cookies", True),
    ("Performance", "third-parties-insight", "Third-party code blocks the main thread",
     "Move tags from the free-text JavaScript field to a JavaScript client extension (async/defer, versioned, scoped).",
     "Client extensions → Global JS", True),
    ("Performance", "legacy-javascript-insight · duplicated-javascript-insight", "Polyfills/legacy or duplicated JS bundles",
     "Build custom JS as client extensions that share Liferay's import maps (React, Clay) instead of bundling their own copies.",
     "Client extensions · import maps", True),
    ("Performance", "dom-size-insight", "Excessive DOM size",
     "Paginate collections and Asset Publishers. Limit items per page and avoid nested grids inside collection items.",
     "Page Editor → Collection Display → Pagination", False),
    ("Performance", "modern-http-insight", "Resources not served over HTTP/2+",
     "Terminate TLS with HTTP/2 or HTTP/3 at the reverse proxy or CDN (Liferay SaaS/PaaS do this at the edge).",
     "Web server / CDN", False),
    ("Performance", "viewport-insight", "Tap delay because the viewport isn't optimized for mobile",
     "Keep the theme's width=device-width viewport meta tag. Don't override it in themes or client extensions.",
     "Theme", False),
    # ------------------------------------------------------------------ Accessibility
    ("Accessibility", "color-contrast", "Text contrast below WCAG AA (4.5:1)",
     "Fix colours once in the Style Book (Primary/Secondary tokens) so every fragment inherits them.",
     "Design → Style Books", True),
    ("Accessibility", "image-alt", "Images without alt text",
     "Fill in Image Description on image editables and D&M files. Leave it empty only for decorative images (alt=\"\").",
     "Page Editor → image → Image Description", True),
    ("Accessibility", "button-name · link-name", "Icon-only buttons/links without an accessible name",
     "Expose aria-label as fragment configuration so authors set it without touching HTML.",
     "Page Editor → fragment → Configuration", True),
    ("Accessibility", "label", "Form fields without labels",
     "Use Liferay Forms or Object form fragments (labels by default). In custom fragments, make the label configurable.",
     "Page Editor · Forms · Objects", True),
    ("Accessibility", "heading-order", "Heading levels skip (h1 → h4)",
     "Set the Heading fragment's level for document structure. Control visual size with styles, not levels.",
     "Heading fragment → Configuration → Heading Level", True),
    ("Accessibility", "html-has-lang · valid-lang", "Missing or invalid document language",
     "Configure site languages. Liferay writes lang on <html> per locale.",
     "Site Settings → Localization", False),
    ("Accessibility", "frame-title · video-caption", "Embeds without titles/captions",
     "Give External Video fragments a title. Provide captions on hosted video.",
     "Page Editor → Video fragment", False),
    ("Accessibility", "bypass (skip link) · landmarks", "No way to skip repeated content",
     "Keep the theme's skip-to-content link and main landmark. Label nav landmarks via fragment configuration.",
     "Theme · fragment configuration", True),
    # ------------------------------------------------------------------ Best practices
    ("Best Practices", "errors-in-console", "Errors logged to the console",
     "Remove dead snippets from the page-set JavaScript field. Monitor client extensions in each release.",
     "Pages ⚙ → Advanced → JavaScript", True),
    ("Best Practices", "geolocation-on-start · notification-on-start", "Permission prompts on page load",
     "Ask for permissions only after a user action, inside a client extension. Never in the global JS field.",
     "Client extensions", True),
    ("Best Practices", "paste-preventing-inputs", "Inputs block pasting",
     "Remove paste blockers. Use Liferay Forms validation and CAPTCHA instead.",
     "Pages ⚙ → JavaScript · Forms", True),
    ("Best Practices", "csp-xss (unscored)", "No effective Content Security Policy",
     "Enable CSP with the [$NONCE$] placeholder. Start in Report Only mode, then enforce.",
     "Instance Settings → Security → Content Security Policy", True),
    ("Best Practices", "has-hsts · origin-isolation · clickjacking-mitigation (unscored)", "Missing HSTS/COOP/frame protections",
     "Keep http.header.secure.x.frame.options on. Set HSTS/COOP at the proxy or CDN.",
     "portal-ext.properties · web server", False),
    ("Best Practices", "is-on-https · redirects-http", "Not served over HTTPS",
     "Terminate TLS at the proxy and set web.server.protocol=https so Liferay generates https URLs.",
     "portal-ext.properties · proxy", False),
    ("Best Practices", "image-aspect-ratio · image-size-responsive", "Distorted or low-resolution images",
     "Let Adaptive Media pick resolutions per viewport. Define a high-density (2x) resolution where needed.",
     "Control Panel → Adaptive Media", False),
    ("Best Practices", "third-party-cookies", "Third-party cookies in use",
     "Use the native cookie consent banner and categorize cookies. Load tags only after consent.",
     "Instance Settings → Cookies", False),
    # ------------------------------------------------------------------ SEO
    ("SEO", "is-crawlable", "Page blocked from indexing (noindex / robots)",
     "Clear staging robots directives before go-live. Audit Robots per page and in robots.txt.",
     "Pages → Configure → SEO → Robots", True),
    ("SEO", "meta-description · document-title", "Missing description / generic title",
     "Set HTML Title and Description per page. On Display Page Templates, map them to content fields.",
     "Pages → Configure → SEO · Display Page Template → SEO", True),
    ("SEO", "robots-txt", "robots.txt is invalid",
     "Maintain robots.txt per page set with [$PROTOCOL$]/[$HOST$]/[$PORT$] placeholders and a Sitemap line.",
     "Pages ⚙ → Advanced → Robots", True),
    ("SEO", "link-text", "Links like \"click here\" / \"read more\"",
     "Make link text editable in fragments and write descriptive text in the Page Editor.",
     "Page Editor", True),
    ("SEO", "canonical", "Invalid or conflicting canonical URL",
     "Keep Liferay's default absolute canonical. Use a custom canonical only for real duplicates. Pick the localized-URL strategy per instance.",
     "Pages → Configure → SEO · Instance Settings → Pages → SEO", False),
    ("SEO", "hreflang", "Invalid alternate language links",
     "Liferay generates hreflang per available language. Enable translated-pages-only to avoid pointing at untranslated pages.",
     "Instance Settings → Pages → SEO", False),
    ("SEO", "http-status-code · crawlable-anchors", "Error status or non-crawlable links",
     "Use real <a href> links in navigation fragments. Track 404s and create 301s in Redirection.",
     "Site Menu → Configuration → Redirection", False),
    ("SEO", "structured-data (manual)", "No machine-readable entity data",
     "Reusable JSON-LD fragment (Organization/Product/Article), mapped to structure fields on Display Page Templates.",
     "Fragments · Display Page Templates", True),
    ("SEO", "(sitemap, not audited)", "Search engines can't discover all URLs",
     "Enable the XML sitemap per content type. In 2026.Q3, schedule cached generation for large sites.",
     "Instance Settings → SEO → XML Sitemap", True),
    # ------------------------------------------------------------------ Agentic
    ("Agentic Browsing", "llms-txt", "llms.txt missing required H1, links or length",
     "Enable the native llms.txt (2026.Q3 beta, flag LPD-80518) per site or instance and write curated Markdown: H1, summary, sections with links.",
     "Site Settings → SEO → llms.txt", True),
    ("Agentic Browsing", "agent-accessibility-tree", "Accessibility tree not well-formed for agents",
     "Same levers as accessibility: names, labels, landmarks and ARIA validity through Style Books and fragment configuration.",
     "Page Editor · Style Books", True),
    ("Agentic Browsing", "cumulative-layout-shift", "Layout moves under an agent taking screenshots",
     "Reserve space for all content at render time. No JS-injected banners.",
     "Page Editor · Cookies banner", True),
    ("Agentic Browsing", "webmcp-form-coverage · webmcp-registered-tools · webmcp-schema-validity (weight 0)", "Forms not exposed as agent tools",
     "Offer a fragment configuration toggle that adds WebMCP declarative attributes (toolname, tooldescription, toolparamdescription).",
     "Page Editor → fragment → Configuration", True),
    ("Agentic Browsing", "ard-schema (weight 0, Lighthouse 13.5)", "No ai-catalog.json for agent resource discovery",
     "Keep an eye on the Agentic Resource Discovery spec. There's no native DXP feature yet.",
     "Watch item", False),
    ("Agentic Browsing", "(server-side, not audited)", "Agents need structured, permissioned access to content",
     "Enable Liferay's MCP Server (/o/mcp, flag LPD-63311). Agents act with the authenticated user's permissions.",
     "Instance Settings → Platform → MCP Server", True),
]


def as_dicts():
    return [dict(zip(["category", "audit", "finding", "fix", "where", "seeded"], r)) for r in ROWS]


def markdown():
    out = ["# Lighthouse 13 → Liferay DXP checklist", "",
           "Map every Lighthouse 13 insight or audit to a native Liferay DXP (2026.Q3) configuration. ✅ = practised in the DevCon 2026 workshop.", ""]
    cat = None
    for r in as_dicts():
        if r["category"] != cat:
            cat = r["category"]
            out += ["", f"## {cat}", "", "| | Lighthouse | What it means | Liferay DXP fix | Where |", "|---|---|---|---|---|"]
        mark = "✅" if r["seeded"] else "☐"
        fix = r['fix'].replace('<', '&lt;').replace('>', '&gt;')
        out.append(f"| {mark} | `{r['audit']}` | {r['finding']} | {fix} | {r['where']} |")
    out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    kit = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs")
    open(os.path.join(kit, "CHECKLIST.md"), "w").write(markdown())
    json.dump(as_dicts(), open(os.path.join(os.path.dirname(__file__), "checklist.json"), "w"), indent=1, ensure_ascii=False)
    print(len(ROWS), "rows")
