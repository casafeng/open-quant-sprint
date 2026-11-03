<!-- Copy of the PR #9 description (https://github.com/valiyevoktay-cmd/open-quant-sprint/pull/9), the pre-registration for Track 07 Part 2. -->

## Pre-registration (posted 2026-11-03 22:20 UTC, before any full-panel run)

Track 07 Part 2 (#7). Features from #8. This draft holds only the pre-registered grid: no IC, no backtest has been run on the full panel yet. `strategies/angelo_closeloc.py`, the measurements and the audit output will be added to this PR afterwards, evaluated against the grid below without changes.

## Hypothesis
H1: `-close_location_residual` (the close-to-VWAP gap after removing the hour's own return) has positive cross-sectional rank IC with future close-to-close returns, beyond plain reversal.
H2 (the one that pays): enough of it survives a one-hour execution lag and 5 bps fees for a dollar-neutral strategy to have net Sharpe > 0.
Prior: most of the effect sits in the next bar (a bounce-like effect), so I expect the IC to be gone at the skipped bar and the strategy to REJECT on the lag test.

## Measurement grid (IC)
- Signals: S_res = -close_location_residual (tested); S_raw = -close_location (comparison, reported but not tested).
- Horizons, close-to-close log returns from close_t: h = 1, 2, 4, 8, 24, plus "skip-1" = close_{t+1} to close_{t+2}.
- Statistic: mean per-timestamp Spearman IC. h = 1 and skip-1 use plain t-stats on per-hour ICs. For h >= 2, Newey-West with h-1 lags, and every h-th hour reported as a cross-check.
- Increment over reversal: per-timestamp regression of the forward return ranks on the ranks of S_res and -r_t. Report the S_res coefficient (Fama-MacBeth t).
- Correction: Holm over the 6 S_res horizons. **Primary IC cell: S_res, skip-1** (the lag test needs it).

## Strategy grid (`strategies/angelo_closeloc.py`)
Signal: EWM(span k) of close_location_residual per symbol, re-residualized at each timestamp on the k-hour log return over the same window (so the averaged gap does not turn into plain reversal). Then sign-flipped, `cross_sectional_zscore`, and `rebalance_deadband(b)`.
- k ∈ {1, 6, 24}
- b ∈ {0.005, 0.015, 0.03}
- 9 cells. **Primary cell: k = 6, b = 0.015.**
- Test statistic: net Sharpe at 5 bps on the full panel. Holm over the 9 cells (t = SR·√years, the block-bootstrap interval is reported too).
- Report for the primary cell: full audit output, lag-test Sharpe, fee rows (0/3/5/10 bps, tiered), turnover, break-even fee, wick share.
- No cells added after the first run. Any other variant goes in the write-up as exploratory, not tested.

## Audit Scorecard Output
_Pending: added after the first run._

## Empirical Notes
_Pending._

🤖 Generated with [Claude Code](https://claude.com/claude-code)

