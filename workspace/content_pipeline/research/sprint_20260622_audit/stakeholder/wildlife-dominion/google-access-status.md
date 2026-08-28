# Google Cloud access — Wildlife Dominion

**Client:** Wildlife Dominion (HogEye + Boar Blanket)  
**Document:** Google access status (working)  
**Created:** 2026-06-10  

## Service account in use

| Field | Value |
| ----- | ----- |
| Key file | `BB-Seo-Content-Publisher-2026/secrets/ttt-google-service-account.json` (repo sibling) |
| GCP project | `tic-tac-toe-485419` |
| Service account | `tic-tac-toe@tic-tac-toe-485419.iam.gserviceaccount.com` |

Pull script: [`analysis/google_wildlife_dominion_pull.py`](../../analysis/google_wildlife_dominion_pull.py)

## Access matrix (verified 2026-06-22 — live probe)

| Property | GSC | GA4 property ID | GA4 API |
| -------- | --- | --------------- | ------- |
| **HogEye** (`hogeyecameras.com`) | **OK** | `245859533` | **OK** — sample report returned 12 rows |
| **Boar Blanket** (`boarblanket.com`) | OK | `484642911` | **OK** (2026-06-22 probe) |

Probe command: `python3 analysis/google_wildlife_dominion_pull.py --probe-only`  
Latest probe file: `clients/wildlife-dominion/working/google-access-probe.json`

### HogEye — confirmed 2026-06-22

- **GSC:** `sc-domain:hogeyecameras.com` listed on service account; API auth OK.
- **GA4:** Property **`245859533`** — `run_report` succeeded (3-day sample).
- **Last full pull in repo:** 2026-06-10 (GSC through **2026-06-07**; GA4 monthly through Jun 2026). **Refresh needed** before Phase 4 findings.

### GSC (historical note)

Both domain properties are accessible:

- `sc-domain:hogeyecameras.com`
- `sc-domain:boarblanket.com`

Exports saved under `clients/{slug}/inputs/gsc/` (Performance_by_date, Pages, Queries).

**Note:** HogEye GSC history starts **2025-01-26** (no 2024 rows returned). Boar Blanket GSC starts **2025-04-01** — aligns with Q2 2025 content launch.

### GA4

- HogEye uses property **`245859533`** (not `104905587` from older manual exports).
- Boar Blanket property **`481500132`** exists in Jcore config but **`tic-tac-toe@...` is not granted access**.

**Fix for Boar Blanket GA4:** In GA4 Admin → Property access management, add `tic-tac-toe@tic-tac-toe-485419.iam.gserviceaccount.com` as **Viewer**, then run:

```bash
python3 analysis/google_wildlife_dominion_pull.py --brand boar-blanket --start-date 2024-01-01
```

### Alternate HogEye key (not used for pulls)

`hogeye-494119-97269a61c407.json` — Analytics Data API **disabled** on project `hogeye-494119`. Enable at [Google Cloud Console](https://console.developers.google.com/apis/api/analyticsdata.googleapis.com/overview?project=hogeye-494119) if you prefer that project.

## DataForSEO

Credentials in repo `.env` — API confirmed working. Historical rank pulled for Boar Blanket; full HogEye bundle at `clients/hogeye/inputs/dataforseo/dataforseo_hogeye_raw.json`.
