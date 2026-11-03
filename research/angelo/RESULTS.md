# Track 07: does it matter when in the hour the price moved?

**Verdict: REJECT.** The signal predicts the next bar (H1 holds there) but not the bar after it. At 5 bps, fees on the primary cell are about 12.6 times its gross PnL (break-even about 0.39 bps).

Pre-registration: `research/angelo/PREREGISTRATION.md` (PR #9, posted 2026-11-03 22:20 UTC, before any full-panel run). Nothing below departs from it.

## Hypothesis
- **H1:** `-close_location_residual` (close-to-VWAP gap after removing the hour's own return, cross-sectionally) has positive rank IC with future close-to-close returns beyond plain reversal.
- **H2:** enough survives a one-hour lag and 5 bps fees for a dollar-neutral strategy to have net Sharpe > 0.
- **Stated prior:** the effect sits in the next bar, so it is gone at the skipped bar and the strategy is rejected on the lag test.

## Setup
- Panel: `data/train_1h.parquet`, 20 Binance USD-M perpetuals, 14,871 hours (Jan 2025 to Sep 2026).
- IC: mean per-hour Spearman IC at h = 1, 2, 4, 8, 24 and skip-1. Plain t-stats for h = 1 and skip-1, Newey-West (h-1 lags) for h ≥ 2. Holm over the 6 horizons. **Primary cell: skip-1.**
- Strategy: per-symbol EWM(k) of the residual, re-residualized on the k-hour return, then negated, `cross_sectional_zscore` and `rebalance_deadband(b)`. Grid: k ∈ {1, 6, 24} × b ∈ {0.005, 0.015, 0.03}. **Primary cell: k = 6, b = 0.015.** Holm over the 9 cells on net Sharpe at 5 bps.
- Two-sided p-values throughout. This was fixed in the scripts' docstrings before they were run.

## IC results (`ic_results.md`)
| Horizon | IC (S_res) | t | Holm p | Increment over −r_t (t) | IC (S_raw, comparison) |
|---|---|---|---|---|---|
| 1h | 0.0141 | 6.21 | 3e-9 | 0.0143 (6.18) | 0.0310 |
| 2h | 0.0131 | 5.85 (NW) | 2e-8 | 0.0131 (5.78) | 0.0275 |
| 4h | 0.0072 | 3.22 (NW) | 0.005 | 0.0068 (3.05) | 0.0228 |
| 8h | 0.0028 | 1.23 (NW) | 0.28 | 0.0027 (1.18) | 0.0129 |
| 24h | −0.0032 | −1.48 (NW) | 0.28 | −0.0038 (−1.71) | 0.0056 |
| **skip-1 (primary)** | **0.0038** | **1.69** | **0.27** | 0.0034 (1.51) | 0.0117 |

The residual adds information over plain reversal at the next bar. The cumulative 2h and 4h ICs are mostly that same next-bar effect. One hour later it is not distinguishable from zero.

## Strategy grid (`grid_results.md`), net Sharpe at 5 bps
| k \ b | 0.005 | 0.015 | 0.03 |
|---|---|---|---|
| 1 | −30.0 | −29.5 | −27.9 |
| 6 | −18.3 | **−17.5 (primary)** | −15.2 |
| 24 | −10.0 | −8.9 | −6.9 |

Every 95% interval lies below zero. Holm-adjusted p-values are all tiny, but every one of them belongs to a *negative* Sharpe, so no cell supports H2. Gross (0 bps) Sharpe is positive in every cell: about 2.6 at k = 1, 1.5 at k = 6 and 0.35–0.57 at k = 24. Break-even fees are 0.23–0.45 bps. Turnover is 0.27–1.41 per hour.

## Audit of the primary cell (`audit_primary.txt`)
- **Verdict:** REJECT (seed 2228275014). Causality PASS on 14 cuts. DQS 99.93.
- **Fee rows:**

  | Fee | Sharpe at 1-bar lag | 95% interval |
  |---|---|---|
  | 0 bps | +1.48 | [−0.09, 2.96] |
  | 3 bps | −9.93 | |
  | 5 bps | −17.51 | |
  | 10 bps | −36.30 | |
  | tiered (~7.7 bps) | −28.15 | |

- **Out-of-sample** (last 30%) at 5 bps: −16.30.
- **Lag test** (one more hour of delay, 5 bps): Sharpe −19.20, FAIL.
- **Turnover:** 0.723 per hour. **Break-even fee:** about 0.39 bps (gross +42.7% vs fees 537.8%).
- **Wick share:** 2.8%, PASS. **Null check:** PASS (mean +0.01).

## Conclusion
Where the close sits against the hour's VWAP does carry information that plain reversal doesn't. After removing what the hour's own return explains, the residual still has a next-hour rank IC of 0.014 (t 6.2), and it adds over the reversal signal by about the same amount. But the effect lasts about one bar. At the skipped bar, the pre-registered primary test, the IC is 0.004 (t 1.7, Holm p 0.27). The audit's lag test is exactly that delay, and it fails.

Even without the extra lag, the strategy can't pay for itself. The gross edge is real but small, and acting on an hourly, fast-decaying signal means turnover of 0.3–1.4 of the book per hour. Break-even fees are under half a basis point in all nine pre-registered cells, against 5 bps paid. Smoothing cuts turnover, but it averages away the gross edge faster: break-even falls from about 0.40 bps at k = 1 to about 0.23 bps at k = 24.

This matches the stated prior. The close-to-VWAP gap behaves like a short-lived microstructure effect, close to bid-ask bounce: predictable, but not tradeable at taker fees with an hour's delay. A REJECT on the full grid is the honest result.
