"""Indicator ports and the feature panel. The indicator math is copied from the screener notebook
(Beardy Squeeze Pro + HMA-Kahlman), so live testing uses the exact same signals."""
import math
import os

import numpy as np
import pandas as pd

NY = "America/New_York"

# ---------------- Settings (same as the notebook) ----------------
SQ_LENGTH, BB_MULT, KC_MULTS = 20, 1.5, (1.0, 1.5, 2.0)
HMA_LENGTH, KAHLMAN_GAIN = 22, 0.7
FIRE_WINDOW = 4          # a squeeze that fired within this many bars counts as "fresh"
MIN_TIGHT_BARS = 4       # a fire only counts if orange/red showed this many bars before it
MIN_SCORE = 5            # of 6, needed to call a side a "setup"
WARMUP_BARS = 60
MAX_DAYS = 60            # trading days of bars used for indicators (same in live and settle)
CUR_W = np.array([40, 25, 10, 15, 10], float)   # opp weights: checks, timing, momentum, extension, movement


def now_et():
    """Current time in ET. TESTER_NOW (e.g. '2026-11-13 16:30') overrides it for testing."""
    o = os.environ.get("TESTER_NOW")
    if o:
        return pd.Timestamp(o).tz_localize(NY)
    return pd.Timestamp.now(tz=NY)


# ---------------- Indicator ports ----------------
def wma(s, n):
    n = int(n)
    w = np.arange(1, n + 1)
    return s.rolling(n).apply(lambda x: np.dot(x, w) / w.sum(), raw=True)


def hma(x, n):
    return wma(2 * wma(x, n / 2) - wma(x, n), round(math.sqrt(n)))


def hma3(x, n):
    p = n / 2
    return wma(3 * wma(x, p / 3) - wma(x, p / 2) - wma(x, p), p)


def kahlman(x, g):
    out = np.full(len(x), np.nan)
    kf_prev, velo_prev = None, 0.0
    for i, xv in enumerate(x):
        if np.isnan(xv):
            continue
        base = xv if kf_prev is None else kf_prev
        dk = xv - base
        smooth = base + dk * math.sqrt(g * 2)
        velo = velo_prev + g * dk
        kf_prev, velo_prev = smooth + velo, velo
        out[i] = kf_prev
    return out


def ribbon(d):
    price = (d["High"] + d["Low"]) / 2
    a = pd.Series(kahlman(hma(price, HMA_LENGTH).values, KAHLMAN_GAIN), index=d.index)
    b = pd.Series(kahlman(hma3(d["Close"], HMA_LENGTH).values, KAHLMAN_GAIN), index=d.index)
    return a, b


def linreg(y, n):
    x = np.arange(n)
    xm = x.mean()
    sxx = ((x - xm) ** 2).sum()
    v = y.values
    out = np.full(len(v), np.nan)
    for i in range(n - 1, len(v)):
        w = v[i - n + 1:i + 1]
        if np.isnan(w).any():
            continue
        b = ((x - xm) * (w - w.mean())).sum() / sxx
        out[i] = w.mean() + b * (n - 1 - xm)
    return pd.Series(out, index=y.index)


def squeeze_calc(d):
    c, h, l = d["Close"], d["High"], d["Low"]
    basis = c.rolling(SQ_LENGTH).mean()
    dev = BB_MULT * c.rolling(SQ_LENGTH).std(ddof=0)
    bb_u, bb_l = basis + dev, basis - dev
    prev = c.shift(1)
    tr = pd.concat([h - l, (h - prev).abs(), (l - prev).abs()], axis=1).max(axis=1)
    dev_kc = tr.rolling(SQ_LENGTH).mean()
    comb = lambda p, q: p | q                      # same as your Pine script
    hi_sq = comb(bb_l >= basis - dev_kc * KC_MULTS[0], bb_u <= basis + dev_kc * KC_MULTS[0])
    mid_sq = comb(bb_l >= basis - dev_kc * KC_MULTS[1], bb_u <= basis + dev_kc * KC_MULTS[1])
    low_sq = comb(bb_l >= basis - dev_kc * KC_MULTS[2], bb_u <= basis + dev_kc * KC_MULTS[2])
    state = pd.Series(np.where(hi_sq, "orange", np.where(mid_sq, "red", np.where(low_sq, "black", "green"))),
                      index=d.index)
    mid = ((h.rolling(SQ_LENGTH).max() + l.rolling(SQ_LENGTH).min()) / 2 + basis) / 2
    return state, linreg(c - mid, SQ_LENGTH)


# ---------------- Time helpers ----------------
def to_et(d):
    d = d.copy()
    idx = d.index
    d.index = (idx.tz_localize(NY) if idx.tz is None else idx).tz_convert(NY)
    return d


def bar_end(ts, minutes):
    return min(ts + pd.Timedelta(minutes=minutes), ts.normalize() + pd.Timedelta(hours=16))


def regular_et(d):
    d = to_et(d)[["Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Close"])
    return d.between_time("09:30", "15:59")


def to_1h(d):
    """9:30-aligned hourly bars built from 15m bars (last bar = 15:30-16:00)."""
    return d.resample("60min", offset="30min").agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"}).dropna(subset=["Close"])


def last_days(d, n=MAX_DAYS):
    days = d.index.normalize().unique()
    return d[d.index >= days[-n]] if len(days) > n else d


def daily_from_15m(d):
    day = d.groupby(d.index.normalize()).agg(Open=("Open", "first"), High=("High", "max"),
                                             Low=("Low", "min"), Close=("Close", "last"))
    prev = day["Close"].shift(1)
    tr = pd.concat([day.High - day.Low, (day.High - prev).abs(), (day.Low - prev).abs()], axis=1).max(axis=1)
    atr_pct = (tr.rolling(14).mean() / day["Close"] * 100).shift(1)      # known BEFORE each day
    sma20 = day["Close"].rolling(20).mean().shift(1)
    return day, atr_pct, sma20


def _runlen(flag):
    out = np.zeros(len(flag), int)
    c = 0
    for i, x in enumerate(flag):
        c = c + 1 if x else 0
        out[i] = c
    return out


# ---------------- Features for one timeframe ----------------
def build_tf(d, minutes, now):
    d = to_et(d)
    ends = pd.DatetimeIndex([bar_end(t, minutes) for t in d.index])
    keep = np.asarray(ends <= now)
    d, ends = d[keep], ends[keep]
    if len(d) < WARMUP_BARS + 60:
        return None
    state, mom = squeeze_calc(d)
    a, b = ribbon(d)
    n = len(d)
    st = state.values
    green = st == "green"
    trans = green & ~np.r_[False, green[:-1]]
    pos = np.arange(n)
    fired = pos - pd.Series(np.where(trans, pos, np.nan)).ffill().values
    tl = np.full(n, np.nan)       # orange/red bars right before a fire
    pb = np.full(n, np.nan)       # black bars right before a fire
    for i in np.flatnonzero(trans):
        j, c, k = i - 1, 0, 0
        while j >= 0 and st[j] != "green":
            c += int(st[j] in ("orange", "red"))
            k += int(st[j] == "black")
            j -= 1
        tl[i], pb[i] = c, k
    m, mp = mom.values, mom.shift(1).values
    mcol = np.where(m > 0, np.where(m > mp, "aqua", "blue"), np.where(m < mp, "red", "yellow"))
    lo, hi = np.minimum(a.values, b.values), np.maximum(a.values, b.values)
    cl = d["Close"].values
    out = pd.DataFrame({"end": ends, "open": d["Open"].values, "high": d["High"].values,
                        "low": d["Low"].values, "close": cl, "sq": st, "mom": m, "mcol": mcol,
                        "rib": np.where(b.values > a.values, "lime", "red"),
                        "pxv": np.where(cl > hi, "above", np.where(cl < lo, "below", "inside")),
                        "fired": fired, "tight": pd.Series(tl).ffill().values,
                        "pre_black": pd.Series(pb).ffill().values,
                        "run_aqua": _runlen(mcol == "aqua"), "run_red": _runlen(mcol == "red")})
    return out.iloc[WARMUP_BARS:].reset_index(drop=True)


def build_panel(bars, now=None):
    """bars: {ticker: 15m regular-hours DataFrame in ET}. Returns one row per ticker per CLOSED 15m bar."""
    now = now_et() if now is None else now
    frames, ctx = [], {}
    for t, raw in bars.items():
        d = last_days(raw)
        if len(d) < 200:
            continue
        day, atr_s, sma_s = daily_from_15m(d)
        a, b = build_tf(d, 15, now), build_tf(to_1h(d), 60, now)
        if a is None or b is None:
            continue
        b = b[["end", "rib", "pxv", "mom"]].rename(columns={"rib": "rib_1h", "pxv": "pxv_1h", "mom": "mom_1h"})
        m = pd.merge_asof(a.sort_values("end"), b.sort_values("end"), on="end", direction="backward")
        m["ticker"] = t
        m["date"] = m["end"].dt.normalize()
        g = m.groupby("date")
        last_close = g["close"].transform("last")
        m["entry"] = g["open"].shift(-1)                      # next bar's open = hypothetical fill
        m["prev_close"] = m["date"].map(g["close"].last().shift(1))
        m["atr"] = m["date"].map(atr_s)
        m["sma20"] = m["date"].map(sma_s)
        m["gap_atr"] = ((g["open"].transform("first") / m["prev_close"] - 1) * 100).abs() / m["atr"]
        m["mins"] = m["end"].dt.hour * 60 + m["end"].dt.minute
        frames.append(m)
        ctx[t] = float(atr_s.dropna().iloc[-1]) if atr_s.notna().any() else np.nan
    if not frames:
        return pd.DataFrame()
    panel = pd.concat(frames, ignore_index=True)
    panel = panel[panel["atr"].notna() & panel["sma20"].notna()].copy()
    rank = pd.Series(ctx).rank(pct=True)
    return score_panel(panel, rank)


# ---------------- Checklist + opp score (same rules as the notebook) ----------------
def score_panel(df, atr_rank):
    fw, mt = FIRE_WINDOW, MIN_TIGHT_BARS
    fr = (df.sq.isin(["orange", "red"]) | ((df.fired <= fw) & (df.tight >= mt))).astype(int)
    c = ((df.rib_1h == "lime").astype(int) + (df.pxv_1h == "above").astype(int) + (df.mom_1h > 0).astype(int)
         + (df.rib == "lime").astype(int) + (df.mcol == "aqua").astype(int) + fr)
    p = ((df.rib_1h == "red").astype(int) + (df.pxv_1h == "below").astype(int) + (df.mom_1h < 0).astype(int)
         + (df.rib == "red").astype(int) + (df.mcol == "red").astype(int) + fr)
    call, put = (c >= MIN_SCORE) & (c > p), (p >= MIN_SCORE) & (p > c)
    df["fresh"] = fr
    df["setup"] = call | put
    df["dir"] = np.where(call, 1, np.where(put, -1, np.where(df.rib_1h == "lime", 1, -1)))
    chk = np.where(df["dir"] == 1, c, p)
    df["agree5"] = chk - fr                                # the five non-squeeze checks in the trade direction
    comp = df.sq.map({"orange": 25, "red": 20, "black": 10}).fillna(0).values
    real = df.fired.notna() & (df.tight >= mt)
    fire = np.where(~real, 0, np.where(df.fired <= fw // 2, 25, np.where(df.fired <= fw, 20,
                    np.where(df.fired <= 2 * fw, 10, 0))))
    e = df["dir"] * (df.close / df.sma20 - 1) * 100
    ext = np.where(e.isna(), 0, np.where(e <= df.atr, 15, np.where(e <= 2 * df.atr, 8, 0)))
    mv = df.mcol.values == np.where(df["dir"] == 1, "aqua", "red")
    xs = np.column_stack([chk / 6, np.maximum(comp, fire) / 25, mv.astype(float), ext / 15,
                          df.ticker.map(atr_rank).fillna(0.5).values])
    df["opp"] = xs @ CUR_W
    df["run_dir"] = np.where(df["dir"] == 1, df.run_aqua, df.run_red)
    return df
