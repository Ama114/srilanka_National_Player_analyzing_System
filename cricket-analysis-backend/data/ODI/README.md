# ODI (One Day International) Data

This folder contains all ODI cricket match data for Sri Lankan players.

## Files

- **odi_performance.csv** - Contains ODI player performance statistics
  - Columns: player_name, opposition, ground, matches, runs, strike_rate, average, wickets, economy, batting_style, main_role, etc.
  - Format: One row per player-opposition-ground combination

## Usage

This data is automatically loaded by `data_loader.py` when the application starts.

- Database: `odi_performance` table
- API Routes: `/api/best-xi/generate?match_type=ODI`
- Frontend Pages: Batting Performance (ODI tab), Bowling Performance (ODI tab), Best XI (ODI selector)
