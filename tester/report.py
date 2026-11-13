"""Reads every settled trade file and writes data/summary.csv and reports/summary.md."""
import glob
import math
from pathlib import Path

import numpy as np
import pandas as pd

COST_PCT = 0.0         # round-trip cost in % of price, subtracted from each trade here (not stored in the files)
THIN = 30              # fewer trades than this = too thin to judge
FLIP_ITER = 4000


def load_trades(trades_dir):
    files = sorted(glob.glob(str(Path(trades_dir) / "*.csv")))
    frames = [pd.read_csv(f) for f in files if Path(f).stat().st_size > 20]
    frames = [f for f in frames if len(f)]
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df["ret_pct"] = df["ret_pct"] - COST_PCT
    df["ret_atr"] = df["ret_pct"] / df["atr_pct"]
    return df


def wilson(wins, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = wins / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (mid - half, mid + half)


def flip_p(x, seed=1):
    x = np.asarray(x, float)
    if len(x) < 8:
        return np.nan
    s = np.random.default_rng(seed).choice([-1.0, 1.0], size=(FLIP_ITER, len(x)))
    return float(((s * np.abs(x)).mean(axis=1) >= x.mean()).mean())


def summarize(df):
    rows = []
    for (kind, variant), g in df.groupby(["kind", "variant"]):
        n = len(g)
        w = g[g.ret_atr > 0]
        l = g[g.ret_atr <= 0]
        lo, hi = wilson(len(w), n)
        daily = g.groupby("date").ret_atr.mean()
        aw, al = (w.ret_atr.mean() if len(w) else np.nan), (l.ret_atr.mean() if len(l) else np.nan)
        rows.append(dict(kind=kind, variant=variant, group=g["group"].iloc[0], n=n, days=g.date.nunique(),
                         win_pct=100 * len(w) / n, win_lo=100 * lo, win_hi=100 * hi,
                         avg_ret_pct=g.ret_pct.mean(), avg_atr=g.ret_atr.mean(),
                         avg_win=aw, avg_loss=al, payoff=(aw / abs(al)) if al and not np.isnan(al) else np.nan,
                         mfe=g.mfe_atr.mean(), mae=g.mae_atr.mean(), bars_held=g.bars_held.mean(),
                         p_luck=flip_p(daily)))
    s = pd.DataFrame(rows)
    ctrl = s[s.variant == "control_random"].set_index("kind").avg_atr
    s["vs_control"] = s.apply(lambda r: r.avg_atr - ctrl.get(r.kind, np.nan), axis=1)
    return s


def md(df, floatfmt=2):
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            cells.append("" if (isinstance(v, float) and np.isnan(v)) else
                         f"{v:.{floatfmt}f}" if isinstance(v, (float, np.floating)) else str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def verdict(r):
    if r.variant == "control_random":
        return "control"
    if r.n < THIN or r.days < 8:
        return "too thin"
    if r.vs_control > 0 and r.avg_atr > 0 and r.p_luck < 0.10:
        return "edge? (beats control, p<0.10)"
    if r.vs_control > 0 and r.avg_atr > 0:
        return "beats control, could be luck"
    return "no edge"


def hold_curve(df, variant="score_setup_70"):
    pc = [c for c in df.columns if c.startswith("p") and c[1:].isdigit()]
    rows = []
    for kind, g in df[df.variant == variant].groupby("kind"):
        rows.append(dict(kind=kind, n=len(g), **{f"+{c[1:]}": g[c].mean() for c in pc}))
        rows.append(dict(kind=kind + " % up", n=len(g), **{f"+{c[1:]}": 100 * (g[c] > 0).sum() / max(g[c].notna().sum(), 1) for c in pc}))
    return pd.DataFrame(rows)


def write_reports(trades_dir, data_dir, reports_dir, quality=None):
    df = load_trades(trades_dir)
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    if df.empty:
        Path(reports_dir, "summary.md").write_text("# Strategy tester\n\nNo settled trades yet.\n")
        return
    s = summarize(df)
    s["verdict"] = s.apply(verdict, axis=1)
    s.round(4).to_csv(Path(data_dir) / "summary.csv", index=False)
    kinds = ["forward", "replay"]
    lines = ["# Strategy tester summary", "",
             f"Updated through **{df.date.max()}** | {df.date.nunique()} trading days | {len(df):,} hypothetical trades "
             f"| {s.variant.nunique()} variants", "",
             "`avg_atr` is the average move in your direction, measured in daily-ATR units (the stock's move, not option P&L). "
             "`vs_control` subtracts the random 1H-ribbon control. `p_luck` is the chance noise alone matches the result, "
             "counted over days. Win-rate range = 95% interval.", "",
             f"With {s.variant.nunique() - 1} variants compared, a few will look good by chance. "
             "Trust a variant only if it also holds in `forward` data (real-time, never tuned on).", ""]
    cols = ["variant", "n", "days", "win_pct", "win_lo", "win_hi", "avg_atr", "vs_control", "payoff",
            "bars_held", "p_luck", "verdict"]
    for kind in kinds:
        k = s[s.kind == kind]
        if k.empty:
            continue
        title = {"forward": "Forward test (real time, after the strategy was frozen)",
                 "replay": "Replay (history re-run through the same rules)"}[kind]
        lines += [f"## {title}", ""]
        for grp, gg in k.groupby("group", sort=False):
            lines += [f"### {grp}", "", md(gg.sort_values("avg_atr", ascending=False)[cols]), ""]
    hc = hold_curve(df)
    if len(hc):
        lines += ["## Where does the move peak? (entries with opp >= 70 and a setup)", "",
                  "Average move in ATR units at +N bars after entry (15m bars) and the percent of trades that are up.", "",
                  md(hc, 2), ""]
    if quality is not None and len(quality):
        lines += ["## Live vs recomputed (data quality)", "", md(quality.tail(10), 0), ""]
    Path(reports_dir, "summary.md").write_text("\n".join(lines))
