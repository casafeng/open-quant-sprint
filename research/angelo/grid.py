"""Track 07 Part 2, item (d): the 9 pre-registered strategy cells.

Run from the repo root:  .venv/bin/python research/angelo/grid.py
Writes research/angelo/grid_results.csv and research/angelo/grid_results.md.

Grid (pre-registered, PR #9): span k in {1, 6, 24} x deadband b in {0.005, 0.015, 0.03}; primary k=6, b=0.015.
Test statistic: net Sharpe at 5 bps on the full panel, t = SR * sqrt(years); Holm over the 9 cells.
p-values are two-sided, the same convention as the IC study. Also reported, not tested: gross (0 bps)
Sharpe, lag-2 Sharpe at 5 bps (the audit's lag test), turnover, and the break-even fee.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.backtest import run_backtest  # noqa: E402
from strategies.angelo_closeloc import build_weights  # noqa: E402

OUT = Path(__file__).resolve().parent
SPANS = (1, 6, 24)
BANDS = (0.005, 0.015, 0.03)
PRIMARY = (6, 0.015)


def holm(p: list[float]) -> list[float]:
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[i]))
        adj[i] = running
    return adj.tolist()


def main() -> None:
    df = pd.read_parquet(ROOT / "data/train_1h.parquet")
    years = df["timestamp"].nunique() / 8760.0
    rows = []
    for k in SPANS:
        for b in BANDS:
            w = build_weights(df, k, b)
            m5 = run_backtest(df, w, fee_bps=5.0)
            m0 = run_backtest(df, w, fee_bps=0.0)
            lag = run_backtest(df, w, fee_bps=5.0, lag_bars=2)
            fee_per_bps = m5.fee_cost_cum / 5.0
            breakeven = (m5.gross_pnl_cum - m5.funding_cost_cum) / fee_per_bps if fee_per_bps > 0 else np.nan
            t = m5.sharpe * np.sqrt(years)
            rows.append({
                "span": k, "deadband": b, "primary": (k, b) == PRIMARY,
                "sharpe_5bps": m5.sharpe, "ci_low": m5.sharpe_ci_low, "ci_high": m5.sharpe_ci_high,
                "t": t, "p": 2 * stats.norm.sf(abs(t)),
                "sharpe_0bps": m0.sharpe, "sharpe_lag2_5bps": lag.sharpe,
                "turnover": m5.mean_turnover, "breakeven_bps": breakeven,
            })
            print(rows[-1], flush=True)
    res = pd.DataFrame(rows)
    res["p_holm"] = holm(res["p"].tolist())
    res.to_csv(OUT / "grid_results.csv", index=False)
    show = res.copy()
    show["cell"] = show.apply(lambda r: f"k={r.span}, b={r.deadband}" + (" **(primary)**" if r.primary else ""), axis=1)
    cols = ["cell", "sharpe_5bps", "ci_low", "ci_high", "p_holm", "sharpe_0bps", "sharpe_lag2_5bps", "turnover", "breakeven_bps"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in show[cols].iterrows():
        lines.append("| " + " | ".join(
            v if isinstance(v, str) else (f"{v:.2e}" if 0 < abs(v) < 1e-3 else f"{v:.3f}") for v in r) + " |")
    (OUT / "grid_results.md").write_text(
        "# Strategy grid (pre-registered, item d)\n\nNet Sharpe at 5 bps, full panel; Holm over 9 cells; two-sided.\n\n"
        + "\n".join(lines) + "\n")
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
