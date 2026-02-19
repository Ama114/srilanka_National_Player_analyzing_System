from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

# ==========================================
# 1. ODI Performance Model
# ==========================================
class ODIPerformance(db.Model):
    __tablename__ = 'odi_performance'
    id = db.Column(db.Integer, primary_key=True)
    match_type = db.Column(db.String(20), default='ODI')
    date = db.Column(db.Date, nullable=False)
    opposition = db.Column(db.String(100), nullable=False)
    ground = db.Column(db.String(150), nullable=False)
    pitch_type = db.Column(db.String(50))
    weather = db.Column(db.String(50))
    
    player_name = db.Column(db.String(120), nullable=False)
    batting_style = db.Column(db.String(50))
    bowling_style = db.Column(db.String(50))
    main_role = db.Column(db.String(50))
    
    # Batting Stats
    matches = db.Column(db.Integer, default=1)
    batting_runs = db.Column(db.Integer, default=0) 
    bf = db.Column(db.Integer, default=0)
    fours = db.Column(db.Integer, default=0)
    sixes = db.Column(db.Integer, default=0)
    sr = db.Column(db.Float, default=0.0)
    bat_position = db.Column(db.Integer)
    dismissal = db.Column(db.String(50))
    
    # Bowling Stats
    overs = db.Column(db.Float, default=0.0)
    mdns = db.Column(db.Integer, default=0)
    runs_conceded = db.Column(db.Integer, default=0)
    wicket_taken = db.Column(db.Integer, default=0) 
    econ = db.Column(db.Float, default=0.0)
    bowling_pos = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        formatted_date = self.date.strftime('%Y-%m-%d') if self.date and not isinstance(self.date, str) else self.date
        return {
            "id": self.id,
            "match_type": self.match_type,
            "date": formatted_date,
            "opposition": self.opposition,
            "ground": self.ground,
            "pitch_type": self.pitch_type,
            "weather": self.weather,
            "player_name": self.player_name,
            "batting_style": self.batting_style,
            "bowling_style": self.bowling_style,
            "main_role": self.main_role,
            "matches": self.matches,
            "batting_runs": self.batting_runs,
            "bf": self.bf,
            "fours": self.fours,
            "sixes": self.sixes,
            "sr": self.sr,
            "bat_position": self.bat_position,
            "dismissal": self.dismissal,
            "overs": self.overs,
            "mdns": self.mdns,
            "runs_conceded": self.runs_conceded,
            "wicket_taken": self.wicket_taken,
            "econ": self.econ,
            "bowling_pos": self.bowling_pos
        }

# ==========================================
# 2. T20 Performance Model
# ==========================================
class T20Performance(db.Model):
    __tablename__ = 't20_performance'
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(120), nullable=False)
    opposition = db.Column(db.String(120), nullable=False)
    ground = db.Column(db.String(120), nullable=False)
    matches = db.Column(db.Integer, default=1)
    
    # T20 specific batting
    runs = db.Column(db.Integer, default=0)
    strike_rate = db.Column(db.Float, default=0.0)
    average = db.Column(db.Float, default=0.0)
    balls_faced = db.Column(db.Integer, default=0)
    fours = db.Column(db.Integer, default=0)
    sixes = db.Column(db.Integer, default=0)
    bat_position = db.Column(db.Integer)
    dismissal = db.Column(db.String(50))
    
    # T20 specific bowling
    wickets = db.Column(db.Integer, default=0)
    economy = db.Column(db.Float, default=0.0)
    overs = db.Column(db.Float, default=0.0)
    maidens = db.Column(db.Integer, default=0)
    runs_conceded = db.Column(db.Integer, default=0)
    bowling_pos = db.Column(db.Integer)
    
    # Common fields
    match_type = db.Column(db.String(20), default='T20')
    batting_style = db.Column(db.String(50))
    bowling_style = db.Column(db.String(50))
    main_role = db.Column(db.String(50))
    pitch_type = db.Column(db.String(50))
    date = db.Column(db.Date)
    weather = db.Column(db.String(50))
    notes = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        formatted_date = self.date.strftime('%Y-%m-%d') if self.date and not isinstance(self.date, str) else self.date
        return {
            "id": self.id,
            "player_name": self.player_name,
            "opposition": self.opposition,
            "ground": self.ground,
            "matches": self.matches,
            "runs": self.runs,
            "strike_rate": self.strike_rate,
            "average": self.average,
            "wickets": self.wickets,
            "economy": self.economy,
            "match_type": self.match_type,
            "batting_style": self.batting_style,
            "main_role": self.main_role,
            "balls_faced": self.balls_faced,
            "fours": self.fours,
            "sixes": self.sixes,
            "bat_position": self.bat_position,
            "dismissal": self.dismissal,
            "pitch_type": self.pitch_type,
            "date": formatted_date,
            "weather": self.weather,
            "bowling_style": self.bowling_style,
            "overs": self.overs,
            "maidens": self.maidens,
            "runs_conceded": self.runs_conceded,
            "bowling_pos": self.bowling_pos,
            "notes": self.notes
        }


class TestPerformance(db.Model):
    __tablename__ = 'test_performance'
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(120), nullable=False)
    opposition = db.Column(db.String(120), nullable=False)
    ground = db.Column(db.String(120), nullable=False)
    matches = db.Column(db.Integer, default=1)
    
    # Batting Stats
    runs = db.Column(db.Integer, default=0)
    strike_rate = db.Column(db.Float, default=0.0)
    average = db.Column(db.Float, default=0.0)
    balls_faced = db.Column(db.Integer, default=0)
    fours = db.Column(db.Integer, default=0)
    sixes = db.Column(db.Integer, default=0)
    bat_position = db.Column(db.Integer)
    dismissal = db.Column(db.String(50))
    
    # Bowling Stats
    wickets = db.Column(db.Integer, default=0)
    economy = db.Column(db.Float, default=0.0)
    overs = db.Column(db.Float, default=0.0)
    maidens = db.Column(db.Integer, default=0)
    runs_conceded = db.Column(db.Integer, default=0)
    bowling_pos = db.Column(db.Integer)
    
    # Other Info
    match_type = db.Column(db.String(20), default='Test')
    batting_style = db.Column(db.String(50))
    bowling_style = db.Column(db.String(50))
    main_role = db.Column(db.String(50))
    pitch_type = db.Column(db.String(50))
    date = db.Column(db.Date)
    weather = db.Column(db.String(50))
    notes = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        formatted_date = self.date.strftime('%Y-%m-%d') if self.date and not isinstance(self.date, str) else self.date
        return {
            "id": self.id,
            "player_name": self.player_name,
            "opposition": self.opposition,
            "ground": self.ground,
            "matches": self.matches,
            "runs": self.runs,
            "strike_rate": self.strike_rate,
            "average": self.average,
            "wickets": self.wickets,
            "economy": self.economy,
            "match_type": self.match_type,
            "batting_style": self.batting_style,
            "main_role": self.main_role,
            "balls_faced": self.balls_faced,
            "fours": self.fours,
            "sixes": self.sixes,
            "bat_position": self.bat_position,
            "dismissal": self.dismissal,
            "pitch_type": self.pitch_type,
            "date": formatted_date,
            "weather": self.weather,
            "bowling_style": self.bowling_style,
            "overs": self.overs,
            "maidens": self.maidens,
            "runs_conceded": self.runs_conceded,
            "bowling_pos": self.bowling_pos,
            "notes": self.notes
        }

# ==========================================
# 3. OTHER MODELS (Test, Best XI)
# ==========================================
 
class BestXIPlayer(db.Model):
    __tablename__ = 'best_xi_players'
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(120), nullable=False, unique=True)
    player_type = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Batsman')

    def to_dict(self):
        return { "id": self.id, "player_name": self.player_name, "player_type": self.player_type, "role": self.role }

class GeneratedBestXITeam(db.Model):
    __tablename__ = 'generated_best_xi_teams'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(200))
    opposition = db.Column(db.String(100), nullable=False)
    pitch_type = db.Column(db.String(50), nullable=False)
    weather = db.Column(db.String(50), nullable=False)
    match_type = db.Column(db.String(20), nullable=False, default='ODI')
    players_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "team_name": self.team_name,
            "players": json.loads(self.players_json) if self.players_json else []
        }