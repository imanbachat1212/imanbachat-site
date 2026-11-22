# imanbachat.com

Static site: `index.html` (homepage) and `pricing.html` (price calculator). Images in `img/`.
Deployed on Netlify from the `main` branch, no build step.

## Important: security policy and inline scripts
`netlify.toml` allows only the exact inline `<script>` blocks in `index.html` and `pricing.html` (by SHA-256 hash).
If you change any inline script, recompute its hash and update the `Content-Security-Policy` lines in `netlify.toml`,
otherwise that script will be blocked in the browser. JSON-LD (`application/ld+json`) blocks don't need hashes.
Fonts are self-hosted in `/fonts` (no Google Fonts).

## Arabic version (`/ar/`)

The Arabic pages in `ar/` are generated from the English pages:

    python3 tools/build_ar.py

After editing any English page, run the script. It fails if an English sentence it translates has changed, so
update the matching line in `tools/build_ar.py`, then rebuild. If an Arabic page's inline script changes, recompute
its hash in `netlify.toml` too.
