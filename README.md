# 🏏 Sri Lanka Cricket Analysis System

Professional cricket analytics platform for analyzing Sri Lankan national team player performance across ODI, T20, and Test formats.

---

## 📊 System Overview

| Component | Details |
|-----------|---------|
| **Backend** | Flask REST API with SQLAlchemy ORM |
| **Database** | MySQL with 3,286 cricket performance records |
| **Frontend** | React.js with Axios HTTP client |
| **Data Formats** | ODI (629 records) • T20 (1,176 records) • Test (1,481 records) |

---

## 🚀 Quick Start

### **Backend Setup**
```bash
cd cricket-analysis-backend
pip install -r requirements.txt
python app.py
```
Runs on: `http://127.0.0.1:5000`

### **Frontend Setup**
```bash
cd cricket-analysis-frontend
npm install
npm start
```
Runs on: `http://localhost:3001`

---

## 🎯 Features

### **1. Best XI Selection** 🏆
- Generate optimal 11-player teams for any match conditions
- Select: Match Type • Opposition • Pitch Type • Weather
- Team Composition: 1 Wicket Keeper + 4 Batsmen + 3 All-Rounders + 3 Bowlers
- **Supports:** ODI, T20, Test

### **2. Batting Performance Analysis** 🏏
- Analyze player batting stats by ground
- View: Average • Strike Rate • Total Runs • 4s & 6s
- **Supports:** ODI, T20, Test

### **3. Bowling Performance Analysis** 🎯
- Analyze player bowling stats by ground
- View: Average • Economy • Total Wickets • Best Opposition
- **Supports:** ODI, T20, Test

### **4. Player Statistics** 📊
- 82 total unique players
- 34 T20 players
- 23 ODI players
- 31 Test players

---

## 📁 Project Structure

```
cricket-analysis-backend/
  ├── app.py                    # Flask application entry point
  ├── models.py                 # Database models (ODI, T20, Test)
  ├── data_loader.py           # Data loading from CSV/Database
  ├── config.py                # MySQL connection config
  ├── routes/
  │   ├── batting.py          # Batting performance endpoints
  │   ├── bowling.py          # Bowling performance endpoints
  │   ├── best_xi.py          # Best XI generation endpoint
  │   ├── home.py             # Homepage statistics
  │   └── dataset.py          # Dataset management
  └── data/
      ├── ODI/                 # 629 ODI records
      ├── T20/                 # 1,176 T20 records (✨ NEW)
      ├── Test/                # 1,481 Test records
      └── DATA_BRIDGE.md       # Complete data mapping

cricket-analysis-frontend/
  ├── src/
  │   ├── pages/
  │   │   ├── HomePage.js
  │   │   ├── BattingPerformancePage.js
  │   │   ├── BowlingPerformancePage.js
  │   │   ├── BestXISelectionPage.js
  │   │   └── ManageBestXIPage.js
  │   ├── components/
  │   ├── styles/
  │   └── App.js
  └── package.json
```

---

## 🔌 API Endpoints

### **Best XI Generation**
```
GET /api/best-xi/generate
Parameters:
  - match_type: ODI | T20 | Test
  - opposition: Team name
  - pitch_type: Balanced | Batting Friendly | Bowling Friendly | Spin Friendly
  - weather: Balanced | Sunny | Cloudy | Humid | Rainy
Returns: Array of 11 players with roles
```

### **Player Statistics**
```
GET /api/players?matchType=ODI|T20|Test
Returns: List of players for selected format

GET /api/grounds-for-player?player=NAME&matchType=ODI|T20|Test
Returns: List of grounds where player performed

GET /api/player-ground-stats?player=NAME&ground=GROUND&matchType=ODI|T20|Test
Returns: Detailed stats for player at specific ground
```

### **Bowling Statistics**
```
GET /api/bowling/players?matchType=ODI|T20|Test
GET /api/bowling/grounds-for-player?player=NAME&matchType=ODI|T20|Test
GET /api/bowling/player-ground-stats?player=NAME&ground=GROUND&matchType=ODI|T20|Test
```

### **Homepage Statistics**
```
GET /api/homepage-stats
Returns: {
  ODI: {totalRuns, totalWickets, topScorer, topBowler},
  T20: {totalRuns, totalWickets, topScorer, topBowler},
  Test: {totalRuns, totalWickets, topScorer, topBowler}
}
```

---

## 📊 Database Statistics

| Metric | ODI | T20 | Test | Total |
|--------|-----|-----|------|-------|
| **Records** | 629 | 1,176 | 1,481 | 3,286 |
| **Players** | 23 | 34 | 31 | 82 |
| **Oppositions** | 12 | 16 | 15 | - |
| **Grounds** | 45 | 57 | 62 | - |
| **Total Runs** | 18,515 | 13,173 | 39,527 | 71,215 |
| **Total Wickets** | 533 | 501 | 726 | 1,760 |

---

## 🔧 Technology Stack

**Backend:**
- Flask 2.3.2 - Web framework
- SQLAlchemy 2.0.21 - ORM
- PyMySQL 1.1.2 - MySQL driver
- Pandas 2.1.4 - Data processing

**Frontend:**
- React 18 - UI framework
- Axios - HTTP client
- CSS3 - Styling

**Database:**
- MySQL 8.0+ - Relational database

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| **README.md** | System overview (you are here) |
| **T20_DATA_LOADED.md** | T20 data loading summary |
| **data/DATA_BRIDGE.md** | Complete data mapping reference |

---

## ✅ System Status

- ✅ Backend: Running on port 5000
- ✅ Frontend: Accessible on port 3001
- ✅ Database: Connected with 3,286 records
- ✅ All three formats: ODI ✓ T20 ✓ Test ✓
- ✅ All pages integrated: Batting ✓ Bowling ✓ Best XI ✓

---

## 🎓 Key Players (Sample)

**Best XI Contenders:**
- Wanindu Hasaranga (All-Rounder)
- Kusal Mendis (Wicket Keeper/Batsman)
- Charith Asalanka (All-Rounder)
- Dhananjaya de Silva (Batsman/All-Rounder)
- Dasun Shanaka (All-Rounder)

---

## 📝 Notes

- Data spans multiple years of Sri Lankan cricket
- Best XI generation uses multi-factor analysis
- All statistics filtered by ground and opposition
- System supports responsive design for mobile/tablet

 
