# Strategy tester summary

Updated through **2026-11-13** | 38 trading days | 4,339 hypothetical trades | 24 variants

`avg_atr` is the average move in your direction, measured in daily-ATR units (the stock's move, not option P&L). `vs_control` subtracts the random 1H-ribbon control. `p_luck` is the chance noise alone matches the result, counted over days. Win-rate range = 95% interval.

With 23 variants compared, a few will look good by chance. Trust a variant only if it also holds in `forward` data (real-time, never tuned on).

## Forward test (real time, after the strategy was frozen)

### control

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| control_random | 5 | 1 | 80.00 | 37.55 | 96.38 | 0.14 | 0.00 | 10.75 | 8.00 |  | control |

### squeeze dot

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| dot_compressing_black | 5 | 1 | 80.00 | 37.55 | 96.38 | 0.09 | -0.05 | 0.82 | 8.00 |  | too thin |
| dot_fire_after_hot | 5 | 1 | 80.00 | 37.55 | 96.38 | 0.08 | -0.06 | 1.10 | 8.00 |  | too thin |
| dot_compressing_hot | 5 | 1 | 20.00 | 3.62 | 62.45 | -0.09 | -0.24 | 0.55 | 8.00 |  | too thin |

### exit rule

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exit_x4 | 5 | 1 | 80.00 | 37.55 | 96.38 | 0.15 | 0.01 | 9.16 | 4.00 |  | too thin |
| exit_ribflip | 5 | 1 | 40.00 | 11.76 | 76.93 | 0.09 | -0.05 | 9.23 | 6.00 |  | too thin |
| exit_x8 | 5 | 1 | 80.00 | 37.55 | 96.38 | 0.08 | -0.06 | 1.10 | 8.00 |  | too thin |
| exit_momturn | 5 | 1 | 40.00 | 11.76 | 76.93 | 0.07 | -0.07 | 6.16 | 6.40 |  | too thin |
| exit_eod | 5 | 1 | 40.00 | 11.76 | 76.93 | -0.05 | -0.19 | 0.41 | 24.00 |  | too thin |
| exit_trail | 5 | 1 | 40.00 | 11.76 | 76.93 | -0.05 | -0.19 | 0.41 | 24.00 |  | too thin |
| exit_tpsl | 5 | 1 | 40.00 | 11.76 | 76.93 | -0.05 | -0.19 | 0.41 | 24.00 |  | too thin |

### momentum bars

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| mom_run_3plus | 5 | 1 | 100.00 | 56.55 | 100.00 | 0.12 | -0.02 |  | 8.00 |  | too thin |
| mom_run_1 | 5 | 1 | 0.00 | -0.00 | 43.45 | -0.09 | -0.23 |  | 8.00 |  | too thin |
| mom_run_2 | 5 | 1 | 20.00 | 3.62 | 62.45 | -0.11 | -0.25 | 0.66 | 8.00 |  | too thin |

### opp score

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| score_70 | 5 | 1 | 80.00 | 37.55 | 96.38 | 0.08 | -0.06 | 1.10 | 8.00 |  | too thin |
| score_85 | 5 | 1 | 80.00 | 37.55 | 96.38 | 0.08 | -0.06 | 1.10 | 8.00 |  | too thin |
| score_setup_70 | 5 | 1 | 80.00 | 37.55 | 96.38 | 0.08 | -0.06 | 1.10 | 8.00 |  | too thin |
| score_92 | 5 | 1 | 40.00 | 11.76 | 76.93 | -0.05 | -0.19 | 0.83 | 8.00 |  | too thin |

### time of day

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| time_0945-1030 | 5 | 1 | 80.00 | 37.55 | 96.38 | 0.31 | 0.17 | 3.61 | 8.00 |  | too thin |
| time_1300-1500 | 5 | 1 | 60.00 | 23.07 | 88.24 | 0.06 | -0.09 | 3.87 | 8.00 |  | too thin |
| time_1130-1300 | 5 | 1 | 20.00 | 3.62 | 62.45 | -0.07 | -0.21 | 0.30 | 8.00 |  | too thin |
| time_1030-1130 | 5 | 1 | 20.00 | 3.62 | 62.45 | -0.17 | -0.31 | 0.02 | 8.00 |  | too thin |

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

### screener rule

| variant | n | days | win_pct | win_lo | win_hi | avg_atr | vs_control | payoff | bars_held | p_luck | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| screener_top5 | 190 | 38 | 55.26 | 48.16 | 62.16 | 0.05 | 0.07 | 1.14 | 8.00 | 0.04 | edge? (beats control, p<0.10) |

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
| forward | 5 | 0.23 | 0.16 | 0.19 | 0.15 | 0.19 | 0.09 | 0.13 | 0.08 | 0.03 | 0.05 | 0.03 | 0.05 | 0.06 | -0.01 | -0.03 | -0.05 |
| forward % up | 5 | 100.00 | 100.00 | 80.00 | 80.00 | 100.00 | 60.00 | 80.00 | 80.00 | 40.00 | 60.00 | 40.00 | 60.00 | 60.00 | 60.00 | 60.00 | 40.00 |
| replay | 185 | 0.01 | 0.00 | -0.01 | 0.00 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | -0.00 | 0.00 | 0.01 | 0.00 | 0.01 | 0.01 | 0.01 |
| replay % up | 185 | 49.19 | 48.65 | 45.95 | 48.65 | 51.89 | 51.35 | 52.43 | 50.27 | 51.35 | 45.95 | 45.95 | 49.19 | 48.65 | 47.03 | 48.11 | 47.57 |

## Live vs recomputed (data quality)

| date | live_rows | recomputed_rows | matched | missed_live |
|---|---|---|---|---|
| 2026-11-13 | 685 | 683 | 683 | 0 |
