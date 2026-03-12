# Phase 7: GitHub Pages Deployment - Context

**Gathered:** 2026-03-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Deploy the `frontend/` directory to GitHub Pages as a static site accessible on iPad Safari at a custom domain. Verify no hidden server-side dependencies exist. No new features, no UI changes — just deployment and verification.

</domain>

<decisions>
## Implementation Decisions

### Static server verification
- Add E2E Playwright test run against a plain static file server (`python -m http.server frontend/`) to verify no hidden FastAPI dependencies before deploying
- Use `BASE_URL` environment variable to point Playwright at the static server URL (conftest.py reads this — no test code changes needed)
- Live in CI only — add as a 'test' job in the GitHub Actions workflow, not a local script

### Deploy trigger
- Deploy on every push to main (auto-deploy) — simple and appropriate for single-developer project
- Gate deploy on tests passing: 'deploy' job depends on 'test' job (static server E2E) passing
- Keep `workflow_dispatch` for manual deploys (already in deploy.yml)

### GitHub Pages setup
- Source: GitHub Actions (required for existing `actions/upload-pages-artifact` / `actions/deploy-pages` workflow)
- Enable in repo Settings → Pages → Source: GitHub Actions (may not be enabled yet — include setup steps)
- Custom domain: `mermaids.chriskaschner.com`
- Requires CNAME file at `frontend/CNAME` containing `mermaids.chriskaschner.com`
- Requires DNS CNAME record pointing `mermaids.chriskaschner.com` → `chriskaschner.github.io`

### Asset paths
- Already relative from Phase 6 (no leading `/`) — no changes needed
- Hash-based SPA routing already in place — no server-side routing required for static hosting

### Claude's Discretion
- Exact structure of the CI 'test' job (install deps, start static server, wait for ready, run Playwright, kill server)
- Whether to use `npx serve`, `python -m http.server`, or another static server in CI

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.github/workflows/deploy.yml`: Existing workflow with checkout → configure-pages → upload-pages-artifact → deploy-pages. Needs a 'test' job added before 'deploy'.
- `frontend/`: Self-contained static directory — HTML, CSS, JS, SVG assets, no server-side logic
- `src/mermaids/app.py`: FastAPI only mounts frontend as static files — no API routes. Static server is a drop-in replacement.

### Established Patterns
- `BASE_URL` env var: conftest.py already uses a port-finding helper — check if it reads `BASE_URL` or needs a small update
- Hash-based routing (`#/home`, `#/dressup`, `#/coloring`) — no server-side routing, works on static hosting
- All asset `fetch()` calls use relative paths: `assets/svg/mermaid.svg`, `assets/svg/dressup/*.svg`, `assets/svg/coloring/*.svg`

### Integration Points
- `deploy.yml` — add 'test' job before 'deploy', make 'deploy' depend on 'test'
- `frontend/CNAME` — new file needed for custom domain
- GitHub repo Settings → Pages → Source and Custom domain fields (manual setup step)

</code_context>

<specifics>
## Specific Ideas

- Custom domain: `mermaids.chriskaschner.com`
- DNS setup: CNAME record `mermaids.chriskaschner.com` → `chriskaschner.github.io`
- GitHub Pages source must be set to "GitHub Actions" (not a branch) for the existing deploy.yml to work

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 07-github-pages-deployment*
*Context gathered: 2026-03-11*
