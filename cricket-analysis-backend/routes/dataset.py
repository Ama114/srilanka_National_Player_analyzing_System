from flask import Blueprint, jsonify, request
from models import db, PlayerPerformanceRecord
from sqlalchemy.exc import SQLAlchemyError
import data_loader

dataset_bp = Blueprint('dataset', __name__)

@dataset_bp.route('/api/dataset/check-condition', methods=['GET'])
def check_condition_in_dataset():
    player_name = request.args.get('player_name')
    opposition = request.args.get('opposition')
    pitch = request.args.get('pitch')
    weather = request.args.get('weather')
    
    if not all([player_name, opposition, pitch, weather]):
        return jsonify({"error": "All parameters required"}), 400
    
    try:
        condition_exists = PlayerPerformanceRecord.query.filter_by(
            player_name=player_name,
            opponent_team=opposition,
            pitch_type=pitch,
            weather=weather
        ).first() is not None
        return jsonify({"exists": bool(condition_exists)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dataset_bp.route('/api/dataset/add-record', methods=['POST'])
def add_dataset_record():
    data = request.get_json() or {}
    required = ['Player_Name', 'Player_Type', 'Opponent_Team', 'Pitch_Type', 'Weather']
    if not all(f in data for f in required):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        
        new_record = PlayerPerformanceRecord(
            player_name=data['Player_Name'],
            player_type=data.get('Player_Type', 'Batsman'),
            role=data.get('Role', data.get('Player_Type', 'Batsman')),
            runs=int(data.get('Runs', 0)),
            balls_faced=int(data.get('Balls_Faced', 0)),
            strike_rate=float(data.get('Strike_Rate', 0.0)),
            wickets_taken=int(data.get('Wickets_Taken', 0)),
            overs_bowled=float(data.get('Overs_Bowled', 0.0)),
            runs_conceded=int(data.get('Runs_Conceded', 0)),
            opponent_team=data['Opponent_Team'],
            pitch_type=data['Pitch_Type'],
            weather=data['Weather']
        )
        
        db.session.add(new_record)
        db.session.commit()
        return jsonify({"message": "Record added", "record": new_record.to_dict()}), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@dataset_bp.route('/api/dataset/update-record', methods=['PUT'])
def update_dataset_record():
    data = request.get_json() or {}
    required = ['Player_Name', 'Opponent_Team', 'Pitch_Type', 'Weather']
    if not all(f in data for f in required):
        return jsonify({"error": "Missing identification fields"}), 400
    
    try:
        record = PlayerPerformanceRecord.query.filter_by(
            player_name=data['Player_Name'],
            opponent_team=data['Opponent_Team'],
            pitch_type=data['Pitch_Type'],
            weather=data['Weather']
        ).first()
        
        if not record:
            return jsonify({"error": "Record not found"}), 404
        
        if 'Runs' in data: record.runs = int(data['Runs'])
        if 'Balls_Faced' in data: record.balls_faced = int(data['Balls_Faced'])
        if 'Strike_Rate' in data: record.strike_rate = float(data['Strike_Rate'])
        if 'Wickets_Taken' in data: record.wickets_taken = int(data['Wickets_Taken'])
        if 'Overs_Bowled' in data: record.overs_bowled = float(data['Overs_Bowled'])
        if 'Runs_Conceded' in data: record.runs_conceded = int(data['Runs_Conceded'])
        
        db.session.commit()
        return jsonify({"message": "Record updated", "record": record.to_dict()}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@dataset_bp.route('/api/dataset/records', methods=['GET'])
def list_dataset_records():
    records = PlayerPerformanceRecord.query.order_by(PlayerPerformanceRecord.created_at.desc()).all()
    return jsonify([record.to_dict() for record in records])

@dataset_bp.route('/api/dataset/records/<int:record_id>', methods=['DELETE'])
def delete_dataset_record(record_id):
    try:
        record = PlayerPerformanceRecord.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Record deleted"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- 6. Reload Dataset (ML Model සඳහා) ---
@dataset_bp.route('/api/dataset/reload', methods=['POST'])
def reload_dataset():
    try:
        # data_loader file එකේ තියෙන function එක call කරනවා
        if data_loader.load_ml_dataset():
            return jsonify({
                "message": "Dataset reloaded successfully", 
                "rows": len(data_loader.df_players_ml)
            }), 200
        else:
            return jsonify({"error": "Failed to reload dataset"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500