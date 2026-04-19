# HogEye +25% Organic Traffic Scorecard (Feb-May 2026)

## Baseline Snapshot (locked 2026-02-10)

- Baseline clicks (GSC top pages, last 28 days): **500**
- Baseline impressions (GSC top pages, last 28 days): **18,903**
- Baseline CTR: **2.65%**
- Baseline weighted avg position: **5.78**
- +25% click target line: **625 clicks**
- DataForSEO rank snapshot pulled for **25 tracked keywords** (timeout at 100 keyword request; reduced and completed)
- GA4 sessions and engaged sessions: **blocked** (current service account has no access to property `104905587`)

## Scenario Forecast (directional model)

| Scenario | Projected Clicks | Lift vs Baseline | Gap to +25% Target |
|---|---:|---:|---:|
| Conservative | 506.67 | +1.33% | -118.33 |
| Base | 517.25 | +3.45% | -107.75 |
| Best | 557.58 | +11.52% | -67.42 |

Interpretation: current keyword/rank baseline does **not** yet model to +25% by May without additional execution lift (new coverage, stronger CTR gains, and/or more ranking keywords).

## Monthly Checkpoints Through May

| Month | Checkpoint Date | Base Path Clicks | +25% Target Line |
|---|---|---:|---:|
| 2026-02 | 2026-02-28 | 502.82 | 625.00 |
| 2026-03 | 2026-03-31 | 507.68 | 625.00 |
| 2026-04 | 2026-04-30 | 512.39 | 625.00 |
| 2026-05 | 2026-05-31 | 517.25 | 625.00 |

## Weekly Operating Rule (fail-fast)

- Track three lines weekly in sheet tabs: baseline, base-path forecast, and actual.
- Trigger adjustment if either condition occurs:
  - three consecutive weeks below base-path by **>=10%**, or
  - two consecutive monthly checkpoints below base-path by **>=8%**.
- On trigger: re-prioritize next four posts/pages toward highest-impression non-brand queries and update titles/meta for CTR gains before publishing net-new pieces.

## Artifact Index

- `work/seo/benchmark/2026-02-10/Benchmark_Summary.csv`
- `work/seo/benchmark/2026-02-10/Benchmark_Source_References.csv`
- `work/seo/gsc_deep/2026-02-10_last_365d/`
- `work/seo/plan/Forecast_25pct_assumptions.json`
- `work/seo/plan/Forecast_25pct_keyword_model.csv`
- `work/seo/plan/Forecast_25pct_scenarios.csv`
- `work/seo/plan/Forecast_25pct_weekly_tracking.csv`
- `work/seo/plan/Forecast_25pct_monthly_checkpoints.csv`
