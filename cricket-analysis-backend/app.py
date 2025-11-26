from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import pymysql
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

# Import Modules
from models import db, BestXIPlayer
import data_loader

# Import Blueprints
from routes.home import home_bp
from routes.batting import batting_bp
from routes.bowling import bowling_bp
from routes.dataset import dataset_bp
from routes.best_xi import best_xi_bp

pymysql.install_as_MySQLdb()
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB with App
db.init_app(app)

# Register Blueprints
app.register_blueprint(home_bp)
app.register_blueprint(batting_bp)
app.register_blueprint(bowling_bp)
app.register_blueprint(dataset_bp)
app.register_blueprint(best_xi_bp)

def seed_best_xi_players():
    """Populate Best XI table from CSV if empty"""
    if BestXIPlayer.query.count() > 0: return
    if data_loader.df_players_ml.empty: return

    unique_players = (
        data_loader.df_players_ml[['Player_Name', 'Player_Type', 'Role']]
        .drop_duplicates()
        .dropna(subset=['Player_Name', 'Player_Type'])
    )

    bulk_players = []
    for _, row in unique_players.iterrows():
        role_value = row['Role'] if pd.notna(row['Role']) else row['Player_Type']
        if row['Player_Name'] in data_loader.WICKET_KEEPER_NAMES:
            role_value = 'Wicket Keeper'
        elif row['Player_Name'] in data_loader.ALL_ROUNDER_NAMES:
            role_value = 'All-Rounder'
            
        bulk_players.append(
            BestXIPlayer(
                player_name=row['Player_Name'],
                player_type=row['Player_Type'],
                role=role_value
            )
        )

    try:
        db.session.bulk_save_objects(bulk_players)
        db.session.commit()
        print(f"Seeded {len(bulk_players)} Best XI players into MySQL.")
    except SQLAlchemyError as err:
        db.session.rollback()
        print(f"Failed to seed: {err}")

# Create Tables and Run
with app.app_context():
    try:
        db.create_all()
        print("✓ Database tables created/verified")
        
        # Initialize match type data
        data_loader.initialize_match_type_data(app)
        print("✓ Match type data loaded (ODI, T20, Test)")
        
        seed_best_xi_players()
        print("✓ Best XI players seeded")
    except Exception as e:
        print(f"✗ Initialization error: {e}")

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🏏 Sri Lanka Cricket Analysis System Started")
    print("="*50)
    print(f"API running on: http://localhost:5000")
    print(f"ML model loaded: {data_loader.model is not None}")
    print(f"Available match types: {', '.join(data_loader.get_all_match_types())}")
    
    for match_type in data_loader.get_all_match_types():
        batting_count = len(data_loader.get_dataset(match_type, 'batting'))
        bowling_count = len(data_loader.get_dataset(match_type, 'bowling'))
        print(f"  {match_type}: {batting_count} batting, {bowling_count} bowling records")
    
    print(f"ML dataset: {len(data_loader.df_players_ml)} records")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)