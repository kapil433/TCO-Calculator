# TCO Calculator — Final Check Report

**Date:** March 2025

---

## ✅ Build & Deployment

| Component | Status | Notes |
|-----------|--------|------|
| Frontend build | ✅ Pass | `npm run build` succeeds |
| Backend calc | ✅ Pass | `calc_vehicle()` returns valid TCO |
| GitHub Actions | ✅ Ready | Deploy on push to `main` |
| Render Docker | ✅ Ready | Dockerfile + `.dockerignore` in place |

---

## ✅ Data & Calculations

| Item | Status |
|------|--------|
| IDV depreciation | ✅ IRDAI schedule (0.05, 0.15, 0.20, 0.30, 0.40, 0.50...) |
| TP large premium | ✅ 7897 (IRDAI FY2024-25) |
| Mileage guard | ✅ `max(mileage, 0.1)` prevents division-by-zero |
| API route order | ✅ `/fuel-prices/live/meta` before `/{state_code}` |

---

## ✅ Frontend

| Feature | Status |
|---------|--------|
| Error Boundary | ✅ Wraps App |
| GA (G-FV2JJFMKN3) | ✅ In index.html + analytics.js |
| PDF export | ✅ JPEG compression, ~2–8 MB (was 60–70 MB) |
| Backend-down banner | ✅ Shows legacy link when API unreachable |
| Form validation | ✅ Ex-showroom, mileage, ann_km |
| A11y | ✅ Tab roles, keyboard nav, aria-invalid |
| Duplicate IDs | ✅ Fixed `ex-hint` with `vehicleIndex` |

---

## ⚠️ Required Configuration

### GitHub (Repo → Settings → Secrets and variables → Actions)

| Variable | Required | Purpose |
|----------|----------|---------|
| `VITE_API_URL` | **Yes** | Backend URL, e.g. `https://tco-calculator-api.onrender.com` |

Without this, the frontend will call `kapil433.github.io/api/...` (404) instead of your Render backend.

### Render

| Setting | Value |
|---------|-------|
| Root directory | `backend` |
| CORS_ORIGINS | `https://kapil433.github.io` |
| REFRESH_KEY | Optional — set if you need to call `/fuel-prices/refresh` |

---

## 🔧 Fixes Applied in This Check

1. **Dockerfile** — Use `PORT` env (Render compatibility): `--port ${PORT:-10000}`
2. **Duplicate IDs** — `ex-hint` → `ex-hint-${vehicleIndex}` for compare mode

---

## Quick Verification

1. **Frontend:** Visit https://kapil433.github.io/TCO-Calculator/
2. **Backend:** Check Render dashboard for successful deploy
3. **GA:** GA4 → Realtime while visiting the site
4. **API:** Ensure `VITE_API_URL` is set in GitHub Actions vars
