# Strategy tester summary

Updated through **2026-11-12** | 37 trading days | 4,039 hypothetical trades | 23 variants

`avg_atr` is the average move in your direction, measured in daily-ATR units (the stock's move, not option P&L). `vs_control` subtracts the random 1H-ribbon control. `p_luck` is the chance noise alone matches the result, counted over days. Win-rate range = 95% interval.

With 22 variants compared, a few will look good by chance. Trust a variant only if it also holds in `forward` data (real-time, never tuned on).

## Replay (history re-run through the same rules)

### control

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| control_random | 185 | 37 | 47.03 | 39.97 | 54.21 | -0.03 | 0.00 | 0.91 | 8.00 | 0.82 | control |

### squeeze dot

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dot_compressing_hot | 184 | 37 | 53.26 | 46.06 | 60.33 | 0.02 | 0.05 | 1.05 | 8.00 | 0.18 | beats control, could be luck |
| dot_fire_after_hot | 185 | 37 | 50.81 | 43.66 | 57.92 | 0.00 | 0.03 | 0.99 | 8.00 | 0.47 | beats control, could be luck |
| dot_compressing_black | 185 | 37 | 46.49 | 39.44 | 53.67 | -0.01 | 0.01 | 1.01 | 8.00 | 0.71 | no edge |
| dot_fire_after_black | 36 | 26 | 41.67 | 27.14 | 57.80 | -0.02 | 0.01 | 1.04 | 8.00 | 0.77 | no edge |

### exit rule

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exit_x8 | 185 | 37 | 50.81 | 43.66 | 57.92 | 0.01 | 0.03 | 1.03 | 8.00 | 0.38 | beats control, could be luck |
| exit_momturn | 185 | 37 | 42.70 | 35.79 | 49.91 | 0.00 | 0.03 | 1.37 | 5.96 | 0.46 | beats control, could be luck |
| exit_x4 | 185 | 37 | 48.65 | 41.55 | 55.81 | 0.00 | 0.03 | 1.06 | 4.00 | 0.49 | beats control, could be luck |
| exit_ribflip | 185 | 37 | 44.32 | 37.35 | 51.53 | -0.00 | 0.03 | 1.25 | 5.95 | 0.50 | no edge |
| exit_trail | 185 | 37 | 46.49 | 39.44 | 53.67 | -0.00 | 0.02 | 1.14 | 20.32 | 0.52 | no edge |
| exit_tpsl | 185 | 37 | 44.32 | 37.35 | 51.53 | -0.01 | 0.02 | 1.20 | 14.65 | 0.58 | no edge |
| exit_eod | 185 | 37 | 47.57 | 40.49 | 54.74 | -0.01 | 0.01 | 1.02 | 23.88 | 0.63 | no edge |

### momentum bars

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mom_run_3plus | 185 | 37 | 54.59 | 47.40 | 61.60 | 0.05 | 0.08 | 1.27 | 8.00 | 0.04 | edge? (beats control, p<0.10) |
| mom_run_1 | 176 | 37 | 52.27 | 44.92 | 59.52 | 0.00 | 0.03 | 0.91 | 8.00 | 0.45 | beats control, could be luck |
| mom_run_2 | 181 | 37 | 49.17 | 41.98 | 56.40 | -0.02 | 0.00 | 0.87 | 8.00 | 0.75 | no edge |

### opp score

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| score_92 | 133 | 35 | 58.65 | 50.15 | 66.66 | 0.05 | 0.08 | 1.23 | 8.00 | 0.04 | edge? (beats control, p<0.10) |
| score_85 | 185 | 37 | 55.68 | 48.47 | 62.65 | 0.03 | 0.06 | 1.05 | 8.00 | 0.12 | beats control, could be luck |
| score_setup_70 | 185 | 37 | 50.81 | 43.66 | 57.92 | 0.01 | 0.03 | 1.03 | 8.00 | 0.38 | beats control, could be luck |
| score_70 | 185 | 37 | 50.81 | 43.66 | 57.92 | 0.01 | 0.03 | 1.02 | 8.00 | 0.41 | beats control, could be luck |

### time of day

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| time_1300-1500 | 184 | 37 | 49.46 | 42.32 | 56.62 | 0.01 | 0.04 | 1.27 | 7.90 | 0.19 | beats control, could be luck |
| time_1130-1300 | 185 | 37 | 49.73 | 42.60 | 56.87 | 0.01 | 0.04 | 1.18 | 8.00 | 0.31 | beats control, could be luck |
| time_1030-1130 | 185 | 37 | 52.97 | 45.79 | 60.03 | 0.01 | 0.03 | 0.96 | 8.00 | 0.37 | beats control, could be luck |
| time_0945-1030 | 185 | 37 | 46.49 | 39.44 | 53.67 | 0.00 | 0.03 | 1.18 | 8.00 | 0.46 | beats control, could be luck |

## Where does the move peak? (entries with opp >= 70 and a setup)

Average move in ATR units at +N bars after entry (15m bars) and the percent of trades that are up.

| kind | n | +1 | +2 | +3 | +4 | +5 | +6 | +7 | +8 | +9 | +10 | +11 | +12 | +13 | +14 | +15 | +16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| replay | 185 | 0.01 | 0.00 | -0.01 | 0.00 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | -0.00 | 0.00 | 0.01 | 0.00 | 0.01 | 0.01 | 0.01 |
| replay % up | 185 | 49.19 | 48.65 | 45.95 | 48.65 | 51.89 | 51.35 | 52.43 | 50.27 | 51.35 | 45.95 | 45.95 | 49.19 | 48.65 | 47.03 | 48.11 | 47.57 |
