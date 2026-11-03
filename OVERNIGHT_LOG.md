# Overnight log, Track 07 Part 2 (branch feat/angelo-closeloc, local only, no pushes)

Spec: research/angelo/PREREGISTRATION.md (copy of PR #9). Grid and primary cells are fixed; nothing below changes them.

## 2026-11-03 23:35 CET: item (a) IC study, done
- Script: research/angelo/ic_study.py; outputs ic_results.csv / ic_results.md.
- Choices the pre-registration left open, fixed in the script docstring before running: two-sided p-values; the increment regression is run at every horizon with the same t rule; at least 5 symbols per hour.
- PRIMARY (S_res, skip-1): mean IC 0.0038, t 1.69, p 0.090, Holm p 0.27 -> not significant.
- S_res h=1: IC 0.0141, t 6.21 (Holm p 3e-9). h=2: 0.0131, NW t 5.85. h=4: 0.0072, NW t 3.22. h=8: 0.0028 (t 1.23). h=24: -0.0032 (t -1.48).
- Increment over -r_t (rank FM slope): h=1 0.0143 (t 6.18), skip-1 0.0034 (t 1.51). So the residual adds to plain reversal at the next bar, but not at the skipped bar.
- S_raw (comparison only, not tested): h=1 IC 0.031 (t 12.7), skip-1 0.0117 (t 4.87). The raw gap is mostly reversal, and that reversal lasts longer than the residual's effect.
- Read: H1 holds at h=1-4, but the effect is mostly gone one bar later, as the stated prior expected. Expect the lag test to fail.
- Next: item (b) strategy file.

## 2026-11-03 23:45 CET: items (b) and (c), done
- src/contrib/angelo.py: added smoothed_close_location_residual(df, span), the pre-registered signal: per-symbol EWM(span) of the residual, re-residualized per timestamp on the span-hour log return.
- strategies/angelo_closeloc.py: -signal -> cross_sectional_zscore -> rebalance_deadband. Primary cell SPAN=6, DEADBAND=0.015 hard-coded.
- tests/contrib/test_angelo.py: +3 tests (span 1 equals the residual; for spans 6 and 24, zero mean and zero cov with the span-hour return, plus prefix causality).
- Full suite: `.venv/bin/python -m pytest -q`: 41 passed.
- Next: item (d) audit of the primary cell, then the 9-cell grid.

## 2026-11-03 23:55 CET: item (d), done
- Audit of the primary cell (research/angelo/audit_primary.txt, seed 2228275014): FINAL VERDICT REJECT.
  Causality PASS (14 cuts), DQS 99.93, 1h rank IC +0.0110 (t 5.10).
  Sharpe 0/3/5/10/tiered bps: +1.48 [-0.09, 2.96] / -9.93 / -17.51 / -36.30 / -28.15. Turnover 0.723 per hour.
  OOS 30% @5bps -16.30. Lag test: 2-bar SR -19.20, FAIL. Null check PASS (+0.01). Wick share 2.8%, PASS.
  Gross +42.7% vs fees 537.8% at 5 bps -> break-even about 0.39 bps.
- Grid (research/angelo/grid.py, grid_results.csv/.md): all 9 cells have negative net Sharpe at 5 bps (-6.9 to -30.0), all CIs below 0.
  Holm-adjusted p < 1e-18 for every cell, but every one of those is for a NEGATIVE Sharpe, so no cell supports H2.
  Gross Sharpe (0 bps) is positive in every cell: k=1 about 2.6, k=6 about 1.5, k=24 about 0.35-0.57. Break-even fee 0.23-0.45 bps. Turnover 0.27-1.41 per hour.
- Proposal (NOT run, NOT part of the result): a holding rule that only trades when |signal| is extreme, or spans of 48h or more, would cut turnover. Given the gross Sharpe falls as the span grows and the skip-1 IC is about 0, I don't expect either to clear 5 bps. Left as a note for the write-up.
- Next: item (e) RESULTS.md.
