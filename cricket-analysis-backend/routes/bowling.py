from flask import Blueprint, jsonify, request
from models import db, ODIPerformance
from sqlalchemy import func, distinct

bowling_bp = Blueprint('bowling', __name__)

@bowling_bp.route('/api/bowling/players', methods=['GET'])
def get_bowling_players():
    match_type = request.args.get('matchType', 'ODI')
    
    # Use database only for ODI
    if match_type.upper() == 'ODI':
        try:
            players = db.session.query(distinct(ODIPerformance.player_name)).filter(
                ODIPerformance.wickets > 0  # Only players who have taken wickets
            ).all()
            players_list = sorted([p[0] for p in players if p[0]])
            return jsonify(players_list)
        except Exception as e:
            print(f"Error fetching bowling players from database: {e}")
            return jsonify({"error": "Database error occurred"}), 500
    
    return jsonify({"error": "Only ODI match type is supported"}), 400

@bowling_bp.route('/api/bowling/grounds-for-player', methods=['GET'])
def get_bowling_grounds_for_player():
    player_name = request.args.get('player')
    match_type = request.args.get('matchType', 'ODI')
    
    if not player_name:
        return jsonify([])
    
    # Use database only for ODI
    if match_type.upper() == 'ODI':
        try:
            grounds = db.session.query(distinct(ODIPerformance.ground)).filter(
                ODIPerformance.player_name == player_name,
                ODIPerformance.wickets > 0  # Only grounds where player bowled
            ).all()
            grounds_list = sorted([g[0] for g in grounds if g[0]])
            return jsonify(grounds_list)
        except Exception as e:
            print(f"Error fetching bowling grounds from database: {e}")
            return jsonify({"error": "Database error occurred"}), 500
    
    return jsonify({"error": "Only ODI match type is supported"}), 400

@bowling_bp.route('/api/bowling/player-ground-stats', methods=['GET'])
def get_bowling_stats():
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
                ODIPerformance.wickets > 0  # Only bowling records
            ).all()
            
            if not performances:
                return jsonify({'message': 'No bowling data found'}), 404
            
            total_matches = sum(p.matches for p in performances)
            total_wickets = sum(p.wickets for p in performances)
            avg_economy = sum(p.economy for p in performances) / len(performances) if performances else 0
            
            # Extract runs_conceded from notes field if available
            total_runs_conceded = 0
            for p in performances:
                if p.notes and 'runs_conceded:' in p.notes:
                    try:
                        runs_conceded = int(p.notes.split('runs_conceded:')[1].split(',')[0])
                        total_runs_conceded += runs_conceded
                    except:
                        pass
            
            # If not in notes, estimate from economy
            if total_runs_conceded == 0 and avg_economy > 0:
                # Average ODI bowler bowls ~8-10 overs per match, use 9 as average
                avg_overs_per_match = 9
                total_runs_conceded = int(avg_economy * avg_overs_per_match * total_matches)
            
            # Find best opposition by wickets
            opposition_wickets = {}
            for p in performances:
                if p.opposition not in opposition_wickets:
                    opposition_wickets[p.opposition] = 0
                opposition_wickets[p.opposition] += p.wickets
            
            best_opposition = max(opposition_wickets.items(), key=lambda x: x[1])[0] if opposition_wickets else 'N/A'
            
            # Calculate bowling average (runs per wicket)
            bowling_average = (total_runs_conceded / total_wickets) if total_wickets > 0 else float('inf')
            
            stats = {
                "matches": total_matches,
                "wickets": total_wickets,
                "runsConceded": total_runs_conceded,
                "economy": round(avg_economy, 2) if avg_economy > 0 else 0,
                "average": round(bowling_average, 2) if bowling_average != float('inf') else 'N/A',
                "bestOpposition": best_opposition
            }
            return jsonify(stats)
        except Exception as e:
            print(f"Error fetching bowling stats from database: {e}")
            return jsonify({"error": "Database error occurred"}), 500
    
    return jsonify({"error": "Only ODI match type is supported"}), 400