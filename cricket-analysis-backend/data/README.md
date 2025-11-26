# Cricket Analysis Data Structure

This `data` folder contains all CSV data files organized by cricket match type.

## Folder Structure

```
data/
├── ODI/
│   ├── odi_performance.csv       (359 records)
│   └── README.md
├── Test/
│   ├── test_performance.csv      (1,481 records)
│   └── README.md
├── T20/
│   └── README.md                 (0 records - placeholder)
└── README.md (this file)
```

## Match Types

### ODI (One Day International)
- **File**: `ODI/odi_performance.csv`
- **Records**: 359 player-opposition-ground combinations
- **Players**: 14 unique players
- **Used in**: 
  - Batting Performance Page (ODI tab)
  - Bowling Performance Page (ODI tab)
  - Best XI Generator (ODI selector)

### Test Cricket
- **File**: `Test/test_performance.csv`
- **Records**: 1,481 player-opposition-ground combinations
- **Players**: 18 unique players
- **Used in**: 
  - Batting Performance Page (Test tab)
  - Bowling Performance Page (Test tab)
  - Best XI Generator (Test selector)

### T20 (Twenty20)
- **File**: `T20/t20_performance.csv`
- **Records**: Currently 0 (awaiting data)
- **Players**: 0
- **Status**: Placeholder folder, ready for T20 data upload
- **Used in**: 
  - Batting Performance Page (T20 tab)
  - Bowling Performance Page (T20 tab)
  - Best XI Generator (T20 selector)

## CSV Format

Each CSV file should contain the following columns:

```
player_name      | String  | Player's full name
opposition       | String  | Opposition team name
ground           | String  | Cricket ground/venue
matches          | Integer | Number of matches
runs             | Integer | Total runs scored
strike_rate      | Float   | Batting strike rate (%)
average          | Float   | Batting average
wickets          | Integer | Total wickets taken
economy          | Float   | Bowling economy rate
batting_style    | String  | Left/Right handed
main_role        | String  | Wicket Keeper / Batsman / Bowler / All-Rounder
balls_faced      | Integer | Total balls faced
fours            | Integer | Total fours hit
sixes            | Integer | Total sixes hit
```

## Data Loading

The application automatically loads data from these folders in this order:

1. **Database First**: Checks if data exists in MySQL `odi_performance`, `test_performance`, `t20_performance` tables
2. **CSV Fallback**: If database is empty or unavailable, loads from CSV files
3. **Bootstrap**: On first run, populates database from CSV files

### Data Loader Configuration

File: `data_loader.py`

- Reads CSV files with UTF-8 encoding ('latin1' fallback)
- Automatically normalizes column names (strips whitespace, quotes)
- Separates batting data (runs > 0) from bowling data (wickets > 0)
- Organizes data by match type in: `datasets[match_type][data_type]`

## Adding New Data

### To add ODI data:
1. Place CSV file in `ODI/` folder
2. Ensure column names match expected format
3. Run `python load_odi_performance_csv.py` or restart application

### To add Test data:
1. Place CSV file in `Test/` folder
2. Ensure column names match expected format
3. Run `python update_odi_performance_table.py` or restart application

### To add T20 data:
1. Place CSV file in `T20/` folder named `t20_performance.csv`
2. Ensure column names match expected format
3. Restart application (data will auto-load)

## Database Tables

- `odi_performance` - Stores ODI data
- `test_performance` - Stores Test data (1,481 records loaded)
- `t20_performance` - Stores T20 data (currently empty)

Each table is created automatically on first application startup.

## Access from Code

```python
from data_loader import get_dataset

# Get ODI batting data
odi_batting = get_dataset('ODI', 'batting')

# Get Test bowling data
test_bowling = get_dataset('TEST', 'bowling')

# Get all available match types
all_types = get_all_match_types()  # Returns ['ODI', 'T20', 'Test']
```
