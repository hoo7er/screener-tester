"""The testers. Each variant = an entry filter + a time window + an exit rule.
Add or edit variants here; nothing else needs to change. Times are bar-CLOSE minutes in ET
(600 = 10:00 ET = 07:00 PT)."""
import numpy as np

from .core import FIRE_WINDOW, MIN_TIGHT_BARS

SCAN = (600, 780)          # default entry window: 10:00-13:00 ET (07:00-10:00 PT)
MAX_PER_DAY = 5            # max hypothetical entries per variant per day (one per ticker)
TOP_N, MAX_PER_SECTOR = 5, 2   # the dashboard rule: top 5 names, at most 2 from one sector
GAP_SKIP_ATR = 1.0         # skip tickers that opened with a gap larger than this many daily ATRs

# exit rules (all in daily-ATR units, checked on 15m closes, filled at the next bar's open)
TRAIL_ATR = 0.5            # trail: exit when price falls this far from its best close
TP_ATR, SL_ATR = 0.5, 0.3  # tpsl: take profit / stop loss
HOLD_BARS = {"x4": 4, "x8": 8}   # fixed holds: 4 bars = 1 hour, 8 bars = 2 hours


def _aligned(df):          # 1H ribbon agrees with the trade direction
    return ((df["dir"] == 1) & (df.rib_1h == "lime")) | ((df["dir"] == -1) & (df.rib_1h == "red"))


def base_ok(df):           # the screener's own idea of a good setup
    return df.setup & (df.opp >= 70)


def base0(df):             # trend agrees (4 of the 5 non-squeeze checks) with the 1H ribbon on side
    return (df.agree5 >= 4) & _aligned(df)


def hot_fire(df):          # fired recently after orange/red compression
    return (df.fired <= FIRE_WINDOW) & (df.tight >= MIN_TIGHT_BARS)


def black_fire(df):        # fired recently after only black (weak) compression
    return (df.fired <= FIRE_WINDOW) & (df.tight == 0) & (df.pre_black >= MIN_TIGHT_BARS)


def _all(df):
    return np.ones(len(df), bool)


def _rib_dir(df):
    return np.where(df.rib_1h == "lime", 1, -1)


VARIANTS = []


def add(name, group, mask, window=SCAN, exit="x8", dirfn=None, rand=False, select=None, since=None):
    """since = first trading day (YYYY-MM-DD) that counts as forward for this tester; earlier days are labelled replay
    (use it for testers added after a day's entries were already decided)."""
    VARIANTS.append(dict(name=name, group=group, mask=mask, window=window, exit=exit, dirfn=dirfn, rand=rand,
                         select=select, since=since))


# 1) Best time of day to enter (bar-close time, ET)
for lo, hi, lab in [(585, 630, "0945-1030"), (630, 690, "1030-1130"), (690, 780, "1130-1300"), (780, 900, "1300-1500")]:
    add(f"time_{lab}", "time of day", base_ok, window=(lo, hi))

# 2) What the squeeze dots were doing at entry
add("dot_fire_after_hot", "squeeze dot", lambda d: base0(d) & hot_fire(d))
add("dot_fire_after_black", "squeeze dot", lambda d: base0(d) & black_fire(d))
add("dot_compressing_hot", "squeeze dot", lambda d: base0(d) & d.sq.isin(["orange", "red"]))
add("dot_compressing_black", "squeeze dot", lambda d: base0(d) & (d.sq == "black"))

# 3) Momentum bars in your direction at entry (aqua for calls, red for puts)
add("mom_run_1", "momentum bars", lambda d: base0(d) & (d.fresh == 1) & (d.run_dir == 1))
add("mom_run_2", "momentum bars", lambda d: base0(d) & (d.fresh == 1) & (d.run_dir == 2))
add("mom_run_3plus", "momentum bars", lambda d: base0(d) & (d.fresh == 1) & (d.run_dir >= 3))

# 4) opp score thresholds
add("score_70", "opp score", lambda d: d.opp >= 70)
add("score_85", "opp score", lambda d: d.opp >= 85)
add("score_92", "opp score", lambda d: d.opp >= 92)
add("score_setup_70", "opp score", base_ok)

# 5) Exit rules on the same entries (setup + opp >= 70)
for ex in ["x4", "x8", "eod", "trail", "tpsl", "momturn", "ribflip"]:
    add(f"exit_{ex}", "exit rule", base_ok, exit=ex)

# 6) The screener dashboard's own top-5 rule, taken once at the start of the scan window
#    (decision at the 10:00 ET close = 7:00 AM PT): setups first, then checklist score, then opp score,
#    at most 2 names per sector. Same 2-hour exit and gap skip as the other testers.
add("screener_top5", "screener rule", _all, window=(600, 600), select="dashboard", since="2026-11-16")

# Control: random picks in the direction of the 1H ribbon only. Everything should beat this.
add("control_random", "control", _all, dirfn=_rib_dir, rand=True)
