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

## Results (added after the run; the grid and primary cells above are unchanged)

**Verdict: REJECT.** Full write-up: `research/angelo/RESULTS.md`. Scripts and outputs: `research/angelo/`.

- **IC, primary cell (S_res, skip-1):** 0.0038, t 1.69, Holm p 0.27, not significant. At the next bar: IC 0.0141, t 6.2, and the residual adds over plain reversal by about the same (FM t 6.2). At h = 8 and 24 the IC is not distinguishable from zero.
- **Strategy, primary cell (k = 6, b = 0.015):**
  - Net Sharpe: 0 bps +1.48 [−0.09, 2.96]; 3 bps −9.93; 5 bps −17.51; 10 bps −36.30; tiered −28.15.
  - Lag-test Sharpe: −19.20.
  - Turnover 0.723 per hour. Break-even fee about 0.39 bps. Wick share 2.8%.
- **Grid:** all 9 cells are negative at 5 bps (−6.9 to −30.0), with every interval below 0. Gross Sharpe is positive in every cell. Break-even fees are 0.23–0.45 bps. No cell supports H2.

## Audit Scorecard Output
```text
========================================================================
SYNDICATE AUDIT REPORT :: angelo_closeloc.py
========================================================================
    audit v1.3.1 | commit 9cdc22d | strategy sha256 36ef8fd2175f8391
    data sha256 d68e6159bbdfb2e3
    causality seed 2228275014 | random cuts 8 (reproduce with --seed 2228275014)
    strategy process: host process
[1] DATA QUALITY     : DQS=99.93/100 (READY) | rows=297420 | symbols=20 | gaps=0 | funding_irreg=0
[2] CAUSALITY CHECK  : [PASS] Causal invariance verified across 14 prefix cuts (max diff=0.00e+00, seed=2228275014)
[3] RANK IC (1h fwd) : mean=+0.01100 | IC_IR=+0.042 | t=+5.10 (p=0.0000)
[4] RUNTIME          : 1949.1 ms (152,591 rows/sec)
------------------------------------------------------------------------
[5] TRANSACTION COST DECAY MATRIX (1-bar lag + funding included):
    Fee (bps)      Sharpe     95% CI (block bootstrap)  DSR(N=10)   Ann.Ret     MaxDD  Turnover
       0.0 bps      +1.48  [-0.09, +2.96] (includes 0)      0.682   +24.61%   -25.54%    0.7232
       3.0 bps      -9.93              [-11.54, -8.43]      0.000  -165.46%  -281.90%    0.7232
       5.0 bps     -17.51             [-19.25, -15.95]      0.000  -292.17%  -496.47%    0.7232
      10.0 bps     -36.30             [-38.37, -34.44]      0.000  -608.96% -1033.85%    0.7232
    tiered ~7.7    -28.15             [-30.00, -26.41]      0.000  -470.94%  -799.58%    0.7232
    tiered = BTC/ETH 5 bps, 6 least liquid by trailing 30d volume 10 bps, others 7 bps
------------------------------------------------------------------------
[6] PURGED SPLIT (70% In-Sample / 24h Embargo / 30% Out-of-Sample @ 5.0 bps):
    In-Sample     : Sharpe=-18.14 [-20.14, -16.33] | DSR=0.000 | Ann.Ret=-295.53% | MaxDD=-351.90%
    Out-of-Sample : Sharpe=-16.30 [-18.96, -13.69] | DSR=0.000 | Ann.Ret=-286.76% | MaxDD=-145.53%
------------------------------------------------------------------------
[7] LAG SENSITIVITY TEST (+1 extra bar execution lag @ 5.0 bps):
    1-bar lag SR  : -17.51 | 2-bar lag SR: -19.20 | Retention: 0.0% [FAIL - microstructure decay / half-life < 1h]
[8] NULL PIPELINE CHECK (200 daily-block permutations of returns):
    Null SR mean  : +0.01 (sd 0.72, hurdle |mean| < 0.75) [PASS]
    Gross SR vs null: p=0.0199 (in-sample, informational only)
[9] FRICTION DRAG BREAKDOWN (@ 5.0 bps taker fee):
    Gross PnL     : +42.72%
    Fee Cost      : +537.77%
    Funding Drag  : +0.94%
    Net PnL       : -495.99%
[10] WICK & MARK INTEGRITY (liquidation wick / bad mark hurdle <= 20.0%):
    Wick PnL Share: 2.8% (3223 anomaly bars) [PASS - structural flow]
------------------------------------------------------------------------
[11] EXECUTION REALISM & MODEL BOUNDARIES:
    Fills         : signal on the close of bar t, filled at that close; lag-2 test = one hour of real delay
    Costs         : flat taker fee grid + tiered row, snapshot funding on the position held across settlement
    Scope Caveat  : Excludes orderbook queueing, depth-scaled impact (Almgren-Chriss), & adverse selection
[12] CORRELATION    : hourly net returns vs baseline_flow.py @ 5 bps = +0.09
[13] REVIEW FLAGS   : none (manual review, not part of the verdict)
========================================================================
FINAL VERDICT: [REJECT] FAILED AUDIT
========================================================================
```

## Empirical Notes
What worked: the feature does what it was built for. After removing the hour's own return, where the close sits against the VWAP still predicts the next hour (rank IC 0.014, t 6.2). It adds to plain one-bar reversal rather than repeating it.

What broke: the effect lasts about one bar. At the pre-registered primary test, the return one hour later, the IC is 0.004 (Holm p 0.27), so the audit's lag test fails at −19.2. Even without the extra hour, the trade can't pay for itself. Acting on a signal that decays this fast turns over 0.3–1.4 of the book per hour, and break-even fees are under 0.5 bps in all nine pre-registered cells, against 5 bps paid. Smoothing lowers turnover but removes the gross edge faster.

Why: the close-to-VWAP gap behaves like a short-lived microstructure effect, close to bid-ask bounce. It is predictable, but at taker fees and with an hour's delay it doesn't pay. This matches the prior stated before the run, and the result is reported as pre-registered, without tuning.

## Local Verification Checklist
- [x] `python -m pytest -q`: 41 passed
- [x] `python -m src.audit strategies/angelo_closeloc.py` run, output above (REJECT)
- [x] The strategy reads only `df`. No file, network or environment access, no imports of `src.audit`, `src.backtest` or `src.sandbox`.
- [x] No `iterrows`/`itertuples`. The deadband loop is the shared `src.features.rebalance_deadband`.
- [x] I license this contribution under the MIT License (`LICENSE`).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
