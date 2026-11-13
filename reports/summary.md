# Strategy tester summary

Updated through **2026-11-12** | 25 trading days | 2,664 hypothetical trades | 23 variants

`avg_atr` is the average move in your direction, measured in daily-ATR units (the stock's move, not option P&L). `vs_control` subtracts the random 1H-ribbon control. `p_luck` is the chance noise alone matches the result, counted over days. Win-rate range = 95% interval.

With 22 variants compared, a few will look good by chance. Trust a variant only if it also holds in `forward` data (real-time, never tuned on).

## Replay (history re-run through the same rules)

### control

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| control_random | 125 | 25 | 47.20 | 38.66 | 55.90 | -0.02 | 0.00 | 0.92 | 8.00 | 0.74 | control |

### squeeze dot

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dot_fire_after_hot | 125 | 25 | 56.00 | 47.25 | 64.39 | 0.04 | 0.06 | 1.06 | 8.00 | 0.15 | beats control, could be luck |
| dot_compressing_hot | 124 | 25 | 54.03 | 45.27 | 62.55 | 0.02 | 0.04 | 0.97 | 8.00 | 0.31 | beats control, could be luck |
| dot_compressing_black | 125 | 25 | 52.00 | 43.31 | 60.57 | -0.01 | 0.01 | 0.83 | 8.00 | 0.66 | no edge |
| dot_fire_after_black | 29 | 19 | 41.38 | 25.51 | 59.26 | -0.02 | 0.00 | 1.04 | 8.00 | 0.76 | too thin |

### exit rule

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exit_x8 | 125 | 25 | 51.20 | 42.53 | 59.80 | 0.00 | 0.03 | 0.98 | 8.00 | 0.47 | beats control, could be luck |
| exit_x4 | 125 | 25 | 49.60 | 40.98 | 58.25 | 0.00 | 0.03 | 1.05 | 4.00 | 0.48 | beats control, could be luck |
| exit_ribflip | 125 | 25 | 44.80 | 36.37 | 53.54 | 0.00 | 0.02 | 1.23 | 5.82 | 0.50 | beats control, could be luck |
| exit_trail | 125 | 25 | 45.60 | 37.13 | 54.33 | -0.00 | 0.02 | 1.17 | 20.30 | 0.52 | no edge |
| exit_momturn | 125 | 25 | 40.00 | 31.83 | 48.76 | -0.01 | 0.02 | 1.44 | 5.62 | 0.56 | no edge |
| exit_tpsl | 125 | 25 | 41.60 | 33.34 | 50.37 | -0.02 | 0.01 | 1.27 | 14.02 | 0.64 | no edge |
| exit_eod | 125 | 25 | 45.60 | 37.13 | 54.33 | -0.04 | -0.02 | 0.95 | 23.77 | 0.78 | no edge |

### momentum bars

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mom_run_3plus | 125 | 25 | 57.60 | 48.84 | 65.91 | 0.06 | 0.08 | 1.21 | 8.00 | 0.03 | edge? (beats control, p<0.10) |
| mom_run_1 | 116 | 25 | 52.59 | 43.56 | 61.44 | 0.00 | 0.03 | 0.92 | 8.00 | 0.40 | beats control, could be luck |
| mom_run_2 | 121 | 25 | 50.41 | 41.63 | 59.17 | -0.01 | 0.01 | 0.88 | 8.00 | 0.64 | no edge |

### opp score

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| score_92 | 58 | 17 | 62.07 | 49.20 | 73.44 | 0.07 | 0.10 | 1.21 | 8.00 | 0.21 | beats control, could be luck |
| score_85 | 96 | 20 | 57.29 | 47.30 | 66.72 | 0.03 | 0.05 | 0.95 | 8.00 | 0.36 | beats control, could be luck |
| score_setup_70 | 125 | 25 | 51.20 | 42.53 | 59.80 | 0.00 | 0.03 | 0.98 | 8.00 | 0.47 | beats control, could be luck |
| score_70 | 125 | 25 | 51.20 | 42.53 | 59.80 | -0.00 | 0.02 | 0.94 | 8.00 | 0.53 | no edge |

### time of day

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| time_0945-1030 | 125 | 25 | 48.80 | 40.20 | 57.47 | 0.02 | 0.05 | 1.21 | 8.00 | 0.33 | beats control, could be luck |
| time_1030-1130 | 125 | 25 | 56.00 | 47.25 | 64.39 | 0.02 | 0.04 | 0.94 | 8.00 | 0.29 | beats control, could be luck |
| time_1300-1500 | 121 | 25 | 51.24 | 42.43 | 59.97 | 0.02 | 0.04 | 1.22 | 7.83 | 0.15 | beats control, could be luck |
| time_1130-1300 | 124 | 25 | 50.81 | 42.12 | 59.45 | 0.00 | 0.03 | 1.01 | 8.00 | 0.43 | beats control, could be luck |

## Where does the move peak? (entries with opp >= 70 and a setup)

Average move in ATR units at +N bars after entry (15m bars) and the percent of trades that are up.

| kind | n | +1 | +2 | +3 | +4 | +5 | +6 | +7 | +8 | +9 | +10 | +11 | +12 | +13 | +14 | +15 | +16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| replay | 125 | 0.01 | 0.01 | -0.01 | 0.00 | 0.01 | 0.01 | 0.01 | 0.00 | -0.01 | -0.00 | -0.00 | -0.01 | -0.01 | -0.01 | -0.01 | -0.02 |
| replay % up | 125 | 50.40 | 52.00 | 44.00 | 49.60 | 48.00 | 50.40 | 53.60 | 51.20 | 50.40 | 47.20 | 46.40 | 46.40 | 47.20 | 45.60 | 47.20 | 46.40 |
