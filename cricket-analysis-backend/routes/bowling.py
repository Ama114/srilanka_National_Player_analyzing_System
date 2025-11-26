from flask import Blueprint, jsonify, request
from models import db, ODIPerformance, T20Performance, TestPerformance
from sqlalchemy import func, distinct

bowling_bp = Blueprint('bowling', __name__)

# Map match types to database models
MATCH_TYPE_MODELS = {
    'ODI': ODIPerformance,
    'T20': T20Performance,
    'TEST': TestPerformance
}

def get_model_for_match_type(match_type):
    """Get the correct database model for the match type"""
    match_type_upper = match_type.upper()
    # Handle 'Test' -> 'TEST' mapping
    if match_type_upper == 'TEST':
        return MATCH_TYPE_MODELS['TEST']
    return MATCH_TYPE_MODELS.get(match_type_upper, ODIPerformance)

@bowling_bp.route('/api/bowling/players', methods=['GET'])
def get_bowling_players():
    match_type = request.args.get('matchType', 'ODI')
    match_type_upper = match_type.upper()
    
    # Validate match type
    if match_type_upper not in MATCH_TYPE_MODELS:
        return jsonify({"error": f"Match type must be one of: ODI, T20, Test"}), 400
    
    try:
        model = get_model_for_match_type(match_type)
        players = db.session.query(distinct(model.player_name)).filter(
            model.wickets > 0  # Only players who have taken wickets
        ).all()
        
        players_list = sorted([p[0] for p in players if p[0]])
        return jsonify(players_list)
    except Exception as e:
        print(f"Error fetching bowling players for {match_type}: {e}")
        return jsonify({"error": "Database error occurred"}), 500

@bowling_bp.route('/api/bowling/grounds-for-player', methods=['GET'])
def get_bowling_grounds_for_player():
    player_name = request.args.get('player')
    match_type = request.args.get('matchType', 'ODI')
    match_type_upper = match_type.upper()
    
    if not player_name:
        return jsonify([])
    
    # Validate match type
    if match_type_upper not in MATCH_TYPE_MODELS:
        return jsonify({"error": f"Match type must be one of: ODI, T20, Test"}), 400
    
    try:
        model = get_model_for_match_type(match_type)
        grounds = db.session.query(distinct(model.ground)).filter(
            model.player_name == player_name,
            model.wickets > 0  # Only grounds where player bowled
        ).all()
        
        grounds_list = sorted([g[0] for g in grounds if g[0]])
        return jsonify(grounds_list)
    except Exception as e:
        print(f"Error fetching bowling grounds for {match_type}: {e}")
        return jsonify({"error": "Database error occurred"}), 500

@bowling_bp.route('/api/bowling/player-ground-stats', methods=['GET'])
def get_bowling_stats():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    match_type = request.args.get('matchType', 'ODI').upper()
    
    if not player_name or not ground_name:
        return jsonify({'error': 'Parameters required'}), 400
    
    # Validate match type
    if match_type not in MATCH_TYPE_MODELS:
        return jsonify({"error": f"Match type must be one of: {', '.join(MATCH_TYPE_MODELS.keys())}"}), 400
    
    try:
        model = get_model_for_match_type(match_type)
        performances = db.session.query(model).filter(
            model.player_name == player_name,
            model.ground == ground_name,
            model.wickets > 0  # Only bowling records
        ).all()
        
        if not performances:
            return jsonify({'message': 'No bowling data found'}), 404
        
        total_matches = sum(p.matches for p in performances)
        total_wickets = sum(p.wickets for p in performances)
        avg_economy = sum(p.economy for p in performances) / len(performances) if performances else 0
        
        # Calculate runs conceded
        total_runs_conceded = sum(p.runs_conceded for p in performances if p.runs_conceded)
        
        # If not available, estimate from economy
        if total_runs_conceded == 0 and avg_economy > 0:
            # Average bowler bowls ~8-10 overs per match, use 9 as average
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
        print(f"Error fetching bowling stats for {match_type}: {e}")
        return jsonify({"error": "Database error occurred"}), 500
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