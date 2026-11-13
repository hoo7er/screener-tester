"""Picks hypothetical entries for each variant and simulates the exits on 15m bars."""
import zlib
from types import SimpleNamespace

import numpy as np
import pandas as pd

from .variants import (GAP_SKIP_ATR, HOLD_BARS, MAX_PER_DAY, MAX_PER_SECTOR, SL_ATR, TOP_N, TP_ATR, TRAIL_ATR,
                       VARIANTS)

PATH_BARS = 16      # records the move at +1 ... +16 bars after entry (shows where the edge peaks)


def _mask(df, v):
    m = np.asarray(v["mask"](df), bool) & df.mins.between(*v["window"]).values
    return m & (df.gap_atr <= GAP_SKIP_ATR).values


def live_flags(df):
    """For the latest bars: which variants would consider each row (no next bar needed)."""
    vs = [v for v in VARIANTS if not v.get("select")]     # snapshot-style testers are not flagged bar by bar
    names = np.array([v["name"] for v in vs])
    hits = np.column_stack([_mask(df, v) for v in vs])
    return [",".join(names[r]) for r in hits]


def _directions(df, v):
    return np.asarray(v["dirfn"](df)) if v["dirfn"] else df["dir"].values


def _pick_dashboard(df, v):
    """The screener dashboard's top-N: setups first, then checklist score, then opp, max 2 per sector."""
    m = _mask(df, v) & df.entry.notna().values
    if not m.any():
        return df.iloc[0:0].assign(side=[])
    c = df[m].assign(side=df["dir"].values[m], tier_n=df.setup.values[m].astype(int))
    c = c.sort_values(["tier_n", "chk", "opp", "ticker"], ascending=[False, False, False, True])
    sec = c["sector"] if "sector" in c.columns else c["ticker"]
    counts, out = {}, []
    for idx, s, t in zip(c.index, sec, c["ticker"]):
        s = t if (not isinstance(s, str) or s in ("", "Unknown")) else s     # unknown sector = its own group
        if counts.get(s, 0) >= MAX_PER_SECTOR:
            continue
        counts[s] = counts.get(s, 0) + 1
        out.append(idx)
        if len(out) == TOP_N:
            break
    return c.loc[out]


def _pick(df, v, day):
    if v.get("select") == "dashboard":
        return _pick_dashboard(df, v)
    m = _mask(df, v) & df.entry.notna().values
    if not m.any():
        return df.iloc[0:0].assign(side=[])
    c = df[m].assign(side=_directions(df, v)[m])
    if v["rand"]:
        seed = zlib.crc32(f"{day}".encode())
        c = c.assign(key=np.random.default_rng(seed).random(len(c)))
    else:
        c = c.assign(key=c.opp)
    c = c.sort_values(["end", "key"], ascending=[True, False])
    taken, out = set(), []
    for idx, r in zip(c.index, c.itertuples()):
        if len(out) >= MAX_PER_DAY:
            break
        if r.ticker in taken:
            continue
        taken.add(r.ticker)
        out.append(idx)
    return c.loc[out]


def _simulate(g, pos, d, rule, atr):
    """g = one ticker's bars for the day (sorted). Decision at the close of bar `pos`; fill at the next open."""
    last = len(g.close_) - 1
    entry = g.open_[pos + 1]
    cl, op, hi, lo = g.close_, g.open_, g.high_, g.low_
    ex_idx, ex_price, reason = last, cl[last], "eod"
    ex_time = g.end_[last]
    if rule in HOLD_BARS:
        j = pos + HOLD_BARS[rule]
        if j <= last:
            ex_idx, ex_price, reason, ex_time = j, cl[j], rule, g.end_[j]
    elif rule != "eod":
        peak = 0.0
        for j in range(pos + 1, last):
            ret = d * (cl[j] / entry - 1) * 100 / atr
            peak = max(peak, ret)
            hit = None
            if rule == "trail" and peak - ret >= TRAIL_ATR:
                hit = "trail"
            elif rule == "tpsl":
                hit = "tp" if ret >= TP_ATR else "sl" if ret <= -SL_ATR else None
            elif rule == "momturn" and g.mcol_[j] != ("aqua" if d == 1 else "red"):
                hit = "momturn"
            elif rule == "ribflip" and g.rib_[j] != ("lime" if d == 1 else "red"):
                hit = "ribflip"
            if hit:
                ex_idx, ex_price, reason, ex_time = j, op[j + 1], hit, g.end_[j]
                break
    seg = slice(pos + 1, ex_idx + 1)
    if d == 1:
        fav, adv = hi[seg].max() / entry - 1, lo[seg].min() / entry - 1
    else:
        fav, adv = 1 - lo[seg].min() / entry, 1 - hi[seg].max() / entry
    path = [d * (cl[pos + k] / entry - 1) * 100 / atr if pos + k <= last else np.nan for k in range(1, PATH_BARS + 1)]
    ret = d * (ex_price / entry - 1) * 100
    return dict(exit_time=ex_time, exit=ex_price, reason=reason, ret_pct=ret, ret_atr=ret / atr,
                mfe_atr=fav * 100 / atr, mae_atr=adv * 100 / atr, bars_held=ex_idx - pos), path


def run_day(day_df, day, kind, only=None):
    """All variants' hypothetical trades for one trading day."""
    df = day_df.sort_values(["ticker", "end"]).reset_index(drop=True)
    tick = {}
    for t, g in df.groupby("ticker"):
        tick[t] = SimpleNamespace(
            end_=list(g.end), open_=g.open.values, high_=g.high.values, low_=g.low.values,
            close_=g.close.values, mcol_=g.mcol.values, rib_=g.rib.values,
            pos={ts: i for i, ts in enumerate(g.end)})
    rows = []
    for v in VARIANTS:
        if only is not None and v["name"] not in only:
            continue
        for idx, r in _pick(df, v, day).iterrows():
            g = tick[r.ticker]
            pos = g.pos[r.end]
            if pos + 1 >= len(g.close_):
                continue
            side = int(r.side)
            res, path = _simulate(g, pos, side, v["exit"], r.atr)
            vkind = kind if (not v.get("since") or str(day) >= v["since"]) else "replay"
            rows.append(dict(date=day, kind=vkind, variant=v["name"], group=v["group"], ticker=r.ticker,
                             side="CALL" if side == 1 else "PUT", decision_end=r.end,
                             entry=g.open_[pos + 1], atr_pct=r.atr, opp=round(r.opp, 1), setup=bool(r.setup),
                             sq=r.sq, fired=r.fired, tight=r.tight, run_dir=r.run_dir, rib_1h=r.rib_1h,
                             mcol=r.mcol, **res, **{f"p{k + 1}": round(x, 3) for k, x in enumerate(path)}))
    return pd.DataFrame(rows)
