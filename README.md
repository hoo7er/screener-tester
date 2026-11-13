# Strategy tester

Runs your screener's strategy on real Yahoo Finance data for testing, automatically, all through market hours, and keeps score.

- **live** (every 15 min, market hours): logs which testers would enter on the newest closed 15m bars -> `data/live/`
- **settle** (after the close): stores the day's bars, simulates every tester's exits, rewrites `reports/summary.md`
- **seed** (once): downloads ~58 days of 15m bars and replays them through every tester so you have a baseline on day one

The indicators are the same ports you use in the Colab screener (REDACTED INFO CUZ).
It measures **the stock's move in your direction, in daily-ATR units**. Option P&L comes later.

## The testers (edit `tester/variants.py`)

| group | what it compares |
|---|---|
| time of day | entries at 09:45-10:30, 10:30-11:30, 11:30-13:00, 13:00-15:00 ET |
| squeeze dot | fire after orange/red vs after black; entering while compressing (orange/red vs black) |
| momentum bars | enter on the 1st, 2nd, or 3rd+ consecutive aqua (call) / red (put) bar |
| opp score | opp >= 70, 85, 92, and setup + 70 |
| exit rule | 1h, 2h, close, trailing stop, take-profit/stop-loss, momentum turn, ribbon flip (same entries) |
| control | random picks in the 1H ribbon direction. Everything must beat this. |

Each variant makes up to 5 hypothetical entries a day (one per ticker) between 10:00 and 13:00 ET (07:00-10:00 PT) unless its window says otherwise.
Entry = next 15m bar's open after the signal bar closes. Exits are checked on 15m closes and filled at the next open.

## One-time setup

1. Put these files in a GitHub repo (keep the folder layout, including the hidden `.github/workflows` folder).
2. **Settings -> Actions -> General -> Workflow permissions -> Read and write permissions -> Save.**
3. Edit `universe.txt` (one ticker per line). To use your screener's survivors, run this in Colab after cell 3 and paste the output:
   ```python
   print("\n".join(TICKERS))
   ```
4. **Actions tab -> `seed` -> Run workflow.** Wait for it to finish (a few minutes). Open `reports/summary.md`.
5. That's it. `live` and `settle` then run on their own on weekdays. To test them off-hours: Actions -> `live` -> Run workflow -> tick "force".

**Never put API keys or passwords in this repo.** It doesn't need any: Yahoo data needs no key.

## Reading the results

`reports/summary.md` is rewritten after every close. Two sections:

- **Forward** - real-time days after the repo was set up. This is the honest scoreboard.
- **Replay** - the seeded history re-run through the rules. Useful for a first look, but variants were chosen with this history in mind.

Columns: `avg_atr` average move in your direction (daily-ATR units) | `vs_control` minus the random control |
`p_luck` chance noise alone matches it (counted over days) | `win_lo/win_hi` 95% range of the win rate.
"too thin" means fewer than 30 trades or 8 days. With ~22 variants some will look good by luck; trust one only if it shows up in Forward too.

Other files: `data/trades/DATE.csv` (every hypothetical trade, incl. the move at +1...+16 bars), `data/live/DATE.csv` (what was flagged
live, with `lag_min` = how old the bar was when logged), `data/live/runs.csv` (heartbeat: proves each run happened),
`data/quality.csv` (live log vs recomputed after the close), `data/bars/` (one file per finished day, so history keeps growing past Yahoo's 60-day limit).

## Limits worth knowing

- GitHub scheduled runs can start a few minutes late or be skipped when GitHub is busy. Missed bars are recomputed after the close (see `data/quality.csv`).
- Yahoo's free intraday feed can lag slightly and differs a little from TradingView's bars, so borderline squeeze colors can differ.
- Free minutes: public repos are free. Private repos on the Free plan have a monthly allowance (check Settings -> Billing); this uses roughly 700-900 minutes a month.
- GitHub may pause scheduled workflows in a public repo after ~60 days with no repository activity. The daily data commits normally count as activity; if runs stop, re-enable under the Actions tab.
