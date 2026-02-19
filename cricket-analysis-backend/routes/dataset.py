from flask import Blueprint, jsonify, request
from models import db, ODIPerformance, T20Performance, TestPerformance
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

dataset_bp = Blueprint('dataset', __name__)

# ----------------------------------------------------------------
# 1. ADD RECORD (ODI, T20 සහ TEST තුනටම)
# ----------------------------------------------------------------
@dataset_bp.route('/api/dataset/add-record', methods=['POST'])
def add_record():
    data = request.get_json() or {}
    # match_type එක කැපිටල් අකුරෙන් ලබා ගැනීම (Error මගහැරීමට)
    match_type = data.get('match_type', 'ODI').upper()
    
    try:
        # Date string එක Python Date object එකකට හැරවීම
        m_date = None
        if data.get('date'):
            m_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

        if match_type == 'ODI':
            new_record = ODIPerformance(
                match_type='ODI',
                date=m_date,
                opposition=data.get('opposition'),
                ground=data.get('ground'),
                pitch_type=data.get('pitch_type'),
                weather=data.get('weather'),
                player_name=data.get('player_name'),
                main_role=data.get('main_role'),
                batting_style=data.get('batting_style'),
                bowling_style=data.get('bowling_style'),
                batting_runs=int(data.get('batting_runs', 0)),
                bf=int(data.get('bf', 0)),
                fours=int(data.get('fours', 0)),
                sixes=int(data.get('sixes', 0)),
                sr=float(data.get('sr', 0.0)),
                bat_position=int(data.get('bat_position', 0)) if data.get('bat_position') else None,
                dismissal=data.get('dismissal', 'Not Out'),
                overs=float(data.get('overs', 0.0)),
                mdns=int(data.get('mdns', 0)),
                runs_conceded=int(data.get('runs_conceded', 0)),
                wicket_taken=int(data.get('wicket_taken', 0)),
                econ=float(data.get('econ', 0.0)),
                bowling_pos=int(data.get('bowling_pos', 0)) if data.get('bowling_pos') else None
            )
        elif match_type == 'T20':
            new_record = T20Performance(
                match_type='T20',
                date=m_date,
                opposition=data.get('opposition'),
                ground=data.get('ground'),
                pitch_type=data.get('pitch_type'),
                weather=data.get('weather'),
                player_name=data.get('player_name'),
                main_role=data.get('main_role'),
                batting_style=data.get('batting_style'),
                bowling_style=data.get('bowling_style'),
                runs=int(data.get('runs', 0)),
                balls_faced=int(data.get('balls_faced', 0)),
                fours=int(data.get('fours', 0)),
                sixes=int(data.get('sixes', 0)),
                strike_rate=float(data.get('strike_rate', 0.0)),
                average=float(data.get('average', 0.0)),
                bat_position=int(data.get('bat_position', 0)) if data.get('bat_position') else None,
                dismissal=data.get('dismissal', 'Not Out'),
                wickets=int(data.get('wickets', 0)),
                overs=float(data.get('overs', 0.0)),
                maidens=int(data.get('maidens', 0)),
                runs_conceded=int(data.get('runs_conceded', 0)),
                economy=float(data.get('economy', 0.0)),
                bowling_pos=int(data.get('bowling_pos', 0)) if data.get('bowling_pos') else None,
                notes=data.get('notes', '')
            )
        elif match_type == 'TEST':
            new_record = TestPerformance(
                match_type='Test',
                date=m_date,
                opposition=data.get('opposition'),
                ground=data.get('ground'),
                pitch_type=data.get('pitch_type'),
                weather=data.get('weather'),
                player_name=data.get('player_name'),
                main_role=data.get('main_role'),
                batting_style=data.get('batting_style'),
                bowling_style=data.get('bowling_style'),
                runs=int(data.get('runs', 0)),
                balls_faced=int(data.get('balls_faced', 0)),
                fours=int(data.get('fours', 0)),
                sixes=int(data.get('sixes', 0)),
                strike_rate=float(data.get('strike_rate', 0.0)),
                average=float(data.get('average', 0.0)),
                bat_position=int(data.get('bat_position', 0)) if data.get('bat_position') else None,
                dismissal=data.get('dismissal', 'Not Out'),
                wickets=int(data.get('wickets', 0)),
                overs=float(data.get('overs', 0.0)),
                maidens=int(data.get('maidens', 0)),
                runs_conceded=int(data.get('runs_conceded', 0)),
                economy=float(data.get('economy', 0.0)),
                bowling_pos=int(data.get('bowling_pos', 0)) if data.get('bowling_pos') else None,
                notes=data.get('notes', '')
            )

        db.session.add(new_record)
        db.session.commit()
        return jsonify({"message": f"{match_type} Record added successfully!"}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Dataset Save Error: {e}")
        return jsonify({"error": str(e)}), 500

# ----------------------------------------------------------------
# 2. CHECK EXISTENCE
# ----------------------------------------------------------------
@dataset_bp.route('/api/dataset/check-condition', methods=['GET'])
def check_condition():
    player_name = request.args.get('player_name')
    opposition = request.args.get('opposition')
    m_type = request.args.get('match_type', 'ODI').upper()
    
    if m_type == 'ODI':
        model = ODIPerformance
    elif m_type == 'T20':
        model = T20Performance
    else:
        model = TestPerformance
        
    exists = model.query.filter_by(player_name=player_name, opposition=opposition).first() is not None
    return jsonify({"exists": exists}), 200

# ----------------------------------------------------------------
# 3. GET ALL RECORDS
# ----------------------------------------------------------------
@dataset_bp.route('/api/dataset/records', methods=['GET'])
def list_records():
    m_type = request.args.get('match_type', 'ODI').upper()
    try:
        if m_type == 'ODI':
            model = ODIPerformance
        elif m_type == 'T20':
            model = T20Performance
        else:
            model = TestPerformance
            
        records = model.query.order_by(model.date.desc()).all()
        return jsonify([r.to_dict() for r in records])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------------------------------------------
# 4. DELETE RECORD
# ----------------------------------------------------------------
@dataset_bp.route('/api/dataset/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    m_type = request.args.get('match_type', 'ODI').upper()
    try:
        if m_type == 'ODI':
            model = ODIPerformance
        elif m_type == 'T20':
            model = T20Performance
        else:
            model = TestPerformance
            
        record = model.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Record deleted successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500