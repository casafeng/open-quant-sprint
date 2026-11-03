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
