# Sri Lanka National Player Analyzing System - Data Flow Diagram

## 📊 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER (Browser)                           │
└────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React.js)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  HomePage    │  │  BattingPage │  │ BowlingPage  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ BestXIPage  │  │ DatasetPage  │                            │
│  └──────────────┘  └──────────────┘                            │
└────────────────────────────┬────────────────────────────────────┘
                              │ HTTP/REST API (JSON)
                              │ Port: 3000 → 5000
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (Flask/Python)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  home_bp     │  │ batting_bp   │  │ bowling_bp   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ best_xi_bp   │  │ dataset_bp   │                            │
│  └──────────────┘  └──────────────┘                            │
└────────────┬──────────────────┬──────────────────┬─────────────┘
             │                   │                  │
             ▼                   ▼                  ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   MySQL Database │  │  CSV Files      │  │  ML Model       │
│  - best_xi_      │  │  - odi_batting  │  │  - best_xi_     │
│    players       │  │    _cleaned.csv │  │    model.joblib │
│  - player_       │  │  - odi_bowling  │  │                 │
│    performance_  │  │    _cleaned.csv │  │                 │
│    records       │  │  - srilanka     │  │                 │
│                  │  │    player 11    │  │                 │
│                  │  │    dataset.csv │  │                 │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 🔄 Complete Data Flow Diagrams

### 1. Homepage Data Flow

```
USER → HomePage Component
         │
         ├─→ GET /api/homepage-stats
         │     │
         │     ├─→ Read odi_batting_cleaned.csv
         │     ├─→ Read odi_bowling_cleaned.csv
         │     ├─→ Calculate: Total Runs, Total Wickets
         │     ├─→ Find: Top Batsman, Top Bowler
         │     │
         │     └─→ Return JSON: {totalRuns, totalWickets, topScorer, topBowler}
         │
         └─→ Display Stats on UI
```

**API Endpoint:** `GET /api/homepage-stats`

**Data Sources:**
- `odi_batting_cleaned.csv` (for batting stats)
- `odi_bowling_cleaned.csv` (for bowling stats)

**Response Format:**
```json
{
  "totalRuns": 12345,
  "totalWickets": 567,
  "topScorer": {"name": "Player Name", "stat": "1234 Runs"},
  "topBowler": {"name": "Player Name", "stat": "56 Wickets"}
}
```

---

### 2. Batting Performance Page Data Flow

```
USER → BattingPerformancePage
         │
         ├─→ Step 1: Load Players
         │     │
         │     └─→ GET /api/players
         │           │
         │           ├─→ Read odi_batting_cleaned.csv
         │           ├─→ Extract unique player names
         │           │
         │           └─→ Return: ["Player1", "Player2", ...]
         │
         ├─→ Step 2: User Selects Player
         │     │
         │     └─→ GET /api/grounds-for-player?player={name}
         │           │
         │           ├─→ Filter CSV by player name
         │           ├─→ Extract unique grounds
         │           │
         │           └─→ Return: ["Ground1", "Ground2", ...]
         │
         ├─→ Step 3: User Selects Ground
         │     │
         │     ├─→ GET /api/player-ground-stats?player={name}&ground={ground}
         │     │     │
         │     │     ├─→ Filter CSV: player + ground
         │     │     ├─→ Calculate: matches, totalRuns, average, strikeRate
         │     │     ├─→ Find: mostFrequentDismissal, bestOpposition
         │     │     ├─→ Count: total4s, total6s
         │     │     │
         │     │     └─→ Return: {matches, totalRuns, average, ...}
         │     │
         │     └─→ GET /api/player-ground-chart-data?player={name}&ground={ground}
         │           │
         │           ├─→ Filter CSV: player + ground
         │           ├─→ Group by Opposition
         │           ├─→ Sum runs per opposition
         │           │
         │           └─→ Return: {labels: [...], data: [...]}
         │
         └─→ Display Stats & Charts on UI
```

**API Endpoints:**
- `GET /api/players` - Get all players
- `GET /api/grounds-for-player?player={name}` - Get grounds for a player
- `GET /api/player-ground-stats?player={name}&ground={ground}` - Get detailed stats
- `GET /api/player-ground-chart-data?player={name}&ground={ground}` - Get chart data

**Data Source:** `odi_batting_cleaned.csv`

---

### 3. Bowling Performance Page Data Flow

```
USER → BowlingPerformancePage
         │
         ├─→ Step 1: Load Players
         │     │
         │     └─→ GET /api/bowling/players
         │           │
         │           ├─→ Read odi_bowling_cleaned.csv
         │           ├─→ Extract unique player names
         │           │
         │           └─→ Return: ["Player1", "Player2", ...]
         │
         ├─→ Step 2: User Selects Player
         │     │
         │     └─→ GET /api/bowling/grounds-for-player?player={name}
         │           │
         │           ├─→ Filter CSV by player name
         │           ├─→ Extract unique grounds
         │           │
         │           └─→ Return: ["Ground1", "Ground2", ...]
         │
         ├─→ Step 3: User Selects Ground
         │     │
         │     └─→ GET /api/bowling/player-ground-stats?player={name}&ground={ground}
         │           │
         │           ├─→ Filter CSV: player + ground
         │           ├─→ Calculate: matches, wickets, runsConceded
         │           ├─→ Calculate: economy, average
         │           ├─→ Find: bestOpposition
         │           │
         │           └─→ Return: {matches, wickets, economy, average, ...}
         │
         └─→ Display Stats on UI
```

**API Endpoints:**
- `GET /api/bowling/players` - Get all bowling players
- `GET /api/bowling/grounds-for-player?player={name}` - Get grounds for a bowler
- `GET /api/bowling/player-ground-stats?player={name}&ground={ground}` - Get bowling stats

**Data Source:** `odi_bowling_cleaned.csv`

---

### 4. Best XI Suggestion Page Data Flow

```
USER → BestXISelectionPage
         │
         ├─→ Step 1: Load Dropdowns
         │     │
         │     ├─→ GET /api/ml/oppositions
         │     │     │
         │     │     ├─→ Read srilanka player 11 dataset.csv
         │     │     ├─→ Extract unique Opponent_Team values
         │     │     │
         │     │     └─→ Return: ["India", "Australia", ...]
         │     │
         │     └─→ Pitch Types: ["Batting Friendly", "Bowling Friendly", ...] (hardcoded)
         │
         ├─→ Step 2: Load Player Pool
         │     │
         │     └─→ GET /api/best-xi/players
         │           │
         │           ├─→ Query MySQL: SELECT * FROM best_xi_players
         │           │
         │           └─→ Return: [{id, player_name, player_type, role}, ...]
         │
         ├─→ Step 3: User Selects Conditions & Clicks "Suggest Best XI"
         │     │
         │     └─→ GET /api/suggest-best-xi?opposition={opp}&pitch={pitch}
         │           │
         │           ├─→ Read srilanka player 11 dataset.csv
         │           ├─→ Get unique players from CSV
         │           │
         │           ├─→ For each player:
         │           │     │
         │           │     ├─→ Prepare input: {Player_Name, Player_Type, Opponent_Team, Pitch_Type, Weather}
         │           │     ├─→ Load ML Model: best_xi_model.joblib
         │           │     ├─→ Predict score using ML model
         │           │     │
         │           │     └─→ Store: {name, type, role, score}
         │           │
         │           ├─→ Sort players by predicted score (descending)
         │           ├─→ Select best wicket keeper (if available)
         │           ├─→ Select top 10 remaining players
         │           │
         │           └─→ Return: [{name, role}, ...] (11 players)
         │
         ├─→ Step 4: User Can Manage Player Pool
         │     │
         │     ├─→ POST /api/best-xi/players
         │     │     │
         │     │     ├─→ Insert into MySQL: best_xi_players table
         │     │     │
         │     │     └─→ Return: {id, player_name, player_type, role}
         │     │
         │     ├─→ PUT /api/best-xi/players/{id}
         │     │     │
         │     │     ├─→ Update MySQL: best_xi_players table
         │     │     │
         │     │     └─→ Return: Updated record
         │     │
         │     └─→ DELETE /api/best-xi/players/{id}
         │           │
         │           ├─→ Delete from MySQL: best_xi_players table
         │           │
         │           └─→ Return: Success message
         │
         └─→ Display Suggested XI on UI (with Edit/Delete buttons)
```

**API Endpoints:**
- `GET /api/ml/oppositions` - Get opposition teams from CSV
- `GET /api/ml/weather-types` - Get weather types from CSV
- `GET /api/best-xi/players` - Get player pool from MySQL
- `POST /api/best-xi/players` - Add player to pool
- `PUT /api/best-xi/players/{id}` - Update player in pool
- `DELETE /api/best-xi/players/{id}` - Delete player from pool
- `GET /api/suggest-best-xi?opposition={opp}&pitch={pitch}` - Generate Best XI

**Data Sources:**
- `srilanka player 11 dataset.csv` (for ML predictions)
- `best_xi_model.joblib` (ML model)
- MySQL `best_xi_players` table (player pool)

---

### 5. Manage Dataset Page Data Flow

```
USER → ManageDatasetPage
         │
         ├─→ Step 1: Fill Form (Player, Opponent, Pitch, Weather, Stats)
         │
         ├─→ Step 2: Check if Condition Exists
         │     │
         │     └─→ GET /api/dataset/check-condition?player_name={name}&opposition={opp}&pitch={pitch}&weather={weather}
         │           │
         │           ├─→ Query MySQL: SELECT * FROM player_performance_records
         │           │                WHERE player_name = ? AND opponent_team = ?
         │           │                AND pitch_type = ? AND weather = ?
         │           │
         │           └─→ Return: {exists: true/false}
         │
         ├─→ Step 3: Add or Update Record
         │     │
         │     ├─→ If NOT exists:
         │     │     │
         │     │     └─→ POST /api/dataset/add-record
         │     │           │
         │     │           ├─→ Check for duplicate (unique constraint)
         │     │           ├─→ Insert into MySQL: player_performance_records table
         │     │           │     Fields: player_name, player_type, role, runs,
         │     │           │             balls_faced, strike_rate, wickets_taken,
         │     │           │             overs_bowled, runs_conceded, opponent_team,
         │     │           │             pitch_type, weather, created_at, updated_at
         │     │           │
         │     │           └─→ Return: {message: "Record added", record: {...}}
         │     │
         │     └─→ If EXISTS:
         │           │
         │           └─→ PUT /api/dataset/update-record
         │                 │
         │                 ├─→ Find record in MySQL: player_performance_records
         │                 ├─→ Update fields: runs, balls_faced, strike_rate, etc.
         │                 ├─→ Update updated_at timestamp
         │                 │
         │                 └─→ Return: {message: "Record updated", record: {...}}
         │
         ├─→ Step 4: Reload Dataset (Optional)
         │     │
         │     └─→ POST /api/dataset/reload
         │           │
         │           ├─→ Reload CSV file into memory (for ML model)
         │           │
         │           └─→ Return: {message: "Dataset reloaded", rows: count}
         │
         └─→ Display Success/Error Message on UI
```

**API Endpoints:**
- `GET /api/dataset/check-condition` - Check if condition exists
- `POST /api/dataset/add-record` - Add new record to MySQL
- `PUT /api/dataset/update-record` - Update existing record in MySQL
- `GET /api/dataset/records` - List all records
- `DELETE /api/dataset/records/{id}` - Delete a record
- `POST /api/dataset/reload` - Reload CSV dataset

**Data Storage:** MySQL `player_performance_records` table

---

## 🗄️ Database Schema

### Table 1: `best_xi_players`
```sql
CREATE TABLE best_xi_players (
    id INT PRIMARY KEY AUTO_INCREMENT,
    player_name VARCHAR(120) NOT NULL UNIQUE,
    player_type VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'Batsman'
);
```

**Purpose:** Stores the pool of players available for Best XI selection

**Operations:**
- CREATE: Add new player to pool
- READ: Get all players for dropdown/selection
- UPDATE: Modify player type or role
- DELETE: Remove player from pool

---

### Table 2: `player_performance_records`
```sql
CREATE TABLE player_performance_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    player_name VARCHAR(120) NOT NULL,
    player_type VARCHAR(50) NOT NULL,
    role VARCHAR(50),
    runs INT DEFAULT 0,
    balls_faced INT DEFAULT 0,
    strike_rate FLOAT DEFAULT 0.0,
    wickets_taken INT DEFAULT 0,
    overs_bowled FLOAT DEFAULT 0.0,
    runs_conceded INT DEFAULT 0,
    opponent_team VARCHAR(100) NOT NULL,
    pitch_type VARCHAR(50) NOT NULL,
    weather VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_player_condition (player_name, opponent_team, pitch_type, weather)
);
```

**Purpose:** Stores player performance data for specific conditions (opponent, pitch, weather)

**Operations:**
- CREATE: Add new performance record
- READ: Check if condition exists, list records
- UPDATE: Modify performance stats
- DELETE: Remove performance record

---

## 📁 File-Based Data Sources

### 1. `odi_batting_cleaned.csv`
**Purpose:** Historical batting performance data

**Used By:**
- Homepage (stats calculation)
- Batting Performance Page (player stats)

**Columns:** Player Name, Ground, Opposition, Runs, BF, 4s, 6s, Dismissal, Pos

---

### 2. `odi_bowling_cleaned.csv`
**Purpose:** Historical bowling performance data

**Used By:**
- Homepage (stats calculation)
- Bowling Performance Page (bowler stats)

**Columns:** Player Name, Ground, Opposition, Overs, Runs, Wkts

---

### 3. `srilanka player 11 dataset.csv`
**Purpose:** Training data for ML model and Best XI suggestions

**Used By:**
- Best XI Suggestion (ML predictions)
- Manage Dataset (reference data)

**Columns:** Player_Name, Player_Type, Role, Runs, Balls_Faced, Strike_Rate, Wickets_Taken, Overs_Bowled, Runs_Conceded, Opponent_Team, Pitch_Type, Weather

---

### 4. `best_xi_model.joblib`
**Purpose:** Trained machine learning model for predicting player performance

**Used By:**
- Best XI Suggestion (score prediction)

**Input Features:** Player_Name, Player_Type, Opponent_Team, Pitch_Type, Weather

**Output:** Predicted performance score

---

## 🔀 Complete User Journey Flow

### Journey 1: View Homepage Stats
```
User Opens Site
    ↓
HomePage Component Loads
    ↓
GET /api/homepage-stats
    ↓
Backend Reads CSV Files
    ↓
Calculates Aggregated Stats
    ↓
Returns JSON Response
    ↓
Frontend Displays Stats
```

### Journey 2: Analyze Batting Performance
```
User Navigates to Batting Page
    ↓
GET /api/players → Load Player Dropdown
    ↓
User Selects Player
    ↓
GET /api/grounds-for-player → Load Grounds Dropdown
    ↓
User Selects Ground
    ↓
GET /api/player-ground-stats → Get Detailed Stats
GET /api/player-ground-chart-data → Get Chart Data
    ↓
Frontend Displays Stats & Charts
```

### Journey 3: Generate Best XI
```
User Navigates to Best XI Page
    ↓
GET /api/ml/oppositions → Load Opposition Dropdown
GET /api/best-xi/players → Load Player Pool
    ↓
User Selects Opposition & Pitch
    ↓
User Clicks "Suggest Best XI"
    ↓
GET /api/suggest-best-xi
    ↓
Backend:
  - Reads CSV for unique players
  - For each player: Predict score using ML model
  - Sort by score
  - Select best 11 players
    ↓
Returns 11 Players
    ↓
Frontend Displays Suggested XI
```

### Journey 4: Add Performance Data
```
User Navigates to Manage Dataset Page
    ↓
User Fills Form (Player, Opponent, Pitch, Weather, Stats)
    ↓
User Clicks "Check if Exists"
    ↓
GET /api/dataset/check-condition
    ↓
Query MySQL Database
    ↓
Returns {exists: true/false}
    ↓
User Clicks "Add Record" or "Update Record"
    ↓
POST /api/dataset/add-record OR PUT /api/dataset/update-record
    ↓
Insert/Update in MySQL: player_performance_records
    ↓
Returns Success Message
    ↓
Frontend Shows Success Notification
```

---

## 🔐 Data Flow Security & Validation

### Frontend Validation
- Form field validation (required fields)
- Input type validation (numbers, strings)
- User feedback (error messages)

### Backend Validation
- Required field checks
- Data type validation
- SQL injection prevention (SQLAlchemy ORM)
- Unique constraint enforcement
- Error handling & rollback

### Database Constraints
- Primary keys (auto-increment)
- Unique constraints (prevent duplicates)
- Foreign key relationships (if needed)
- Timestamps (created_at, updated_at)

---

## 📊 Data Flow Summary Table

| Page | Data Source | Storage | API Endpoints | Operations |
|------|-------------|---------|---------------|------------|
| Homepage | CSV Files | Read-only | `/api/homepage-stats` | READ |
| Batting | CSV Files | Read-only | `/api/players`, `/api/grounds-for-player`, `/api/player-ground-stats`, `/api/player-ground-chart-data` | READ |
| Bowling | CSV Files | Read-only | `/api/bowling/players`, `/api/bowling/grounds-for-player`, `/api/bowling/player-ground-stats` | READ |
| Best XI | CSV + MySQL + ML Model | Read/Write | `/api/best-xi/*`, `/api/suggest-best-xi`, `/api/ml/*` | READ, CREATE, UPDATE, DELETE |
| Manage Dataset | MySQL | Read/Write | `/api/dataset/*` | READ, CREATE, UPDATE, DELETE |

---

## 🚀 System Initialization Flow

```
1. Backend Server Starts
   ↓
2. Load Environment Variables (.env)
   ↓
3. Initialize Flask App
   ↓
4. Connect to MySQL Database
   ↓
5. Create Database Tables (db.create_all())
   ↓
6. Load CSV Files into Memory:
   - odi_batting_cleaned.csv
   - odi_bowling_cleaned.csv
   - srilanka player 11 dataset.csv
   ↓
7. Load ML Model (best_xi_model.joblib)
   ↓
8. Seed Database (if tables empty):
   - Populate best_xi_players from CSV
   ↓
9. Start Flask Server (Port 5000)
   ↓
10. Frontend Connects (Port 3000)
    ↓
11. System Ready for User Requests
```

---

## 📝 Notes

1. **CSV Files**: Used for read-only historical data and ML model training
2. **MySQL Database**: Used for dynamic data that users can add/modify
3. **ML Model**: Used for predictions in Best XI suggestions
4. **CORS**: Enabled for frontend-backend communication
5. **Error Handling**: All endpoints have try-catch blocks
6. **Data Validation**: Both frontend and backend validation
7. **Unique Constraints**: Prevent duplicate records in database

---

**Last Updated:** 2024
**Version:** 1.0

