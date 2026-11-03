"""Track 07 Part 2, item (a): IC study exactly as pre-registered in research/angelo/PREREGISTRATION.md.

Run from the repo root:  .venv/bin/python research/angelo/ic_study.py
Writes research/angelo/ic_results.csv and research/angelo/ic_results.md.

Pre-registered spec (copied, not changed):
- Signals: S_res = -close_location_residual (tested); S_raw = -close_location (comparison, not tested).
- Horizons, close-to-close log returns from close_t: h = 1, 2, 4, 8, 24, plus skip-1 = close_{t+1} -> close_{t+2}.
- Statistic: mean per-timestamp Spearman IC. h = 1 and skip-1: plain t-stat on per-hour ICs.
  h >= 2: Newey-West with h-1 lags, and every h-th hour reported as a cross-check.
- Increment over reversal: per-timestamp regression of forward-return ranks on ranks of S_res and -r_t;
  report the S_res coefficient (Fama-MacBeth t).
- Holm over the 6 S_res horizons. Primary IC cell: S_res, skip-1.

Choices the pre-registration left open, fixed here before the first run:
- p-values are two-sided (normal approximation; T is ~14,800 hours).
- The increment regression is run at every horizon and uses the same t-stat rule as the IC
  (plain for h = 1 and skip-1, Newey-West h-1 lags for h >= 2). Its p-values are reported, not Holm-tested.
- A timestamp counts if at least 5 symbols have a finite signal and forward return.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.contrib.angelo import bar_log_return, close_location, close_location_residual  # noqa: E402

OUT = Path(__file__).resolve().parent
HORIZONS = ["1", "2", "4", "8", "24", "skip1"]
MIN_N = 5


def wide(df: pd.DataFrame, s: pd.Series) -> np.ndarray:
    return (
        pd.DataFrame({"t": df["timestamp"], "s": df["symbol"], "v": s.to_numpy()})
        .pivot(index="t", columns="s", values="v")
        .to_numpy(dtype=np.float64)
    )


def row_ranks(x: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Average ranks per row over masked entries; NaN elsewhere. Rows centred to mean 0."""
    xm = np.where(mask, x, np.nan)
    r = pd.DataFrame(xm).rank(axis=1, method="average").to_numpy()
    return r - np.nanmean(r, axis=1, keepdims=True)


def per_hour_ic(sig: np.ndarray, fwd: np.ndarray) -> np.ndarray:
    mask = np.isfinite(sig) & np.isfinite(fwd)
    n = mask.sum(axis=1)
    a = np.nan_to_num(row_ranks(sig, mask))
    b = np.nan_to_num(row_ranks(fwd, mask))
    num = (a * b).sum(axis=1)
    den = np.sqrt((a * a).sum(axis=1) * (b * b).sum(axis=1))
    ic = np.where((n >= MIN_N) & (den > 1e-12), num / np.where(den > 0, den, 1.0), np.nan)
    return ic


def per_hour_increment(sig: np.ndarray, rev: np.ndarray, fwd: np.ndarray) -> np.ndarray:
    """Slope on rank(sig) in rank(fwd) ~ 1 + rank(sig) + rank(rev), per hour, ranks scaled to unit sd."""
    mask = np.isfinite(sig) & np.isfinite(rev) & np.isfinite(fwd)
    n = mask.sum(axis=1)
    y = np.nan_to_num(row_ranks(fwd, mask))
    x1 = np.nan_to_num(row_ranks(sig, mask))
    x2 = np.nan_to_num(row_ranks(rev, mask))
    sd = lambda z: np.sqrt((z * z).sum(axis=1) / np.maximum(n - 1, 1))[:, None]  # noqa: E731
    y, x1, x2 = y / np.where(sd(y) > 0, sd(y), 1), x1 / np.where(sd(x1) > 0, sd(x1), 1), x2 / np.where(sd(x2) > 0, sd(x2), 1)
    s11, s22, s12 = (x1 * x1).sum(1), (x2 * x2).sum(1), (x1 * x2).sum(1)
    s1y, s2y = (x1 * y).sum(1), (x2 * y).sum(1)
    det = s11 * s22 - s12 * s12
    b1 = (s22 * s1y - s12 * s2y) / np.where(np.abs(det) > 1e-12, det, np.nan)
    return np.where(n >= MIN_N, b1, np.nan)


def t_plain(x: np.ndarray) -> tuple[float, float, int]:
    x = x[np.isfinite(x)]
    m = x.mean()
    se = x.std(ddof=1) / np.sqrt(len(x))
    return m, m / se, len(x)


def t_newey_west(x: np.ndarray, lags: int) -> tuple[float, float, int]:
    x = x[np.isfinite(x)]
    n = len(x)
    m = x.mean()
    e = x - m
    var = (e @ e) / n
    for k in range(1, lags + 1):
        w = 1.0 - k / (lags + 1.0)
        var += 2.0 * w * (e[k:] @ e[:-k]) / n
    return m, m / np.sqrt(var / n), n


def forward_returns(lc: np.ndarray) -> dict[str, np.ndarray]:
    out = {}
    T = lc.shape[0]
    for h in (1, 2, 4, 8, 24):
        f = np.full_like(lc, np.nan)
        f[: T - h] = lc[h:] - lc[: T - h]
        out[str(h)] = f
    f = np.full_like(lc, np.nan)
    f[: T - 2] = lc[2:] - lc[1 : T - 1]
    out["skip1"] = f
    return out


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
    s_res = wide(df, -close_location_residual(df))
    s_raw = wide(df, -close_location(df))
    rev = wide(df, -bar_log_return(df))
    lc = wide(df, np.log(df["close"]))
    fwd = forward_returns(lc)

    rows = []
    for name, sig in (("S_res", s_res), ("S_raw", s_raw)):
        for h in HORIZONS:
            ic = per_hour_ic(sig, fwd[h])
            lags = 0 if h in ("1", "skip1") else int(h) - 1
            m, t, n = t_plain(ic) if lags == 0 else t_newey_west(ic, lags)
            row = {"signal": name, "horizon": h, "mean_ic": m, "t": t, "p": 2 * stats.norm.sf(abs(t)), "n_hours": n,
                   "t_method": "plain" if lags == 0 else f"NW({lags})"}
            if lags > 0:  # every h-th hour cross-check
                sub = ic[:: int(h)]
                ms, ts, ns = t_plain(sub)
                row.update({"nonoverlap_ic": ms, "nonoverlap_t": ts, "nonoverlap_n": ns})
            if name == "S_res":
                inc = per_hour_increment(sig, rev, fwd[h])
                mi, ti, _ = t_plain(inc) if lags == 0 else t_newey_west(inc, lags)
                row.update({"incr_coef": mi, "incr_t": ti, "incr_p": 2 * stats.norm.sf(abs(ti))})
            rows.append(row)

    res = pd.DataFrame(rows)
    tested = res["signal"] == "S_res"
    res.loc[tested, "p_holm"] = holm(res.loc[tested, "p"].tolist())
    res["primary"] = (res["signal"] == "S_res") & (res["horizon"] == "skip1")
    res.to_csv(OUT / "ic_results.csv", index=False)

    fmt = res.copy()
    for c in fmt.columns:
        if fmt[c].dtype.kind == "f":
            fmt[c] = fmt[c].map(lambda v: "" if pd.isna(v) else (f"{v:.2e}" if abs(v) < 1e-3 and v != 0 else f"{v:.4f}"))
    md = ["# IC study (pre-registered, item a)", "",
          f"Panel: data/train_1h.parquet, {df['timestamp'].nunique()} hours x {df['symbol'].nunique()} symbols.",
          "Primary cell: S_res, skip1. Holm over the 6 S_res horizons; S_raw is comparison only.", "",
          "```", fmt.to_string(index=False), "```"]
    (OUT / "ic_results.md").write_text("\n".join(md) + "\n")
    print(res.to_string(index=False))


if __name__ == "__main__":
    main()
