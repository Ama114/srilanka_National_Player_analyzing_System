from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BestXIPlayer(db.Model):
    __tablename__ = 'best_xi_players'

    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(120), nullable=False, unique=True)
    player_type = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Batsman')

    def to_dict(self):
        return {
            "id": self.id,
            "player_name": self.player_name,
            "player_type": self.player_type,
            "role": self.role
        }

class PlayerPerformanceRecord(db.Model):
    __tablename__ = 'player_performance_records'

    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(120), nullable=False)
    player_type = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50))
    runs = db.Column(db.Integer, default=0)
    balls_faced = db.Column(db.Integer, default=0)
    strike_rate = db.Column(db.Float, default=0.0)
    wickets_taken = db.Column(db.Integer, default=0)
    overs_bowled = db.Column(db.Float, default=0.0)
    runs_conceded = db.Column(db.Integer, default=0)
    opponent_team = db.Column(db.String(100), nullable=False)
    pitch_type = db.Column(db.String(50), nullable=False)
    weather = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Composite unique constraint
    __table_args__ = (
        db.UniqueConstraint('player_name', 'opponent_team', 'pitch_type', 'weather', name='unique_player_condition'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "Player_Name": self.player_name,
            "Player_Type": self.player_type,
            "Role": self.role,
            "Runs": self.runs,
            "Balls_Faced": self.balls_faced,
            "Strike_Rate": self.strike_rate,
            "Wickets_Taken": self.wickets_taken,
            "Overs_Bowled": self.overs_bowled,
            "Runs_Conceded": self.runs_conceded,
            "Opponent_Team": self.opponent_team,
            "Pitch_Type": self.pitch_type,
            "Weather": self.weather,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }