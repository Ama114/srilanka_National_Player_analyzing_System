from flask import Blueprint, jsonify, request
import data_loader

bowling_bp = Blueprint('bowling', __name__)

@bowling_bp.route('/api/bowling/players', methods=['GET'])
def get_bowling_players():
    if not data_loader.df_bowling.empty:
        players = data_loader.df_bowling['Player Name'].unique().tolist()
        return jsonify(sorted(players))
    return jsonify([])

@bowling_bp.route('/api/bowling/grounds-for-player', methods=['GET'])
def get_bowling_grounds_for_player():
    player_name = request.args.get('player')
    df = data_loader.df_bowling
    if not player_name or df.empty: return jsonify([])
    
    player_grounds = df[df['Player Name'] == player_name]['Ground'].unique().tolist()
    return jsonify(sorted(player_grounds))

@bowling_bp.route('/api/bowling/player-ground-stats', methods=['GET'])
def get_bowling_stats():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    df = data_loader.df_bowling
    
    if not player_name or not ground_name or df.empty: 
        return jsonify({'error': 'Parameters required'}), 400
        
    filtered_df = df[(df['Player Name'] == player_name) & (df['Ground'] == ground_name)]
    if filtered_df.empty: return jsonify({'message': 'No bowling data found'})
    
    matches = len(filtered_df)
    total_wickets = int(filtered_df['Wkts'].sum())
    total_runs_conceded = int(filtered_df['Runs'].sum())
    full_overs = filtered_df['Overs'].astype(int)
    partial_balls = (filtered_df['Overs'] * 10 % 10).astype(int)
    total_balls_bowled = (full_overs * 6 + partial_balls).sum()
    
    economy = (total_runs_conceded / (total_balls_bowled / 6)) if total_balls_bowled > 0 else 0
    bowling_average = (total_runs_conceded / total_wickets) if total_wickets > 0 else float('inf')
    
    wickets_by_opposition = filtered_df.groupby('Opposition')['Wkts'].sum()
    best_opposition = wickets_by_opposition.idxmax() if not wickets_by_opposition.empty and wickets_by_opposition.max() > 0 else 'N/A'
    
    stats = { 
        "matches": matches, 
        "wickets": total_wickets, 
        "runsConceded": total_runs_conceded, 
        "economy": round(economy, 2), 
        "average": round(bowling_average, 2) if bowling_average != float('inf') else 'N/A', 
        "bestOpposition": best_opposition
    }
    return jsonify(stats)