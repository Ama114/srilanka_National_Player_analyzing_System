from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()

class BestXIPlayer(db.Model):
    __tablename__ = 'best_xi_players'
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(120), nullable=False, unique=True)
    player_type = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Batsman')

    def to_dict(self):
        return { "id": self.id, "player_name": self.player_name, "player_type": self.player_type, "role": self.role }

class PlayerPerformanceRecord(db.Model):
    __tablename__ = 'player_performance_records'

    id = db.Column(db.Integer, primary_key=True)
    
    # --- Basic Info ---
    player_name = db.Column(db.String(120), nullable=False)
    player_type = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50))
    
    # --- Batting Stats ---
    runs = db.Column(db.Integer, default=0)
    balls_faced = db.Column(db.Integer, default=0)
    strike_rate = db.Column(db.Float, default=0.0)
    
    # --- Bowling Stats ---
    wickets_taken = db.Column(db.Integer, default=0)
    overs_bowled = db.Column(db.Float, default=0.0)
    runs_conceded = db.Column(db.Integer, default=0)
    
    # --- Match Conditions ---
    opponent_team = db.Column(db.String(100), nullable=False)
    pitch_type = db.Column(db.String(50), nullable=False)
    weather = db.Column(db.String(50), nullable=False)
    
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # මෙතැන තිබූ __table_args__ (Unique Constraint) කොටස ඉවත් කරන ලදී.
    # දැන් එකම ක්‍රීඩකයාට සමාන අවස්ථා කිහිපයක් තිබිය හැක.

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
            "Weather": self.weather
        }

class GeneratedBestXITeam(db.Model):
    __tablename__ = 'generated_best_xi_teams'

    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(200))  # e.g., "Bangladesh vs ODI - Balanced Pitch"
    opposition = db.Column(db.String(100), nullable=False)
    pitch_type = db.Column(db.String(50), nullable=False)
    weather = db.Column(db.String(50), nullable=False)
    match_type = db.Column(db.String(20), nullable=False, default='ODI')
    players_json = db.Column(db.Text, nullable=False)  # JSON string of players array
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "team_name": self.team_name,
            "opposition": self.opposition,
            "pitch_type": self.pitch_type,
            "weather": self.weather,
            "match_type": self.match_type,
            "players": json.loads(self.players_json) if self.players_json else [],
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

def seed_database(data_loader):
    try:
        db.create_all()

        # Performance Records Seeding
        if PlayerPerformanceRecord.query.count() == 0:
            print("Seeding Player Performance Records from CSV...")
            try:
                df_ml = pd.read_csv('srilanka player 11 dataset.csv')
                df_ml.columns = df_ml.columns.str.strip() 
                
                bulk_records = []
                for _, row in df_ml.iterrows():
                    record = PlayerPerformanceRecord(
                        player_name=row.get('Player_Name') or row.get('Player Name'),
                        player_type=row.get('Player_Type', 'Batsman'),
                        role=row.get('Role', 'Batsman'),
                        opponent_team=row.get('Opponent_Team') or row.get('Opponent Team'),
                        pitch_type=row.get('Pitch_Type') or row.get('Pitch Type'),
                        weather=row.get('Weather', 'Balanced'),
                        runs=row.get('Runs', 0),
                        balls_faced=row.get('Balls_Faced', 0),
                        strike_rate=row.get('Strike_Rate', 0),
                        wickets_taken=row.get('Wickets', 0),
                        overs_bowled=row.get('Overs', 0),
                        runs_conceded=row.get('Runs_Conceded', 0)
                    )
                    bulk_records.append(record)
                
                db.session.bulk_save_objects(bulk_records)
                db.session.commit()
                print(f"Successfully seeded {len(bulk_records)} records.")
            except Exception as e:
                print(f"Error processing CSV: {e}")

        # Best XI Roster Seeding
        if BestXIPlayer.query.count() == 0 and PlayerPerformanceRecord.query.count() > 0:
            print("Seeding Best XI Roster...")
            unique_players = db.session.query(
                PlayerPerformanceRecord.player_name, 
                PlayerPerformanceRecord.player_type, 
                PlayerPerformanceRecord.role
            ).distinct().all()

            bulk_players = []
            for p in unique_players:
                bulk_players.append(BestXIPlayer(player_name=p.player_name, player_type=p.player_type, role=p.role))
            
            db.session.bulk_save_objects(bulk_players)
            db.session.commit()
            print(f"Seeded {len(bulk_players)} players to roster.")

    except SQLAlchemyError as err:
        db.session.rollback()
        print(f"Database Seeding Error: {err}")