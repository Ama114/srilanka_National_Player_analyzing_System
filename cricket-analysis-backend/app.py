from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import joblib

app = Flask(__name__)
CORS(app)

# (DATA සහ MODELS LOAD කරන කොටසේ වෙනසක් නෑ...)
try:
    df_batting = pd.read_csv('odi_batting_cleaned.csv')
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
try:
    model = joblib.load("best_xi_model.joblib")
    print("ML model 'best_xi_model.joblib' loaded successfully.")
    df_raw = pd.read_csv('srilanka player 11 dataset.csv', header=None)
    df_players_ml = df_raw[0].str.split(',', expand=True)
    df_players_ml.columns = df_players_ml.iloc[0]
    df_players_ml = df_players_ml[1:]
    df_players_ml.columns = df_players_ml.columns.str.replace('"', '').str.strip()
    print("Player dataset for ML ('srilanka player 11 dataset.csv') loaded successfully.")
except FileNotFoundError:
    print("Warning: ML model or its dataset not found. Best XI feature may not work.")
    model = None
    df_players_ml = pd.DataFrame()
except Exception as e:
    print(f"An error occurred loading ML components: {e}")
    model = None
    df_players_ml = pd.DataFrame()

# BEST XI SUGGESTION API ENDPOINT (නිවැරදි කරන ලද කොටස)
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
    
    # --- මෙතන තමයි වැදගත්ම වෙනස කළේ ---
    WICKET_KEEPERS = ['Kusal Mendis', 'Sadeera Samarawickrama']
    ALL_ROUNDERS = [
        'Wanindu Hasaranga', 
        'Dhananjaya de Silva', 
        'Dasun Shanaka', 
        'Dunith Wellalage', 
        'Chamika Karunaratne',
        'Charith Asalanka',
        'Janith Liyanage'
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

# (පැරණි Batting, Bowling, සහ dropdowns වලට අදාළ සියලුම API ටික මෙතනින් යටට තියෙනවා)
@app.route('/api/all-grounds', methods=['GET'])
def get_all_grounds():
    if not df_batting.empty:
        grounds = df_batting['Ground'].unique().tolist()
        return jsonify(sorted(grounds))
    return jsonify([])
@app.route('/api/ml/oppositions', methods=['GET'])
def get_ml_oppositions():
    if not df_players_ml.empty:
        oppositions = df_players_ml['Opponent_Team'].unique().tolist()
        return jsonify(sorted(oppositions))
    return jsonify([])
@app.route('/api/ml/weather-types', methods=['GET'])
def get_ml_weather_types():
    if not df_players_ml.empty:
        weather = df_players_ml['Weather'].unique().tolist()
        return jsonify(sorted(weather))
    return jsonify([])
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)