# Test Cricket Data

This folder contains all Test cricket match data for Sri Lankan players.

## Files

- **test_performance.csv** - Contains Test player performance statistics
  - Columns: player_name, opposition, ground, matches, runs, strike_rate, average, wickets, economy, batting_style, main_role, etc.
  - Format: One row per player-opposition-ground combination
  - Records: 1,481 Test cricket records

## Usage

This data is automatically loaded by `data_loader.py` when the application starts.

- Database: `test_performance` table
- API Routes: `/api/best-xi/generate?match_type=TEST`
- Frontend Pages: Batting Performance (Test tab), Bowling Performance (Test tab), Best XI (Test selector)
