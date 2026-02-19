from flask import Blueprint, jsonify, request
from models import db, ODIPerformance, T20Performance, TestPerformance
from sqlalchemy import func, distinct

batting_bp = Blueprint('batting', __name__)

def get_model(match_type):
    # Match type එක standardize කිරීම
    m_type = match_type.upper()
    if m_type == 'ODI': return ODIPerformance
    elif m_type == 'T20': return T20Performance
    elif m_type == 'TEST': return TestPerformance
    return ODIPerformance

@batting_bp.route('/api/players', methods=['GET'])
def get_players():
    match_type = request.args.get('matchType', 'ODI').upper()
    try:
        model = get_model(match_type)
        # ODI සදහා batting_runs, අනිත් ඒවට runs
        run_col = model.batting_runs if match_type == 'ODI' else model.runs
        
        players = db.session.query(distinct(model.player_name)).filter(
            run_col > 0
        ).all()
        
        return jsonify(sorted([p[0] for p in players if p[0]]))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@batting_bp.route('/api/grounds-for-player', methods=['GET'])
def get_grounds_for_player():
    player_name = request.args.get('player')
    match_type = request.args.get('matchType', 'ODI').upper()
    if not player_name: return jsonify([])

    try:
        model = get_model(match_type)
        run_col = model.batting_runs if match_type == 'ODI' else model.runs
        
        grounds = db.session.query(distinct(model.ground)).filter(
            model.player_name == player_name,
            run_col > 0
        ).all()
        
        return jsonify(sorted([g[0] for g in grounds if g[0]]))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@batting_bp.route('/api/player-ground-stats', methods=['GET'])
def get_player_stats():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    match_type = request.args.get('matchType', 'ODI').upper()
    
    try:
        model = get_model(match_type)
        run_col_name = 'batting_runs' if match_type == 'ODI' else 'runs'
        sr_col_name = 'sr' if match_type == 'ODI' else 'strike_rate'
        
        performances = db.session.query(model).filter(
            model.player_name == player_name,
            model.ground == ground_name,
            getattr(model, run_col_name) > 0
        ).all()
        
        if not performances: return jsonify({'message': 'No data found'}), 404

        # --- CALCULATION STEP ---
        total_matches = len(performances)
        total_runs = sum(getattr(p, run_col_name) for p in performances)
        total_fours = sum(p.fours for p in performances if p.fours)
        total_sixes = sum(p.sixes for p in performances if p.sixes)
        avg_sr = sum(getattr(p, sr_col_name, 0) for p in performances) / total_matches
        
        # Best Opposition
        opp_runs = {}
        for p in performances:
            opp = p.opposition
            r = getattr(p, run_col_name)
            opp_runs[opp] = opp_runs.get(opp, 0) + r
        
        best_opp = max(opp_runs.items(), key=lambda x: x[1])[0] if opp_runs else 'N/A'
        avg = total_runs / total_matches if total_matches > 0 else 0

        return jsonify({
            "matches": total_matches,
            "totalRuns": total_runs,
            "bestOpposition": best_opp,
            "total4s": total_fours,
            "total6s": total_sixes,
            "average": round(avg, 2),
            "strikeRate": round(avg_sr, 2),
            "mostFrequentDismissal": "N/A",
            "recommendedPosition": 0
        })

    except Exception as e:
        print(f"Stats Error: {e}")
        return jsonify({"error": str(e)}), 500

@batting_bp.route('/api/player-ground-chart-data', methods=['GET'])
def get_chart_data():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    match_type = request.args.get('matchType', 'ODI').upper()
    
    try:
        model = get_model(match_type)
        run_col_name = 'batting_runs' if match_type == 'ODI' else 'runs'
        
        performances = db.session.query(model).filter(
            model.player_name == player_name,
            model.ground == ground_name,
            getattr(model, run_col_name) > 0
        ).all()
        
        opp_runs = {}
        for p in performances:
            opp = p.opposition
            r = getattr(p, run_col_name)
            opp_runs[opp] = opp_runs.get(opp, 0) + r
            
        sorted_opp = sorted(opp_runs.items(), key=lambda x: x[1], reverse=True)
        
        return jsonify({
            'labels': [x[0] for x in sorted_opp],
            'data': [x[1] for x in sorted_opp]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500