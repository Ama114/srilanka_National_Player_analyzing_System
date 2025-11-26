from flask import Blueprint, jsonify, request
from models import db, ODIPerformance
from sqlalchemy import func, distinct

batting_bp = Blueprint('batting', __name__)

@batting_bp.route('/api/players', methods=['GET'])
def get_players():
    match_type = request.args.get('matchType', 'ODI')
    
    # Use database only for ODI - Only players who have batting data (runs > 0)
    if match_type.upper() == 'ODI':
        try:
            players = db.session.query(distinct(ODIPerformance.player_name)).filter(
                ODIPerformance.runs > 0  # Only players who have scored runs (batsmen)
            ).all()
            if players:
                players_list = sorted([p[0] for p in players if p[0]])
                return jsonify(players_list)
            return jsonify([])
        except Exception as e:
            print(f"Error fetching players from database: {e}")
            return jsonify({"error": "Database error occurred"}), 500
    
    return jsonify({"error": "Only ODI match type is supported"}), 400

@batting_bp.route('/api/grounds-for-player', methods=['GET'])
def get_grounds_for_player():
    player_name = request.args.get('player')
    match_type = request.args.get('matchType', 'ODI')
    
    if not player_name:
        return jsonify([])
    
    # Use database only for ODI - Only grounds where player has batting data (runs > 0)
    if match_type.upper() == 'ODI':
        try:
            grounds = db.session.query(distinct(ODIPerformance.ground)).filter(
                ODIPerformance.player_name == player_name,
                ODIPerformance.runs > 0  # Only grounds where player has scored runs
            ).all()
            grounds_list = sorted([g[0] for g in grounds if g[0]])
            return jsonify(grounds_list)
        except Exception as e:
            print(f"Error fetching grounds from database: {e}")
            return jsonify({"error": "Database error occurred"}), 500
    
    return jsonify({"error": "Only ODI match type is supported"}), 400

@batting_bp.route('/api/player-ground-stats', methods=['GET'])
def get_player_stats():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    match_type = request.args.get('matchType', 'ODI')
    
    if not player_name or not ground_name:
        return jsonify({'error': 'Parameters required'}), 400
    
    # Use database only for ODI - Only batting records (runs > 0)
    if match_type.upper() == 'ODI':
        try:
            performances = ODIPerformance.query.filter(
                ODIPerformance.player_name == player_name,
                ODIPerformance.ground == ground_name,
                ODIPerformance.runs > 0  # Only batting records (runs > 0)
            ).all()
            
            if not performances:
                return jsonify({'message': 'No data found'}), 404
            
            total_matches = sum(p.matches for p in performances)
            total_runs = sum(p.runs for p in performances)
            total_fours = sum(p.fours for p in performances if p.fours)
            total_sixes = sum(p.sixes for p in performances if p.sixes)
            avg_strike_rate = sum(p.strike_rate for p in performances) / len(performances) if performances else 0
            avg_batting_avg = sum(p.average for p in performances) / len(performances) if performances else 0
            
            # Find best opposition by runs
            opposition_runs = {}
            for p in performances:
                if p.opposition not in opposition_runs:
                    opposition_runs[p.opposition] = 0
                opposition_runs[p.opposition] += p.runs
            
            best_opposition = max(opposition_runs.items(), key=lambda x: x[1])[0] if opposition_runs else 'N/A'
            
            # Find most frequent dismissal
            dismissals = [p.dismissal for p in performances if p.dismissal]
            most_frequent_dismissal = max(set(dismissals), key=dismissals.count) if dismissals else 'N/A'
            
            # Find most frequent batting position
            positions = [p.bat_position for p in performances if p.bat_position]
            recommended_position = int(max(set(positions), key=positions.count)) if positions else 'N/A'
            
            stats = {
                "matches": total_matches,
                "totalRuns": total_runs,
                "mostFrequentDismissal": most_frequent_dismissal,
                "bestOpposition": best_opposition,
                "total4s": total_fours,
                "total6s": total_sixes,
                "average": round(avg_batting_avg, 2) if avg_batting_avg > 0 else 'Not Out',
                "strikeRate": round(avg_strike_rate, 2),
                "recommendedPosition": recommended_position
            }
            return jsonify(stats)
        except Exception as e:
            print(f"Error fetching stats from database: {e}")
            return jsonify({"error": "Database error occurred"}), 500
    
    return jsonify({"error": "Only ODI match type is supported"}), 400

@batting_bp.route('/api/player-ground-chart-data', methods=['GET'])
def get_chart_data():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    match_type = request.args.get('matchType', 'ODI')
    
    if not player_name or not ground_name:
        return jsonify({'error': 'Parameters required'}), 400
    
    # Use database only for ODI
    if match_type.upper() == 'ODI':
        try:
            performances = ODIPerformance.query.filter(
                ODIPerformance.player_name == player_name,
                ODIPerformance.ground == ground_name,
                ODIPerformance.runs > 0  # Only batting records (runs > 0)
            ).all()
            
            if not performances:
                return jsonify({'labels': [], 'data': []})
            
            opposition_runs = {}
            for p in performances:
                if p.opposition not in opposition_runs:
                    opposition_runs[p.opposition] = 0
                opposition_runs[p.opposition] += p.runs
            
            sorted_oppositions = sorted(opposition_runs.items(), key=lambda x: x[1], reverse=True)
            chart_data = {
                'labels': [opp[0] for opp in sorted_oppositions],
                'data': [opp[1] for opp in sorted_oppositions]
            }
            return jsonify(chart_data)
        except Exception as e:
            print(f"Error fetching chart data from database: {e}")
            return jsonify({"error": "Database error occurred"}), 500
    
    return jsonify({"error": "Only ODI match type is supported"}), 400