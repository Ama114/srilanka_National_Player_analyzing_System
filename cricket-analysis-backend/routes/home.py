from flask import Blueprint, jsonify
import data_loader

home_bp = Blueprint('home', __name__)

def get_stats_for_match_type(match_type):
    """Get statistics for a specific match type"""
    try:
        df_bat = data_loader.get_dataset(match_type, 'batting')
        df_bowl = data_loader.get_dataset(match_type, 'bowling')
        
        # Get total runs
        total_runs = 0
        if not df_bat.empty:
            if 'runs' in df_bat.columns:
                total_runs = int(df_bat['runs'].sum())
            elif 'Runs' in df_bat.columns:
                total_runs = int(df_bat['Runs'].sum())
        
        # Get total wickets
        total_wickets = 0
        if not df_bowl.empty:
            if 'wickets' in df_bowl.columns:
                total_wickets = int(df_bowl['wickets'].sum())
            elif 'Wkts' in df_bowl.columns:
                total_wickets = int(df_bowl['Wkts'].sum())
        
        # Top Batsman
        top_batsman = "N/A"
        top_batsman_runs = 0
        if not df_bat.empty:
            player_col = 'player_name' if 'player_name' in df_bat.columns else ('Player Name' if 'Player Name' in df_bat.columns else None)
            runs_col = 'runs' if 'runs' in df_bat.columns else ('Runs' if 'Runs' in df_bat.columns else None)
            
            if player_col and runs_col:
                stats = df_bat.groupby(player_col)[runs_col].sum()
                top_batsman = stats.idxmax()
                top_batsman_runs = int(stats.max())
        
        # Top Bowler
        top_bowler = "N/A"
        top_bowler_wickets = 0
        if not df_bowl.empty:
            player_col = 'player_name' if 'player_name' in df_bowl.columns else ('Player Name' if 'Player Name' in df_bowl.columns else None)
            wickets_col = 'wickets' if 'wickets' in df_bowl.columns else ('Wkts' if 'Wkts' in df_bowl.columns else None)
            
            if player_col and wickets_col:
                stats = df_bowl.groupby(player_col)[wickets_col].sum()
                top_bowler = stats.idxmax()
                top_bowler_wickets = int(stats.max())
        
        return {
            'totalRuns': total_runs,
            'totalWickets': total_wickets,
            'topScorer': {'name': top_batsman, 'stat': f"{top_batsman_runs} Runs"},
            'topBowler': {'name': top_bowler, 'stat': f"{top_bowler_wickets} Wickets"}
        }
    except Exception as e:
        print(f"Error getting stats for {match_type}: {e}")
        return {
            'totalRuns': 0,
            'totalWickets': 0,
            'topScorer': {'name': 'N/A', 'stat': '0 Runs'},
            'topBowler': {'name': 'N/A', 'stat': '0 Wickets'}
        }

@home_bp.route('/api/homepage-stats', methods=['GET'])
def get_homepage_stats():
    """Get homepage stats for all match types"""
    try:
        stats_data = {
            'ODI': get_stats_for_match_type('ODI'),
            'T20': get_stats_for_match_type('T20'),
            'Test': get_stats_for_match_type('Test')
        }
        
        return jsonify(stats_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500