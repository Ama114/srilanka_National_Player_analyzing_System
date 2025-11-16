from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import joblib

app = Flask(__name__)
CORS(app)

# =================================================================
# APP එක START වෙද්දී අවශ්‍ය සියලුම DATA සහ MODELS LOAD කරගැනීම
# =================================================================

# --- Batting සහ Bowling Pages සඳහා අවශ්‍ය Data ---
try:
    df_batting = pd.read_csv('odi_batting_cleaned.csv', encoding='latin1')
    numeric_cols_bat = ['Runs', 'BF', '4s', '6s']
    for col in numeric_cols_bat:
        df_batting[col] = pd.to_numeric(df_batting[col], errors='coerce')
    df_batting.dropna(subset=numeric_cols_bat, inplace=True)
    print("Batting dataset ('odi_batting_cleaned.csv') loaded successfully.")
except FileNotFoundError:
    print("Warning: 'odi_batting_cleaned.csv' not found.")
    df_batting = pd.DataFrame()

try:
    df_bowling = pd.read_csv('odi_bowling_cleaned.csv', encoding='latin1')
    numeric_cols_bowl = ['Overs', 'Runs', 'Wkts']
    for col in numeric_cols_bowl:
        df_bowling[col] = pd.to_numeric(df_bowling[col], errors='coerce')
    df_bowling.dropna(subset=numeric_cols_bowl, inplace=True)
    print("Bowling dataset ('odi_bowling_cleaned.csv') loaded successfully.")
except FileNotFoundError:
    print("Warning: 'odi_bowling_cleaned.csv' not found.")
    df_bowling = pd.DataFrame()


# --- Best XI Page එක සඳහා අවශ්‍ය Data සහ Model ---
try:
    model = joblib.load("best_xi_model.joblib")
    print("ML model 'best_xi_model.joblib' loaded successfully.")
    
    # Read CSV normally - it has proper headers
    df_players_ml = pd.read_csv('srilanka player 11 dataset.csv')
    
    # Clean column names (remove any extra spaces or quotes)
    df_players_ml.columns = df_players_ml.columns.str.strip()
    
    # Debug: Print column names to help identify issues
    print(f"ML Dataset columns: {df_players_ml.columns.tolist()}")
    print(f"ML Dataset shape: {df_players_ml.shape}")
    print("Player dataset for ML ('srilanka player 11 dataset.csv') loaded successfully.")
    
except FileNotFoundError:
    print("Warning: ML model or its dataset not found. Best XI feature may not work.")
    model = None
    df_players_ml = pd.DataFrame()
except Exception as e:
    print(f"An error occurred loading ML components: {e}")
    model = None
    df_players_ml = pd.DataFrame()

# ===============================================================
# API ENDPOINTS
# ===============================================================

# --- Homepage Stats API (මේක තියෙනවා) ---
@app.route('/api/homepage-stats', methods=['GET'])
def get_homepage_stats():
    try:
        total_runs = int(df_batting['Runs'].sum())
        total_wickets = int(df_bowling['Wkts'].sum())
        
        # Top Batsman (by runs)
        top_batsman = df_batting.groupby('Player Name')['Runs'].sum().idxmax()
        top_batsman_runs = int(df_batting.groupby('Player Name')['Runs'].sum().max())

        # Top Bowler (by wickets)
        top_bowler = df_bowling.groupby('Player Name')['Wkts'].sum().idxmax()
        top_bowler_wickets = int(df_bowling.groupby('Player Name')['Wkts'].sum().max())

        return jsonify({
            'totalRuns': total_runs,
            'totalWickets': total_wickets,
            'topScorer': {'name': top_batsman, 'stat': f"{top_batsman_runs} Runs"},
            'topBowler': {'name': top_bowler, 'stat': f"{top_bowler_wickets} Wickets"}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- /api/player-search endpoint එක මෙතනින් ඉවත් කළා ---

# --- BEST XI PAGE එකට DROPDOWNS වලට DATA දෙන API ---
@app.route('/api/all-grounds', methods=['GET'])
def get_all_grounds():
    if not df_batting.empty:
        grounds = df_batting['Ground'].unique().tolist()
        return jsonify(sorted(grounds))
    return jsonify([])

@app.route('/api/ml/oppositions', methods=['GET'])
def get_ml_oppositions():
    try:
        if df_players_ml.empty:
            return jsonify([])
        
        # Try different possible column name variations
        col_name = None
        for possible_name in ['Opponent_Team', 'Opponent Team', 'OpponentTeam', 'opponent_team', 'opponent team']:
            if possible_name in df_players_ml.columns:
                col_name = possible_name
                break
        
        if col_name is None:
            # Print available columns for debugging
            print(f"Available columns: {df_players_ml.columns.tolist()}")
            return jsonify({"error": "Opponent_Team column not found"}), 500
        
        oppositions = df_players_ml[col_name].dropna().unique().tolist()
        return jsonify(sorted(oppositions))
    except Exception as e:
        print(f"Error in get_ml_oppositions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ml/weather-types', methods=['GET'])
def get_ml_weather_types():
    try:
        if df_players_ml.empty:
            return jsonify([])
        
        # Try different possible column name variations
        col_name = None
        for possible_name in ['Weather', 'weather', 'weather_type', 'Weather Type', 'WeatherType']:
            if possible_name in df_players_ml.columns:
                col_name = possible_name
                break
        
        if col_name is None:
            # Print available columns for debugging
            print(f"Available columns: {df_players_ml.columns.tolist()}")
            return jsonify({"error": "Weather column not found"}), 500
        
        weather = df_players_ml[col_name].dropna().unique().tolist()
        return jsonify(sorted(weather))
    except Exception as e:
        print(f"Error in get_ml_weather_types: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- BATTING API ENDPOINTS ---
@app.route('/api/players', methods=['GET'])
def get_players():
    if not df_batting.empty:
        players = df_batting['Player Name'].unique().tolist()
        return jsonify(sorted(players))
    return jsonify([])

@app.route('/api/grounds-for-player', methods=['GET'])
def get_grounds_for_player():
    player_name = request.args.get('player')
    if not player_name or df_batting.empty: return jsonify([])
    player_grounds = df_batting[df_batting['Player Name'] == player_name]['Ground'].unique().tolist()
    return jsonify(sorted(player_grounds))

@app.route('/api/player-ground-stats', methods=['GET'])
def get_player_stats():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    if not player_name or not ground_name or df_batting.empty: return jsonify({'error': 'Parameters required'}), 400
    filtered_df = df_batting[(df_batting['Player Name'] == player_name) & (df_batting['Ground'] == ground_name)]
    if filtered_df.empty: return jsonify({'message': 'No data found'})
    total_runs = int(filtered_df['Runs'].sum())
    out_innings = filtered_df[filtered_df['Dismissal'] != 'not out']
    average = (total_runs / len(out_innings)) if not out_innings.empty else float('inf')
    total_balls_faced = filtered_df['BF'].sum()
    strike_rate = (total_runs / total_balls_faced * 100) if total_balls_faced > 0 else 0
    stats = { "matches": len(filtered_df), "totalRuns": total_runs, "mostFrequentDismissal": filtered_df['Dismissal'].mode().iloc[0] if not filtered_df.empty else 'N/A', "bestOpposition": filtered_df.groupby('Opposition')['Runs'].sum().idxmax() if not filtered_df.empty else 'N/A', "total4s": int(filtered_df['4s'].sum()), "total6s": int(filtered_df['6s'].sum()), "average": round(average, 2) if average != float('inf') else 'Not Out', "strikeRate": round(strike_rate, 2), "recommendedPosition": int(filtered_df['Pos'].mode().iloc[0]) if not filtered_df.empty else 'N/A' }
    return jsonify(stats)

@app.route('/api/player-ground-chart-data', methods=['GET'])
def get_chart_data():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    if not player_name or not ground_name or df_batting.empty: return jsonify({'error': 'Parameters required'}), 400
    filtered_df = df_batting[(df_batting['Player Name'] == player_name) & (df_batting['Ground'] == ground_name)]
    if filtered_df.empty: return jsonify({'labels': [], 'data': []})
    runs_by_opposition = filtered_df.groupby('Opposition')['Runs'].sum().sort_values(ascending=False)
    chart_data = {'labels': runs_by_opposition.index.tolist(), 'data': runs_by_opposition.values.tolist()}
    return jsonify(chart_data)

# --- BOWLING API ENDPOINTS ---
@app.route('/api/bowling/players', methods=['GET'])
def get_bowling_players():
    if not df_bowling.empty:
        players = df_bowling['Player Name'].unique().tolist()
        return jsonify(sorted(players))
    return jsonify([])

@app.route('/api/bowling/grounds-for-player', methods=['GET'])
def get_bowling_grounds_for_player():
    player_name = request.args.get('player')
    if not player_name or df_bowling.empty: return jsonify([])
    player_grounds = df_bowling[df_bowling['Player Name'] == player_name]['Ground'].unique().tolist()
    return jsonify(sorted(player_grounds))

@app.route('/api/bowling/player-ground-stats', methods=['GET'])
def get_bowling_stats():
    player_name = request.args.get('player')
    ground_name = request.args.get('ground')
    if not player_name or not ground_name or df_bowling.empty: return jsonify({'error': 'Parameters required'}), 400
    filtered_df = df_bowling[(df_bowling['Player Name'] == player_name) & (df_bowling['Ground'] == ground_name)]
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
    stats = { "matches": matches, "wickets": total_wickets, "runsConceded": total_runs_conceded, "economy": round(economy, 2), "average": round(bowling_average, 2) if bowling_average != float('inf') else 'N/A', "bestOpposition": best_opposition, }
    return jsonify(stats)

# --- BEST XI SUGGESTION API ENDPOINT ---
@app.route('/api/suggest-best-xi', methods=['GET'])
def suggest_best_xi():
    opposition = request.args.get('opposition')
    pitch = request.args.get('pitch')
    weather = request.args.get('weather')

    if not all([opposition, pitch, weather, model, not df_players_ml.empty]):
        return jsonify({"error": "Missing parameters or model not loaded"}), 400

    unique_players = df_players_ml[['Player_Name', 'Player_Type']].drop_duplicates()
    predictions = []
    for index, player in unique_players.iterrows():
        input_data = pd.DataFrame({
            'Opponent_Team': [opposition], 'Pitch_Type': [pitch],
            'Weather': [weather], 'Player_Name': [player['Player_Name']],
            'Player_Type': [player['Player_Type']]
        })
        predicted_score = model.predict(input_data)[0]
        predictions.append({'name': player['Player_Name'], 'type': player['Player_Type'], 'score': predicted_score})

    predictions.sort(key=lambda x: x['score'], reverse=True)
    
    final_team_with_roles = []
    team_member_names = set()
    
    WICKET_KEEPERS = ['Kusal Mendis', 'Sadeera Samarawickrama']
    ALL_ROUNDERS = [
        'Wanindu Hasaranga', 'Dhananjaya de Silva', 'Dasun Shanaka', 
        'Dunith Wellalage', 'Chamika Karunaratne', 'Charith Asalanka', 'Janith Liyanage'
    ]

    keeper_candidates = [p for p in predictions if p['name'] in WICKET_KEEPERS]
    if keeper_candidates:
        best_keeper_obj = max(keeper_candidates, key=lambda x: x['score'])
        final_team_with_roles.append({'name': best_keeper_obj['name'], 'role': 'Wicket Keeper'})
        team_member_names.add(best_keeper_obj['name'])

    for player in predictions:
        if len(final_team_with_roles) >= 11:
            break
        if player['name'] not in team_member_names:
            role = ''
            if player['name'] in ALL_ROUNDERS:
                role = 'All-Rounder'
            else:
                role = player['type']
            
            final_team_with_roles.append({'name': player['name'], 'role': role})
            team_member_names.add(player['name'])
            
    return jsonify(final_team_with_roles)

if __name__ == '__main__':
    app.run(debug=True, port=5000)