from flask import Blueprint, jsonify, request
from models import db, ODIPerformance, T20Performance, TestPerformance
from sqlalchemy import func, distinct

bowling_bp = Blueprint('bowling', __name__)

def get_model(match_type):
    # Match type එක upper case කරලා check කිරීම වඩාත් ආරක්ෂිතයි
    m_type = match_type.upper()
    if m_type == 'ODI': return ODIPerformance
    elif m_type == 'T20': return T20Performance
    elif m_type == 'TEST': return TestPerformance
    return ODIPerformance

@bowling_bp.route('/api/bowling/players', methods=['GET'])
def get_bowling_players():
    match_type = request.args.get('matchType', 'ODI').upper()
    
    try:
        model = get_model(match_type)
        # ODI සදහා wicket_taken, අනිත් ඒවා සදහා wickets
        wicket_col = model.wicket_taken if match_type == 'ODI' else model.wickets
        
        players = db.session.query(distinct(model.player_name)).filter(
            wicket_col > 0
        ).all()
        
        players_list = sorted([p[0] for p in players if p[0]])
        return jsonify(players_list)

    except Exception as e:
        print(f"Bowling Players Error: {e}")
        return jsonify({"error": str(e)}), 500

@bowling_bp.route('/api/bowling/grounds-for-player', methods=['GET'])
def get_bowling_grounds_for_player():
    player_name = request.args.get('player')
    match_type = request.args.get('matchType', 'ODI').upper()
    
    if not player_name: return jsonify([])

    try:
        model = get_model(match_type)
        wicket_col = model.wicket_taken if match_type == 'ODI' else model.wickets
        
        grounds = db.session.query(distinct(model.ground)).filter(
            model.player_name == player_name,
            wicket_col > 0
        ).all()
        
        return jsonify(sorted([g[0] for g in grounds if g[0]]))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bowling_bp.route('/api/bowling/player-ground-stats', methods=['GET'])
def get_bowling_stats():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    match_type = request.args.get('matchType', 'ODI').upper()
    
    if not player_name or not ground_name: 
        return jsonify({'error': 'Missing params'}), 400
    
    try:
        model = get_model(match_type)
        wicket_col = model.wicket_taken if match_type == 'ODI' else model.wickets
        
        performances = db.session.query(model).filter(
            model.player_name == player_name,
            model.ground == ground_name,
            wicket_col > 0
        ).all()

        if not performances: 
            return jsonify({'message': 'No data found'}), 404

        # --- CALCULATION STEP ---
        total_matches = len(performances)
        total_wickets = sum(getattr(p, 'wicket_taken' if match_type == 'ODI' else 'wickets') for p in performances)
        total_runs = sum(p.runs_conceded for p in performances)
        
        # Economy එක ODI වල 'econ', අනිත් ඒවගේ 'economy'
        econ_attr = 'econ' if match_type == 'ODI' else 'economy'
        avg_econ = sum(getattr(p, econ_attr, 0) for p in performances) / total_matches

        # Best Opposition Logic
        opp_wkts = {}
        for p in performances:
            opp = p.opposition
            if opp not in opp_wkts: opp_wkts[opp] = 0
            w = getattr(p, 'wicket_taken' if match_type == 'ODI' else 'wickets')
            opp_wkts[opp] += w
            
        best_opp = max(opp_wkts.items(), key=lambda x: x[1])[0] if opp_wkts else 'N/A'
        avg = (total_runs / total_wickets) if total_wickets > 0 else 0

        return jsonify({
            "matches": total_matches,
            "wickets": total_wickets,
            "runsConceded": total_runs,
            "economy": round(avg_econ, 2),
            "average": round(avg, 2),
            "bestOpposition": best_opp
        })

    except Exception as e:
        print(f"Stats Error: {e}")
        return jsonify({"error": str(e)}), 500