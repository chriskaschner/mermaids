# Phase 7: GitHub Pages Deployment - Research

**Researched:** 2026-03-11
**Domain:** GitHub Pages static deployment, GitHub Actions CI, Playwright E2E against static server
**Confidence:** HIGH (core deployment mechanics), MEDIUM (CNAME/custom domain specifics)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Add E2E Playwright test run against `python -m http.server frontend/` in CI (static server verification)
- Use `BASE_URL` environment variable to point Playwright at the static server URL
- Live in CI only — add as a 'test' job in the GitHub Actions workflow
- Deploy on every push to main (auto-deploy)
- Gate deploy on tests passing: 'deploy' job depends on 'test' job passing
- Keep `workflow_dispatch` for manual deploys
- GitHub Pages source: GitHub Actions (required for existing `actions/upload-pages-artifact` / `actions/deploy-pages`)
- Enable in repo Settings → Pages → Source: GitHub Actions
- Custom domain: `mermaids.chriskaschner.com`
- DNS CNAME record: `mermaids.chriskaschner.com` → `chriskaschner.github.io`
- Asset paths already relative from Phase 6 — no changes needed
- Hash-based SPA routing already in place — no server-side routing required

### Claude's Discretion
- Exact structure of the CI 'test' job (install deps, start static server, wait for ready, run Playwright, kill server)
- Whether to use `npx serve`, `python -m http.server`, or another static server in CI

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DPLY-01 | frontend/ directory deploys to GitHub Pages as static site | Existing deploy.yml already uses actions/upload-pages-artifact + actions/deploy-pages with path: frontend — needs test job gate added |
| DPLY-02 | All asset paths are relative (no absolute /assets/ paths) | Confirmed in code: all fetch() calls and COLORING_PAGES array use relative paths (no leading /) |
| DPLY-03 | App is accessible on iPad Safari via GitHub Pages URL | Playwright E2E test job in CI verifies this against static server; iPad emulation already configured in conftest.py |
</phase_requirements>

---

## Summary

Phase 7 deploys a fully static `frontend/` directory to GitHub Pages using the existing `actions/upload-pages-artifact` + `actions/deploy-pages` workflow. The site is already fully static — FastAPI only mounts the directory, there are no API routes. Asset paths are confirmed relative throughout.

The two work items are: (1) adding a CI 'test' job that runs Playwright E2E tests against a plain static file server to verify no hidden server dependencies, and (2) configuring the custom domain `mermaids.chriskaschner.com` in repo Settings + DNS.

**Critical finding:** The CONTEXT.md decision mentions "CNAME file at `frontend/CNAME`" but official GitHub docs state that CNAME files are **ignored** when using GitHub Actions as the Pages source. The custom domain must be set via repo Settings → Pages → Custom domain field. This is a documentation discrepancy in the locked decisions — the CNAME file approach applies only to branch-based deployments.

**Primary recommendation:** Add a 'test' job to deploy.yml using `python -m http.server` (available on ubuntu-latest with no extra install), update `conftest.py` to read `BASE_URL` env var and skip uvicorn startup when set, run existing Playwright tests against the static server, and configure the custom domain through the GitHub Settings UI (not a CNAME file).

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| actions/checkout | v4 | Repo checkout in CI | Already in deploy.yml |
| actions/configure-pages | v5 | Configure GitHub Pages settings | Already in deploy.yml |
| actions/upload-pages-artifact | v3 | Package frontend/ as Pages artifact | Already in deploy.yml |
| actions/deploy-pages | v4 | Deploy artifact to GitHub Pages | Already in deploy.yml |
| python -m http.server | stdlib (3.11+) | Static file server for CI test job | No install needed, available on ubuntu-latest |
| pytest-playwright | >=0.6 | Playwright test runner | Already in pyproject.toml dev deps |
| playwright | >=1.49 | Browser automation | Already in pyproject.toml dev deps |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| uv | latest | Python package manager | Install dev deps in CI (consistent with project conventions) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| python -m http.server | npx serve | serve requires Node.js; python is available free on ubuntu-latest |
| python -m http.server | npx http-server | Same: extra install, no benefit here |
| UI-only custom domain | CNAME file in frontend/ | CNAME files are ignored by actions/deploy-pages — UI is the only working method |

**Installation (CI — dev dependencies):**
```bash
uv sync --extra dev
python -m playwright install --with-deps webkit chromium
```

## Architecture Patterns

### Recommended Workflow Structure
```
.github/workflows/deploy.yml
  jobs:
    test:       # NEW — static server E2E
      - checkout
      - install python deps + playwright browsers
      - start python -m http.server frontend/ in background
      - wait for port ready (curl retry loop)
      - run pytest tests/test_e2e.py tests/test_coloring.py tests/test_dressup.py
        with BASE_URL=http://localhost:PORT
    deploy:     # EXISTING — gates on test
      - needs: [test]
      - checkout → configure-pages → upload-pages-artifact → deploy-pages
```

### Pattern 1: BASE_URL-Driven conftest.py
**What:** When `BASE_URL` env var is set, `live_server` fixture yields it directly (no uvicorn). When not set, starts uvicorn as before.
**When to use:** CI test job sets `BASE_URL=http://127.0.0.1:PORT`; local dev does not set it.
**Example:**
```python
# conftest.py live_server fixture — update
import os

@pytest.fixture(scope="session")
def live_server():
    base_url = os.environ.get("BASE_URL")
    if base_url:
        yield base_url
        return
    # existing uvicorn startup logic...
```

### Pattern 2: Static Server in GitHub Actions
**What:** Start `python -m http.server` in background, poll until ready, run tests, exit.
**When to use:** CI 'test' job only.
**Example:**
```yaml
- name: Start static server
  run: |
    python -m http.server 8080 --directory frontend &
    echo $! > /tmp/server.pid
    for i in $(seq 1 30); do
      curl -sf http://127.0.0.1:8080/ && break
      sleep 1
    done

- name: Run E2E tests against static server
  env:
    BASE_URL: http://127.0.0.1:8080
  run: uv run pytest tests/test_e2e.py tests/test_coloring.py tests/test_dressup.py -x --browser webkit

- name: Stop static server
  if: always()
  run: kill $(cat /tmp/server.pid) || true
```

### Pattern 3: Custom Domain via GitHub Settings UI (NOT CNAME file)
**What:** When using `actions/deploy-pages`, custom domain is stored in repo settings, not a CNAME file.
**When to use:** One-time manual setup step before first deploy.
**Steps:**
1. Repo Settings → Pages → Source: GitHub Actions (verify already set)
2. Repo Settings → Pages → Custom domain: `mermaids.chriskaschner.com` → Save
3. Wait for DNS check to pass (GitHub verifies the CNAME record)
4. Enable "Enforce HTTPS" once available (up to 24h after DNS propagates)

### Pattern 4: DNS CNAME Record
**What:** Point subdomain to GitHub Pages default domain.
**Record:** `mermaids` CNAME `chriskaschner.github.io`
**Verify:** `dig mermaids.chriskaschner.com CNAME` should return `chriskaschner.github.io`

### Anti-Patterns to Avoid
- **CNAME file in frontend/:** GitHub docs confirm this is ignored for `actions/deploy-pages`. Creates false confidence. Use the Settings UI.
- **Setting custom domain in UI without DNS:** Pages will show a "domain improperly configured" error. DNS must be set first.
- **Running all tests in the CI static job:** Unit tests (test_app.py, test_pipeline.py, etc.) import FastAPI and shouldn't run against a static server. Run only E2E tests (test_e2e.py, test_coloring.py, test_dressup.py, test_floodfill_unit.py).
- **Using absolute localhost URL without env var:** Hardcoding `http://127.0.0.1:8080` in test code breaks local dev. Use `BASE_URL` env var exclusively.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Static file serving in CI | Custom Python HTTP handler | `python -m http.server` | Built-in, zero setup, handles ES modules and SVG MIME types correctly |
| GitHub Pages deployment | Manual rsync/scp | `actions/deploy-pages` | Handles artifact signing, CDN invalidation, HTTPS cert renewal |
| Browser test automation | Puppeteer wrapper | Playwright (already installed) | Already in the project, iPad emulation configured |
| Port availability check | Custom socket polling | `curl` retry loop in bash | Simple, reliable, no dependencies |

**Key insight:** The deployment infrastructure is almost entirely in place. The existing deploy.yml covers 80% of the work. The task is narrowly scoped: add a test job, update conftest.py, and do one-time manual DNS + Settings UI config.

## Common Pitfalls

### Pitfall 1: CNAME File Does Not Work with actions/deploy-pages
**What goes wrong:** Developer adds `frontend/CNAME` containing domain, deploys, custom domain is not set — or is set once from UI then cleared.
**Why it happens:** Official GitHub docs explicitly state CNAME files are ignored for GitHub Actions source. The Settings UI field is the only mechanism.
**How to avoid:** Do not create a CNAME file. Set the custom domain in repo Settings → Pages → Custom domain.
**Warning signs:** Custom domain field in Settings clears after deploy; site serves from `chriskaschner.github.io/mermaids` path instead of custom domain.

### Pitfall 2: conftest.py live_server Imports FastAPI app — Fails Without uvicorn
**What goes wrong:** CI job with `BASE_URL` set still tries to import `from mermaids.app import app` at module load time, requiring FastAPI, uvicorn, and the full app to be installed.
**Why it happens:** The `live_server` fixture file imports the app at the top level.
**How to avoid:** The `BASE_URL` guard in `live_server` only skips the server startup, not the import. For the CI test job, install all dev deps (`uv sync --extra dev`), which includes everything. No structural change needed — the import will succeed even if uvicorn doesn't start.
**Warning signs:** `ModuleNotFoundError: No module named 'mermaids'` in CI.

### Pitfall 3: python -m http.server MIME Types for ES Modules
**What goes wrong:** Browser refuses to load `.js` files as modules because server returns wrong MIME type.
**Why it happens:** Python 3.11+ http.server handles `application/javascript` correctly. Older Python versions may send `text/plain`.
**How to avoid:** ubuntu-latest uses Python 3.12+. No special configuration needed.
**Warning signs:** Browser console shows `Failed to load module script: expected a JavaScript module script but the server responded with a MIME type of "text/plain"`.

### Pitfall 4: GitHub Pages Serves from Subdirectory Path Without Custom Domain
**What goes wrong:** If Pages is accessed at `chriskaschner.github.io/mermaids` (not root), relative asset paths like `assets/svg/mermaid.svg` resolve correctly. If accessed at root without custom domain, they still resolve correctly. But if the repo name changes, paths break.
**Why it happens:** `actions/upload-pages-artifact` deploys the directory as the site root.
**How to avoid:** The custom domain makes the site serve from root regardless. All paths are already relative — no `<base href>` needed.
**Warning signs:** Assets 404 after deploying to a different URL base.

### Pitfall 5: iPad Safari WebKit Differences in CI vs Browser
**What goes wrong:** Playwright WebKit on Linux emulates Safari but is not identical to iPad Safari. Tests pass in CI but fail on real device (or vice versa).
**Why it happens:** Playwright WebKit is based on Safari's engine but runs on Linux. Some iOS-specific behaviors (viewport, touch handling) may differ.
**How to avoid:** After CI passes, manually verify on real iPad Safari as final acceptance check (DPLY-03 is a manual verification requirement). CI tests provide regression protection; real device is the acceptance gate.
**Warning signs:** Touch events or `pointer-events` behaving differently on device.

### Pitfall 6: Playwright Browser Install in CI
**What goes wrong:** `playwright install` without `--with-deps` fails because OS-level browser dependencies are missing on ubuntu-latest.
**Why it happens:** ubuntu-latest is a minimal image; browser binaries need system libs.
**How to avoid:** Always use `python -m playwright install --with-deps webkit chromium`.
**Warning signs:** `error while loading shared libraries` in Playwright output.

## Code Examples

Verified patterns from official sources and the existing codebase:

### Complete Updated deploy.yml Structure
```yaml
# Source: based on existing .github/workflows/deploy.yml + GitHub Actions docs
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --extra dev

      - name: Install Playwright browsers
        run: uv run python -m playwright install --with-deps webkit chromium

      - name: Start static server
        run: |
          python -m http.server 8080 --directory frontend &
          echo $! > /tmp/server.pid
          for i in $(seq 1 30); do
            curl -sf http://127.0.0.1:8080/ && break
            sleep 1
          done

      - name: Run E2E tests against static server
        env:
          BASE_URL: http://127.0.0.1:8080
        run: uv run pytest tests/test_e2e.py tests/test_coloring.py tests/test_dressup.py tests/test_floodfill_unit.py -x --browser webkit

      - name: Stop static server
        if: always()
        run: kill $(cat /tmp/server.pid) || true

  deploy:
    needs: [test]
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: frontend
      - id: deployment
        uses: actions/deploy-pages@v4
```

### conftest.py live_server Fixture Update (BASE_URL Support)
```python
# Source: conftest.py — minimal update for BASE_URL env var
import os

@pytest.fixture(scope="session")
def live_server():
    base_url = os.environ.get("BASE_URL")
    if base_url:
        yield base_url
        return

    port = _get_free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    import time
    for _ in range(50):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                break
        except OSError:
            time.sleep(0.1)

    yield f"http://127.0.0.1:{port}"

    server.should_exit = True
    thread.join(timeout=5)
```

### DNS Verification Command
```bash
# Verify CNAME record propagated before configuring GitHub Pages
dig mermaids.chriskaschner.com CNAME
# Expected output: mermaids.chriskaschner.com. 300 IN CNAME chriskaschner.github.io.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| CNAME file in repo branch | Settings UI for custom domain | When switching to Actions source | CNAME file is ignored; UI is required |
| `actions/configure-pages` v3 | v5 | 2024 | Use v5 as in existing workflow |
| `actions/upload-pages-artifact` v1/v2 | v3 | 2024 | Use v3 as in existing workflow |
| `actions/deploy-pages` v2/v3 | v4 | 2024-2025 | Use v4 as in existing workflow |

**Deprecated/outdated:**
- CNAME file for Actions-based deployments: ignored by `actions/deploy-pages`; set custom domain in Settings UI instead
- `actions/setup-python` + pip: project uses `uv`; use `astral-sh/setup-uv@v4` + `uv sync` in CI

## Open Questions

1. **astral-sh/setup-uv action availability**
   - What we know: uv is the project's package manager; `astral-sh/setup-uv` is the standard CI action
   - What's unclear: Whether the project has previously used this action (no existing CI for tests)
   - Recommendation: Use `astral-sh/setup-uv@v4` + `uv sync --extra dev`; fallback is `pip install -e ".[dev]"` if setup-uv action has issues

2. **DNS TTL and GitHub Pages verification timing**
   - What we know: GitHub performs a DNS verification check after you enter the custom domain in Settings; it can take minutes to hours depending on TTL
   - What's unclear: Whether DNS is already configured (CONTEXT says it needs to be set up)
   - Recommendation: Plan task includes DNS config first, then Settings UI config, with a note that HTTPS enforcement can take up to 24 hours after DNS propagates

3. **Which E2E tests to include in the static server job**
   - What we know: test_e2e.py, test_coloring.py, test_dressup.py, test_floodfill_unit.py all use `live_server` fixture
   - What's unclear: Whether test_floodfill_unit.py has any FastAPI-specific behaviors (it uses `live_server` to get a URL for ES module loading)
   - Recommendation: Include all four files; all use relative paths compatible with static server

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8 + pytest-playwright 0.6 |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `uv run pytest tests/test_e2e.py -x --browser webkit` |
| Full suite command | `uv run pytest tests/test_e2e.py tests/test_coloring.py tests/test_dressup.py tests/test_floodfill_unit.py --browser webkit` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DPLY-01 | frontend/ serves as static site (no FastAPI deps) | E2E smoke | `BASE_URL=http://127.0.0.1:8080 uv run pytest tests/test_e2e.py -x --browser webkit` | Yes (test_e2e.py exists; conftest needs BASE_URL update) |
| DPLY-02 | All asset paths relative, no 404s on static server | E2E smoke | Same as above — test_e2e.py navigates all views and loads assets | Yes |
| DPLY-03 | App loads on iPad Safari via GitHub Pages URL | Manual (real device) + E2E proxy | CI: `uv run pytest tests/test_e2e.py tests/test_coloring.py tests/test_dressup.py --browser webkit` | Yes — final acceptance requires real iPad verification |

### Sampling Rate
- **Per task commit:** `BASE_URL=http://127.0.0.1:8080 uv run pytest tests/test_e2e.py -x --browser webkit` (after starting static server locally)
- **Per wave merge:** Full E2E suite against static server
- **Phase gate:** CI test job green before accepting phase complete; real iPad Safari verification before closing DPLY-03

### Wave 0 Gaps
- [ ] `tests/conftest.py` — add `BASE_URL` env var guard to `live_server` fixture (no new file, update existing)
- [ ] `.github/workflows/deploy.yml` — add 'test' job with static server + Playwright (no new file, update existing)

*(New test files are not needed — existing test files cover all requirements once conftest.py is updated)*

## Sources

### Primary (HIGH confidence)
- [GitHub Pages managing custom domains - Official Docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) — CNAME file behavior with Actions source, custom domain setup steps
- [actions/deploy-pages issue #304](https://github.com/actions/deploy-pages/issues/304) — confirmed CNAME files are not supported by actions/deploy-pages, closed as "not planned"
- [Playwright Python CI docs](https://playwright.dev/python/docs/ci) — browser install, GitHub Actions setup
- Existing codebase: `deploy.yml`, `conftest.py`, `pyproject.toml`, `frontend/js/*.js` — confirmed asset paths, test infrastructure, action versions

### Secondary (MEDIUM confidence)
- [GitHub community discussion #48422](https://github.com/orgs/community/discussions/48422) — custom domain field clearing behavior, multiple users confirming Settings UI approach
- [GitHub community discussion #159544](https://github.com/orgs/community/discussions/159544) — same issue, confirmed custom domain must be set in UI for Actions deployments

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — existing workflow uses pinned action versions; python stdlib static server requires no research
- Architecture: HIGH — test job pattern is straightforward; `BASE_URL` env var pattern is a minimal conftest change
- CNAME/custom domain: MEDIUM — official docs are clear that CNAME files don't work, but the GitHub Settings UI persistence behavior across deploys has some community ambiguity (most report it persists once set via UI)
- Pitfalls: HIGH — CNAME pitfall is documented in official sources; others from code inspection

**Research date:** 2026-03-11
**Valid until:** 2026-09-11 (stable — GitHub Pages/Actions APIs change infrequently)
