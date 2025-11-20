from flask import Blueprint, jsonify, request
from models import db, BestXIPlayer
from sqlalchemy.exc import SQLAlchemyError
import data_loader
import pandas as pd

best_xi_bp = Blueprint('best_xi', __name__)

# --- Dropdowns ---
@best_xi_bp.route('/api/all-grounds', methods=['GET'])
def get_all_grounds():
    if not data_loader.df_batting.empty:
        grounds = data_loader.df_batting['Ground'].unique().tolist()
        return jsonify(sorted(grounds))
    return jsonify([])

@best_xi_bp.route('/api/ml/oppositions', methods=['GET'])
def get_ml_oppositions():
    df = data_loader.df_players_ml
    if df.empty: return jsonify([])
    
    col_name = next((name for name in ['Opponent_Team', 'opponent_team'] if name in df.columns), None)
    if not col_name: return jsonify({"error": "Opponent_Team column not found"}), 500
    
    return jsonify(sorted(df[col_name].dropna().unique().tolist()))

@best_xi_bp.route('/api/ml/weather-types', methods=['GET'])
def get_ml_weather_types():
    df = data_loader.df_players_ml
    if df.empty: return jsonify([])
    
    col_name = next((name for name in ['Weather', 'weather'] if name in df.columns), None)
    if not col_name: return jsonify({"error": "Weather column not found"}), 500
    
    return jsonify(sorted(df[col_name].dropna().unique().tolist()))

# --- CRUD for Best XI ---
@best_xi_bp.route('/api/best-xi/players', methods=['GET'])
def list_best_xi_players():
    players = BestXIPlayer.query.order_by(BestXIPlayer.player_name).all()
    return jsonify([player.to_dict() for player in players])

@best_xi_bp.route('/api/best-xi/players', methods=['POST'])
def create_best_xi_player():
    data = request.get_json() or {}
    if not all(k in data for k in ['player_name', 'player_type', 'role']):
        return jsonify({"error": "Missing fields"}), 400

    try:
        player = BestXIPlayer(
            player_name=data['player_name'],
            player_type=data['player_type'],
            role=data['role']
        )
        db.session.add(player)
        db.session.commit()
        return jsonify(player.to_dict()), 201
    except SQLAlchemyError as err:
        db.session.rollback()
        return jsonify({"error": str(err)}), 500

@best_xi_bp.route('/api/best-xi/players/<int:player_id>', methods=['PUT'])
def update_best_xi_player(player_id):
    data = request.get_json() or {}
    player = BestXIPlayer.query.get_or_404(player_id)
    for field in ['player_name', 'player_type', 'role']:
        if field in data: setattr(player, field, data[field])
    try:
        db.session.commit()
        return jsonify(player.to_dict())
    except SQLAlchemyError as err:
        db.session.rollback()
        return jsonify({"error": str(err)}), 500

@best_xi_bp.route('/api/best-xi/players/<int:player_id>', methods=['DELETE'])
def delete_best_xi_player(player_id):
    player = BestXIPlayer.query.get_or_404(player_id)
    try:
        db.session.delete(player)
        db.session.commit()
        return jsonify({"message": "Player removed"})
    except SQLAlchemyError as err:
        db.session.rollback()
        return jsonify({"error": str(err)}), 500

# --- Prediction Logic ---
@best_xi_bp.route('/api/suggest-best-xi', methods=['GET'])
def suggest_best_xi():
    opposition = request.args.get('opposition')
    pitch = request.args.get('pitch')
    weather = request.args.get('weather') or data_loader.default_weather

    if not all([opposition, pitch, data_loader.model]):
        return jsonify({"error": "Missing parameters or model not loaded"}), 400

    if data_loader.df_players_ml.empty:
        return jsonify({"error": "CSV dataset not loaded"}), 400

    unique_players = data_loader.df_players_ml[['Player_Name', 'Player_Type', 'Role']].drop_duplicates(subset=['Player_Name'])
    
    predictions = []
    for _, row in unique_players.iterrows():
        player_name = row['Player_Name']
        player_type = row['Player_Type'] if pd.notna(row['Player_Type']) else 'Batsman'
        
        input_data = pd.DataFrame({
            'Opponent_Team': [opposition], 'Pitch_Type': [pitch],
            'Weather': [weather], 'Player_Name': [player_name],
            'Player_Type': [player_type]
        })
        
        try:
            predicted_score = data_loader.model.predict(input_data)[0]
            role = row['Role'] if pd.notna(row['Role']) else player_type
            
            if player_name in data_loader.WICKET_KEEPER_NAMES: role = 'Wicket Keeper'
            elif player_name in data_loader.ALL_ROUNDER_NAMES: role = 'All-Rounder'
            
            predictions.append({
                'name': player_name, 'type': player_type,
                'role': role, 'score': float(predicted_score)
            })
        except: continue

    if not predictions: return jsonify({"error": "No predictions generated"}), 400

    predictions.sort(key=lambda x: x['score'], reverse=True)
    
    final_team = []
    team_names = set()
    
    # Select Keeper
    keepers = [p for p in predictions if 'keeper' in str(p['role']).lower()]
    if keepers:
        best_keeper = max(keepers, key=lambda x: x['score'])
        best_keeper['role'] = 'Wicket Keeper'
        final_team.append(best_keeper)
        team_names.add(best_keeper['name'])

    # Fill remaining spots
    for p in predictions:
        if len(final_team) >= 11: break
        if p['name'] not in team_names:
            final_team.append(p)
            team_names.add(p['name'])

    return jsonify(final_team)