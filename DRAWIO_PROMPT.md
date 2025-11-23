# Draw.io System Design & Data Flow Diagram - Prompt Guide

## 📐 System Architecture Diagram Prompt for Draw.io

### Layer 1: User Interface Layer (Top)
```
Create a rectangle labeled "User/Browser" at the top center
- Color: Light Blue (#E3F2FD)
- Icon: User icon
```

### Layer 2: Frontend Layer
```
Create 5 rectangles in a horizontal row below the User layer:

1. "HomePage Component"
   - Color: Light Green (#E8F5E9)
   - Shows: Stats Dashboard
   - API Calls: /api/homepage-stats

2. "BattingPerformancePage Component"
   - Color: Light Green (#E8F5E9)
   - Shows: Player Batting Stats
   - API Calls: /api/players, /api/grounds-for-player, /api/player-ground-stats

3. "BowlingPerformancePage Component"
   - Color: Light Green (#E8F5E9)
   - Shows: Player Bowling Stats
   - API Calls: /api/bowling/players, /api/bowling/grounds-for-player, /api/bowling/player-ground-stats

4. "BestXISelectionPage Component"
   - Color: Light Green (#E8F5E9)
   - Shows: Best XI Team Suggestion
   - API Calls: /api/best-xi/*, /api/suggest-best-xi, /api/ml/*

5. "ManageDatasetPage Component"
   - Color: Light Green (#E8F5E9)
   - Shows: Dataset Management Form
   - API Calls: /api/dataset/*

Connect all Frontend components to "User/Browser" with arrows pointing down
Label: "HTTP Requests (Port 3000)"
```

### Layer 3: API Gateway / Backend Layer
```
Create a large rectangle labeled "Flask Backend Server (Port 5000)" below Frontend
- Color: Light Orange (#FFF3E0)
- Inside, create 5 smaller rectangles:

1. "home_bp (Home Routes)"
   - Endpoints: /api/homepage-stats

2. "batting_bp (Batting Routes)"
   - Endpoints: /api/players, /api/grounds-for-player, /api/player-ground-stats, /api/player-ground-chart-data

3. "bowling_bp (Bowling Routes)"
   - Endpoints: /api/bowling/players, /api/bowling/grounds-for-player, /api/bowling/player-ground-stats

4. "best_xi_bp (Best XI Routes)"
   - Endpoints: /api/best-xi/players, /api/suggest-best-xi, /api/ml/oppositions, /api/ml/weather-types

5. "dataset_bp (Dataset Routes)"
   - Endpoints: /api/dataset/check-condition, /api/dataset/add-record, /api/dataset/update-record, /api/dataset/records

Connect Frontend components to corresponding Backend routes with arrows
Label: "REST API (JSON)"
Color: Blue arrows
```

### Layer 4: Data Processing Layer
```
Create 3 rectangles below Backend:

1. "Data Loader Module"
   - Color: Light Yellow (#FFFDE7)
   - Functions: load_ml_dataset(), load_ml_model()
   - Loads: CSV files, ML model

2. "ML Model Processor"
   - Color: Light Purple (#F3E5F5)
   - Model: best_xi_model.joblib
   - Input: Player data, Conditions
   - Output: Predicted scores

3. "Business Logic"
   - Color: Light Cyan (#E0F7FA)
   - Functions: Team selection, Stats calculation, Data validation

Connect Backend routes to Data Processing with arrows
Label: "Process & Calculate"
```

### Layer 5: Data Storage Layer (Bottom)
```
Create 3 sections at the bottom:

Section 1: MySQL Database
- Large rectangle "MySQL Database"
  - Color: Light Blue (#E1F5FE)
  - Inside create 2 tables:
  
  Table 1: "best_xi_players"
    Columns: id (PK), player_name (UNIQUE), player_type, role
    
  Table 2: "player_performance_records"
    Columns: id (PK), player_name, player_type, role, runs, balls_faced,
             strike_rate, wickets_taken, overs_bowled, runs_conceded,
             opponent_team, pitch_type, weather, created_at, updated_at
    Unique Constraint: (player_name, opponent_team, pitch_type, weather)

Section 2: CSV Files
- Rectangle "CSV Data Files"
  - Color: Light Green (#E8F5E9)
  - List files:
    * odi_batting_cleaned.csv (Batting stats)
    * odi_bowling_cleaned.csv (Bowling stats)
    * srilanka player 11 dataset.csv (ML training data)

Section 3: ML Model File
- Rectangle "ML Model File"
  - Color: Light Pink (#FCE4EC)
  - File: best_xi_model.joblib
  - Purpose: Predict player performance scores

Connect Data Processing to Storage with arrows
Label: "Read/Write Operations"
```

---

## 🔄 Data Flow Diagram Prompt for Draw.io

### Flow 1: Homepage Stats Flow
```
Start: User opens Homepage
  ↓
Process: HomePage Component renders
  ↓
API Call: GET /api/homepage-stats
  ↓
Backend: home_bp.route('/api/homepage-stats')
  ↓
Data Source: Read odi_batting_cleaned.csv
  ↓
Data Source: Read odi_bowling_cleaned.csv
  ↓
Process: Calculate totalRuns, totalWickets
  ↓
Process: Find topScorer, topBowler
  ↓
Response: JSON {totalRuns, totalWickets, topScorer, topBowler}
  ↓
Display: Show stats on Homepage
```

### Flow 2: Batting Performance Analysis Flow
```
Start: User navigates to Batting Page
  ↓
Step 1: Load Players
  API: GET /api/players
  Source: odi_batting_cleaned.csv
  Process: Extract unique player names
  Display: Populate player dropdown
  ↓
Step 2: User selects Player
  API: GET /api/grounds-for-player?player={name}
  Source: Filter CSV by player
  Process: Extract unique grounds
  Display: Populate ground dropdown
  ↓
Step 3: User selects Ground
  API: GET /api/player-ground-stats?player={name}&ground={ground}
  Source: Filter CSV by player + ground
  Process: Calculate stats (matches, runs, average, strike rate)
  Display: Show detailed stats
  ↓
Step 4: Load Chart Data
  API: GET /api/player-ground-chart-data?player={name}&ground={ground}
  Source: Filter CSV by player + ground
  Process: Group by opposition, sum runs
  Display: Show chart visualization
```

### Flow 3: Best XI Suggestion Flow
```
Start: User navigates to Best XI Page
  ↓
Load Dropdowns:
  - GET /api/ml/oppositions → Load from CSV
  - GET /api/ml/weather-types → Load from CSV
  - GET /api/best-xi/players → Load from MySQL
  ↓
User Input: Selects Opposition, Pitch, Weather, Match Type
  ↓
User Action: Clicks "Suggest Best XI"
  ↓
API: GET /api/suggest-best-xi?opposition={opp}&pitch={pitch}&weather={weather}&match_type={type}
  ↓
Backend Process:
  1. Read srilanka player 11 dataset.csv
  2. Get unique players
  3. For each player:
     - Prepare input: {Player_Name, Player_Type, Opponent_Team, Pitch_Type, Weather}
     - Load ML Model: best_xi_model.joblib
     - Predict score using ML model
     - Store: {name, type, role, score}
  4. Sort players by predicted score (descending)
  5. Select best wicket keeper
  6. Select top 10 remaining players
  ↓
Response: JSON array of 11 players [{name, role}, ...]
  ↓
Display: Show Suggested Playing XI with Edit/Delete buttons
```

### Flow 4: Dataset Management Flow
```
Start: User navigates to Manage Dataset Page
  ↓
User Action: Fills form (Player, Opponent, Pitch, Weather, Stats)
  ↓
Step 1: Check Condition
  User clicks "Check if Exists"
  API: GET /api/dataset/check-condition?player_name={name}&opposition={opp}&pitch={pitch}&weather={weather}
  Database: Query player_performance_records table
  Response: {exists: true/false}
  Display: Show status message
  ↓
Step 2: Add/Update Record
  If NOT exists:
    API: POST /api/dataset/add-record
    Database: INSERT INTO player_performance_records
    Response: {message: "Record added", record: {...}}
  
  If EXISTS:
    API: PUT /api/dataset/update-record
    Database: UPDATE player_performance_records
    Response: {message: "Record updated", record: {...}}
  ↓
Step 3: Reload Dataset (Optional)
  API: POST /api/dataset/reload
  Process: Reload CSV file into memory
  Response: {message: "Dataset reloaded"}
  ↓
Display: Show success/error message
```

### Flow 5: Player Pool Management Flow
```
Start: User on Best XI Page
  ↓
Load Player Pool:
  API: GET /api/best-xi/players
  Database: SELECT * FROM best_xi_players
  Display: Show player list
  ↓
User Actions:
  
  Action 1: Add Player
    Form: Fill player_name, player_type, role
    API: POST /api/best-xi/players
    Database: INSERT INTO best_xi_players
    Response: {id, player_name, player_type, role}
    Display: Refresh player list
  
  Action 2: Edit Player
    Click "Edit" button
    Form: Pre-fill with player data
    API: PUT /api/best-xi/players/{id}
    Database: UPDATE best_xi_players
    Response: Updated record
    Display: Refresh player list
  
  Action 3: Delete Player
    Click "Delete" button
    Confirm: "Remove this player?"
    API: DELETE /api/best-xi/players/{id}
    Database: DELETE FROM best_xi_players
    Response: {message: "Player removed"}
    Display: Refresh player list
```

---

## 🎨 Draw.io Component Specifications

### Colors Scheme:
- **User Layer**: #E3F2FD (Light Blue)
- **Frontend Components**: #E8F5E9 (Light Green)
- **Backend Server**: #FFF3E0 (Light Orange)
- **Data Processing**: #FFFDE7 (Light Yellow), #F3E5F5 (Light Purple), #E0F7FA (Light Cyan)
- **MySQL Database**: #E1F5FE (Light Blue)
- **CSV Files**: #E8F5E9 (Light Green)
- **ML Model**: #FCE4EC (Light Pink)

### Arrow Types:
- **HTTP Requests**: Blue solid arrows (→)
- **Data Flow**: Green dashed arrows (⇢)
- **Database Operations**: Red solid arrows (→)
- **Process Flow**: Black solid arrows (→)

### Shapes:
- **Rectangles**: Components, Modules, Pages
- **Cylinders**: Databases
- **Documents**: Files (CSV, Model)
- **Clouds**: External Services (optional)
- **Diamonds**: Decision Points (if/else)

---

## 📊 Detailed Component Connections

### Frontend to Backend Connections:
```
HomePage → home_bp
  - GET /api/homepage-stats

BattingPerformancePage → batting_bp
  - GET /api/players
  - GET /api/grounds-for-player
  - GET /api/player-ground-stats
  - GET /api/player-ground-chart-data

BowlingPerformancePage → bowling_bp
  - GET /api/bowling/players
  - GET /api/bowling/grounds-for-player
  - GET /api/bowling/player-ground-stats

BestXISelectionPage → best_xi_bp
  - GET /api/ml/oppositions
  - GET /api/ml/weather-types
  - GET /api/best-xi/players
  - POST /api/best-xi/players
  - PUT /api/best-xi/players/{id}
  - DELETE /api/best-xi/players/{id}
  - GET /api/suggest-best-xi

ManageDatasetPage → dataset_bp
  - GET /api/dataset/check-condition
  - POST /api/dataset/add-record
  - PUT /api/dataset/update-record
  - GET /api/dataset/records
  - DELETE /api/dataset/records/{id}
  - POST /api/dataset/reload
```

### Backend to Data Sources:
```
home_bp → odi_batting_cleaned.csv
home_bp → odi_bowling_cleaned.csv

batting_bp → odi_batting_cleaned.csv

bowling_bp → odi_bowling_cleaned.csv

best_xi_bp → srilanka player 11 dataset.csv
best_xi_bp → best_xi_model.joblib
best_xi_bp → MySQL (best_xi_players table)

dataset_bp → MySQL (player_performance_records table)
dataset_bp → srilanka player 11 dataset.csv (for reload)
```

---

## 🔐 Security & Validation Flow

```
User Input → Frontend Validation
  - Required fields check
  - Data type validation
  - Format validation
  ↓
HTTP Request → Backend Validation
  - Parameter validation
  - SQL injection prevention (ORM)
  - Data sanitization
  ↓
Database Operation → Constraint Validation
  - Primary key constraints
  - Unique constraints
  - Foreign key constraints (if any)
  ↓
Response → Error Handling
  - Try-catch blocks
  - Rollback on errors
  - User-friendly error messages
```

---

## 📈 System Initialization Flow

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
   - best_xi_players
   - player_performance_records
   ↓
6. Load CSV Files into Memory:
   - odi_batting_cleaned.csv → df_batting
   - odi_bowling_cleaned.csv → df_bowling
   - srilanka player 11 dataset.csv → df_players_ml
   ↓
7. Load ML Model
   - best_xi_model.joblib → model
   ↓
8. Seed Database (if tables empty)
   - Populate best_xi_players from CSV
   ↓
9. Start Flask Server (Port 5000)
   ↓
10. Frontend Connects (Port 3000)
    ↓
11. System Ready for User Requests
```

---

## 🎯 Key Points for Draw.io Diagram:

1. **Use Layers**: Create separate layers for UI, API, Processing, Storage
2. **Color Coding**: Use consistent colors for each component type
3. **Arrow Labels**: Label all arrows with operation types (GET, POST, PUT, DELETE)
4. **Data Flow Direction**: Show data flow from top (User) to bottom (Storage)
5. **Component Details**: Include key endpoints/functions inside each component
6. **Database Schema**: Show table structures with columns
7. **File Icons**: Use document icons for CSV files and model files
8. **Legend**: Add a legend explaining colors and arrow types

---

## 📝 Additional Notes for Thesis:

- **Architecture Pattern**: 3-Tier Architecture (Presentation, Application, Data)
- **API Style**: RESTful API with JSON responses
- **Database**: MySQL with SQLAlchemy ORM
- **ML Integration**: Pre-trained model for predictions
- **Data Sources**: Hybrid (CSV for historical data, MySQL for dynamic data)
- **Frontend Framework**: React.js with React Router
- **Backend Framework**: Flask (Python)
- **Communication**: HTTP/REST API with CORS enabled

---

**Use this prompt in Draw.io to create comprehensive system design and data flow diagrams for your thesis!**

