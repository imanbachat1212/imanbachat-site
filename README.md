# imanbachat.com

Static site: `index.html` (homepage) and `pricing.html` (price calculator). Images in `img/`.
Deployed on Netlify from the `main` branch, no build step.

## Important: security policy and inline scripts
`netlify.toml` allows only the exact inline `<script>` blocks in `index.html` and `pricing.html` (by SHA-256 hash).
If you change any inline script, recompute its hash and update the `Content-Security-Policy` lines in `netlify.toml`,
otherwise that script will be blocked in the browser. JSON-LD (`application/ld+json`) blocks don't need hashes.
Fonts are self-hosted in `/fonts` (no Google Fonts).
