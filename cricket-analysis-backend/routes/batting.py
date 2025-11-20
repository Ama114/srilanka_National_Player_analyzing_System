from flask import Blueprint, jsonify, request
import data_loader
import pandas as pd

batting_bp = Blueprint('batting', __name__)

@batting_bp.route('/api/players', methods=['GET'])
def get_players():
    if not data_loader.df_batting.empty:
        players = data_loader.df_batting['Player Name'].unique().tolist()
        return jsonify(sorted(players))
    return jsonify([])

@batting_bp.route('/api/grounds-for-player', methods=['GET'])
def get_grounds_for_player():
    player_name = request.args.get('player')
    df = data_loader.df_batting
    if not player_name or df.empty: return jsonify([])
    
    player_grounds = df[df['Player Name'] == player_name]['Ground'].unique().tolist()
    return jsonify(sorted(player_grounds))

@batting_bp.route('/api/player-ground-stats', methods=['GET'])
def get_player_stats():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    df = data_loader.df_batting
    
    if not player_name or not ground_name or df.empty: 
        return jsonify({'error': 'Parameters required'}), 400
        
    filtered_df = df[(df['Player Name'] == player_name) & (df['Ground'] == ground_name)]
    if filtered_df.empty: return jsonify({'message': 'No data found'})
    
    total_runs = int(filtered_df['Runs'].sum())
    out_innings = filtered_df[filtered_df['Dismissal'] != 'not out']
    average = (total_runs / len(out_innings)) if not out_innings.empty else float('inf')
    total_balls_faced = filtered_df['BF'].sum()
    strike_rate = (total_runs / total_balls_faced * 100) if total_balls_faced > 0 else 0
    
    stats = { 
        "matches": len(filtered_df), 
        "totalRuns": total_runs, 
        "mostFrequentDismissal": filtered_df['Dismissal'].mode().iloc[0] if not filtered_df.empty else 'N/A', 
        "bestOpposition": filtered_df.groupby('Opposition')['Runs'].sum().idxmax() if not filtered_df.empty else 'N/A', 
        "total4s": int(filtered_df['4s'].sum()), 
        "total6s": int(filtered_df['6s'].sum()), 
        "average": round(average, 2) if average != float('inf') else 'Not Out', 
        "strikeRate": round(strike_rate, 2), 
        "recommendedPosition": int(filtered_df['Pos'].mode().iloc[0]) if not filtered_df.empty else 'N/A' 
    }
    return jsonify(stats)

@batting_bp.route('/api/player-ground-chart-data', methods=['GET'])
def get_chart_data():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    df = data_loader.df_batting
    
    if not player_name or not ground_name or df.empty: 
        return jsonify({'error': 'Parameters required'}), 400
        
    filtered_df = df[(df['Player Name'] == player_name) & (df['Ground'] == ground_name)]
    if filtered_df.empty: return jsonify({'labels': [], 'data': []})
    
    runs_by_opposition = filtered_df.groupby('Opposition')['Runs'].sum().sort_values(ascending=False)
    chart_data = {'labels': runs_by_opposition.index.tolist(), 'data': runs_by_opposition.values.tolist()}
    return jsonify(chart_data)