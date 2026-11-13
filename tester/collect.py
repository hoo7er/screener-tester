"""Entry points:
    python -m tester.collect seed     one-time: download ~58 days of bars and replay them through every tester
    python -m tester.collect live     every 15 min in market hours: log what each tester would do on the newest bars
    python -m tester.collect settle   after the close: store the day's bars, simulate exits, update the reports
"""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from . import core, engine, report
from .variants import VARIANTS

ROOT = Path(__file__).resolve().parent.parent
DATA, BARS, LIVE, TRADES, REPORTS = (ROOT / "data", ROOT / "data" / "bars", ROOT / "data" / "live",
                                     ROOT / "data" / "trades", ROOT / "reports")
UNIVERSE = ROOT / "universe.txt"
SEED_PERIOD, FRESH_PERIOD = "58d", "5d"


# ---------------- Data ----------------
def universe():
    out = []
    for line in UNIVERSE.read_text().splitlines():
        t = line.split("#")[0].strip().upper().replace(".", "-")
        if t:
            out.append(t)
    return list(dict.fromkeys(out))


def fetch(tickers, period, chunk=25):
    out = {}
    todo = list(tickers)
    for attempt in range(2):
        for i in range(0, len(todo), chunk):
            batch = todo[i:i + chunk]
            try:
                h = yf.download(batch, period=period, interval="15m", auto_adjust=True,
                                group_by="ticker", progress=False, threads=True)
            except Exception as e:
                print("download failed:", type(e).__name__, str(e)[:100])
                continue
            for t in batch:
                try:
                    x = h[t] if isinstance(h.columns, pd.MultiIndex) else h      # one-ticker batches come back flat
                    d = core.regular_et(x.dropna(subset=["Close"]))
                    if len(d) >= 10:
                        out[t] = d
                except Exception:
                    pass
            time.sleep(1)
        todo = [t for t in tickers if t not in out]
        if not todo:
            break
        print("retrying", len(todo), "tickers with no data")
        time.sleep(5)
    if todo:
        print("no data for:", todo)
    return out


STORE_DAYS = 70          # day files read back for indicator history (>= MAX_DAYS)


def load_store(tickers):
    files = sorted(BARS.glob("*.csv.gz"))[-STORE_DAYS:]
    if not files:
        return {}
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df.index = pd.to_datetime(df.pop("time"), utc=True).dt.tz_convert(core.NY)
    return {t: g.drop(columns="ticker") for t, g in df.groupby("ticker") if t in tickers}


def save_store(bars, now):
    """One immutable file per finished trading day (data/bars/YYYY-MM-DD.csv.gz), so git history stays small."""
    BARS.mkdir(parents=True, exist_ok=True)
    after_close = (now.hour * 60 + now.minute) >= (16 * 60 + 10)
    allbars = pd.concat([d.assign(ticker=t) for t, d in bars.items()])
    for day, g in allbars.groupby(allbars.index.normalize()):
        if day.date() >= now.date() and not after_close:
            continue
        f = BARS / f"{day:%Y-%m-%d}.csv.gz"
        if f.exists():
            continue
        out = g.copy()
        out.insert(0, "time", out.index.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ"))
        out.round(4).to_csv(f, index=False)


def merged_bars(tickers, period=FRESH_PERIOD):
    store = load_store(tickers)
    missing = [t for t in tickers if t not in store]
    fresh = fetch(tickers, SEED_PERIOD if missing else period)
    bars = {}
    for t in tickers:
        parts = [x for x in (store.get(t), fresh.get(t)) if x is not None]
        if not parts:
            continue
        d = pd.concat(parts)
        bars[t] = d[~d.index.duplicated(keep="last")].sort_index()
    return bars


def meta():
    f = DATA / "meta.json"
    return json.loads(f.read_text()) if f.exists() else {}


def save_meta(m):
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "meta.json").write_text(json.dumps(m, indent=1))


def market_open_now(now):
    return now.weekday() < 5 and (9 * 60 + 45) <= now.hour * 60 + now.minute <= (16 * 60 + 10)


# ---------------- live ----------------
def live():
    now = core.now_et()
    if not market_open_now(now) and not os.environ.get("FORCE_LIVE"):
        print("market closed, nothing to do:", now)
        return
    tickers = universe()
    if not list(BARS.glob("*.csv.gz")):
        print("no stored history yet - running seed first")
        seed()
    bars = merged_bars(tickers)
    panel = core.build_panel(bars, now)
    today = now.normalize()
    rows = panel[panel.date == today].copy() if len(panel) else panel
    LIVE.mkdir(parents=True, exist_ok=True)
    f = LIVE / f"{today:%Y-%m-%d}.csv"
    seen = set()
    if f.exists():
        old = pd.read_csv(f)
        seen = set(zip(old.ticker, old.end))
    last_end = rows.end.max() if len(rows) else None
    new = rows[[(t, str(e)) not in seen for t, e in zip(rows.ticker, rows.end)]] if len(rows) else rows
    flagged = 0
    if len(new):
        new = new.assign(variants=engine.live_flags(new))
        new = new[new.variants != ""]
        flagged = len(new)
        if flagged:
            cols = ["end", "ticker", "close", "dir", "setup", "opp", "sq", "mcol", "rib", "rib_1h",
                    "fired", "tight", "run_dir", "variants"]
            out = new[cols].assign(lag_min=((now - new.end).dt.total_seconds() / 60).round(0),
                                   end=new.end.astype(str), logged_at=str(now))
            out.to_csv(f, mode="a", header=not f.exists(), index=False)
    run = pd.DataFrame([dict(run_at=str(now), last_bar_end=str(last_end), tickers=int(rows.ticker.nunique()) if len(rows) else 0,
                             new_flagged=flagged)])
    run.to_csv(LIVE / "runs.csv", mode="a", header=not (LIVE / "runs.csv").exists(), index=False)
    print(f"{now:%H:%M} ET | bars through {last_end} | {flagged} new flagged rows")
    if flagged:
        print(new.sort_values("opp", ascending=False).head(10)[["ticker", "end", "dir", "opp", "variants"]].to_string(index=False))


# ---------------- settle ----------------
def settle(bars=None, save=True):
    now = core.now_et()
    if bars is None:
        bars = merged_bars(universe())
    if save:
        save_store(bars, now)
    panel = core.build_panel(bars, now)
    if panel.empty:
        print("no panel (not enough data)")
        return
    m = meta()
    if "forward_start" not in m:
        m["forward_start"] = str(now.date())
        save_meta(m)
    TRADES.mkdir(parents=True, exist_ok=True)
    after_close = (now.hour * 60 + now.minute) >= (16 * 60 + 10)
    quality = []
    for day in sorted(panel.date.unique()):
        d = pd.Timestamp(day)
        if d.date() >= now.date() and not after_close:
            continue
        f = TRADES / f"{d:%Y-%m-%d}.csv"
        sub = panel[panel.date == day]
        if f.exists() or sub.ticker.nunique() < 5:
            continue
        kind = "forward" if str(d.date()) >= m["forward_start"] else "replay"
        tr = engine.run_day(sub, d.date(), kind)
        if len(tr):
            tr.to_csv(f, index=False)
        else:
            f.write_text("variant\n")
        print(f"{d:%Y-%m-%d} {kind}: {len(tr)} hypothetical trades")
        lf = LIVE / f"{d:%Y-%m-%d}.csv"
        if kind == "forward" and lf.exists():
            live_rows = pd.read_csv(lf)
            recomputed = sub.assign(variants=engine.live_flags(sub))
            recomputed = recomputed[recomputed.variants != ""]
            keys_live = set(zip(live_rows.ticker, live_rows.end))
            keys_re = set(zip(recomputed.ticker, recomputed.end.astype(str)))
            quality.append(dict(date=str(d.date()), live_rows=len(keys_live), recomputed_rows=len(keys_re),
                                matched=len(keys_live & keys_re), missed_live=len(keys_re - keys_live)))
    q_file = DATA / "quality.csv"
    if quality:
        pd.DataFrame(quality).to_csv(q_file, mode="a", header=not q_file.exists(), index=False)
    report.write_reports(TRADES, DATA, REPORTS, pd.read_csv(q_file) if q_file.exists() else None)
    print("reports updated")


def seed():
    tickers = universe()
    print("seeding", len(tickers), "tickers")
    bars = merged_bars(tickers, SEED_PERIOD)
    m = meta()
    if "forward_start" not in m:
        m["forward_start"] = str(core.now_et().date())
        save_meta(m)
    settle(bars=bars, save=True)


if __name__ == "__main__":
    {"live": live, "settle": settle, "seed": seed}[sys.argv[1]]()
