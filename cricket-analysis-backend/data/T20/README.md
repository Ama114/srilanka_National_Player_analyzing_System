# T20 (Twenty20) Cricket Data

This folder contains all T20 cricket match data for Sri Lankan players.

## Files

- **t20_performance.csv** - Contains T20 player performance statistics (currently no data)
  - Columns: player_name, opposition, ground, matches, runs, strike_rate, average, wickets, economy, batting_style, main_role, etc.
  - Format: One row per player-opposition-ground combination

## Usage

This data will be automatically loaded by `data_loader.py` when the application starts (if a CSV file is added).

- Database: `t20_performance` table
- API Routes: `/api/best-xi/generate?match_type=T20`
- Frontend Pages: Batting Performance (T20 tab), Bowling Performance (T20 tab), Best XI (T20 selector)

## Note

Currently, there are no T20 records in the database. To add T20 data:
1. Place a CSV file named `t20_performance.csv` in this folder
2. Ensure it has the same column structure as `odi_performance.csv` and `test_performance.csv`
3. Restart the backend application
