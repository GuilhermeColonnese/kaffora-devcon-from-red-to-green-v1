# Adaptive Media resolutions

Control Panel → Configuration → Adaptive Media → Add (Max Width only):

| Name | Max Width | Used for |
|---|---|---|
| Card-400 | 400 | product cards (fixed Resolution, every viewport) |
| Mobile-760 | 760 | the roastery (LCP) image on phones |
| Desktop-1600 | 1600 | the roastery image on large screens |

Then open ⋮ at the top of the list → **Adapt All Images**.

Avoid exact 2× pairs (for example 800 + 1600): Adaptive Media treats the larger one as the high-density (2x) version, so phones with a device pixel ratio above 1 download the big file.

## The LCP switch (live code)

Design → Fragments → Kaffora Coffee → Kaffora Hero → Edit:

1. **Configuration** tab first: paste `kaffora-hero/configuration.json`.
2. **Code** tab, HTML: add to the roastery `<img>`
   `fetchpriority="${configuration.imagePriority!'auto'}"` (see `kaffora-hero/index.html`).
   `!'auto'` is FreeMarker's default operator, so the preview never breaks before the field exists.
3. **Publish**, then propagate to the pages that use it.
4. Page Editor → select the hero → Configuration → **Roastery image priority → High (LCP image)** → Publish.
