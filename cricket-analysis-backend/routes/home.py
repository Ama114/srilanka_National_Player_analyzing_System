from flask import Blueprint, jsonify
import data_loader

home_bp = Blueprint('home', __name__)

@home_bp.route('/api/homepage-stats', methods=['GET'])
def get_homepage_stats():
    try:
        df_bat = data_loader.df_batting
        df_bowl = data_loader.df_bowling
        
        total_runs = int(df_bat['Runs'].sum()) if not df_bat.empty else 0
        total_wickets = int(df_bowl['Wkts'].sum()) if not df_bowl.empty else 0
        
        # Top Batsman
        top_batsman = "N/A"
        top_batsman_runs = 0
        if not df_bat.empty:
            top_batsman = df_bat.groupby('Player Name')['Runs'].sum().idxmax()
            top_batsman_runs = int(df_bat.groupby('Player Name')['Runs'].sum().max())

        # Top Bowler
        top_bowler = "N/A"
        top_bowler_wickets = 0
        if not df_bowl.empty:
            top_bowler = df_bowl.groupby('Player Name')['Wkts'].sum().idxmax()
            top_bowler_wickets = int(df_bowl.groupby('Player Name')['Wkts'].sum().max())

        return jsonify({
            'totalRuns': total_runs,
            'totalWickets': total_wickets,
            'topScorer': {'name': top_batsman, 'stat': f"{top_batsman_runs} Runs"},
            'topBowler': {'name': top_bowler, 'stat': f"{top_bowler_wickets} Wickets"}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500