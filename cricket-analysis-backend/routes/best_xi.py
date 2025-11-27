from flask import Blueprint, jsonify, request
import pandas as pd
import joblib
import xgboost as xgb
import os
import traceback
import numpy as np

best_xi_bp = Blueprint('best_xi', __name__)

# --- CONFIGURATION ---
ODI_MODEL_PATH = 'multi_target_odi_model.joblib'
T20_MODEL_PATH = 't20_model.json'
DATA_PATH = 'odi_performance.csv'

odi_model = None
t20_model = None

# --- MODEL LOADING ---
# 1. Load ODI Model
try:
    if os.path.exists(ODI_MODEL_PATH):
        odi_model = joblib.load(ODI_MODEL_PATH)
        print("✅ ODI Model Loaded Successfully!")
    else:
        print(f"⚠️ Warning: ODI Model '{ODI_MODEL_PATH}' not found.")
except Exception as e:
    print(f"❌ Error loading ODI model: {e}")

# 2. Load T20 Model
try:
    if os.path.exists(T20_MODEL_PATH):
        t20_model = xgb.Booster()
        t20_model.load_model(T20_MODEL_PATH)
        print("✅ T20 Model Loaded Successfully!")
    else:
        print(f"⚠️ Warning: T20 Model '{T20_MODEL_PATH}' not found.")
except Exception as e:
    print(f"❌ Error loading T20 model: {e}")

# --- HELPER FUNCTIONS ---

def get_player_data(match_format):
    """Loads and cleans data based on format"""
    if not os.path.exists(DATA_PATH):
        print(f"⚠️ Data file not found: {DATA_PATH}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(DATA_PATH)
        
        # Rename columns
        df = df.rename(columns={
            'player_name': 'Player_Name', 'batting_runs': 'Runs', 'sr': 'SR',
            'wicket_taken': 'Wickets', 'econ': 'Econ', 'fours': 'Fours',
            'sixes': 'Sixes', 'main_role': 'main_role', 'bowling_style': 'Bowling_Style',
            'match_type': 'Match_Type'
        })

        # Filter
        if 'Match_Type' in df.columns:
            df = df[df['Match_Type'].str.lower() == match_format.lower()]
        
        if df.empty: return pd.DataFrame()

        # Numeric conversion
        numeric_cols = ['Runs', 'SR', 'Wickets', 'Econ', 'Fours', 'Sixes']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)
        
        # Aggregate
        df_agg = df.groupby('Player_Name').agg({
            'main_role': 'first', 'Bowling_Style': 'first',
            'Runs': 'mean', 'SR': 'mean', 'Wickets': 'mean',
            'Econ': 'mean', 'Fours': 'mean', 'Sixes': 'mean'
        }).reset_index()

        # Rename for Model Features
        df_agg.rename(columns={
            'Runs': 'Avg_Batting_Runs', 'SR': 'Avg_SR',
            'Wickets': 'Avg_Wicket_taken', 'Econ': 'Avg_Econ',
            'Fours': 'Avg_Fours', 'Sixes': 'Avg_Sixes'
        }, inplace=True)

        return df_agg
    except Exception as e:
        print(f"Data Load Error: {e}")
        return pd.DataFrame()

def select_team_logic(df_predict, pitch_type, match_format):
    """Applies selection rules for both formats"""
    # Sort by score
    df_select = df_predict.sort_values(by='Predicted_Score', ascending=False)
    
    # Normalize Roles
    df_select['Role'] = df_select['main_role'].replace({
        'bat': 'Batsman', 'bowler': 'Bowler', 
        'batting alrounder': 'Allrounder', 'bowling alrounder': 'Allrounder', 
        'keeper': 'Wicket Keeper', 'wk batsman': 'Wicket Keeper', 'all_rounder': 'Allrounder',
        'spin bowler': 'Bowler', 'pace bowler': 'Bowler'
    })
    
    df_select['is_spinner'] = df_select['Bowling_Style'].str.contains('spin|off|leg', case=False)
    df_select['is_pacer'] = df_select['Bowling_Style'].str.contains('fast|medium|pace', case=False)

    # Define Rules based on Pitch & Format
    pitch_type_new = str(pitch_type).lower()
    
    if match_format == 'T20':
        # T20 Logic - More Allrounders
        if "batting" in pitch_type_new: 
            comp = {'wk':1, 'bat':3, 'ar':4, 'spin':1, 'pace':2}
        elif "spin" in pitch_type_new: 
            comp = {'wk':1, 'bat':3, 'ar':3, 'spin':2, 'pace':2}
        else: 
            comp = {'wk':1, 'bat':4, 'ar':3, 'spin':1, 'pace':2}
            
    else:
        # ODI Logic - UPDATED WITH YOUR RULES
        if pitch_type_new == "batting": 
            comp = {'wk':1, 'bat':4, 'ar':3, 'spin':1, 'pace':2}
        elif pitch_type_new == "pace=bowling friendly": 
            comp = {'wk':1, 'bat':3, 'ar':2, 'spin':1, 'pace':3}
        elif pitch_type_new == "spin": 
            comp = {'wk':1, 'bat':3, 'ar':2, 'spin':3, 'pace':2}
        elif pitch_type_new == "balanced": 
            comp = {'wk':1, 'bat':4, 'ar':3, 'spin':1, 'pace':2}
        else: 
            comp = {'wk':1, 'bat':4, 'ar':3, 'spin':1, 'pace':2}

    # Selection Loop
    result = []
    temp_df = df_select.copy()
    execution_order = ['wk', 'bat', 'ar', 'spin', 'pace']

    for role_type in execution_order:
        candidates = pd.DataFrame()
        count = comp.get(role_type, 2)

        if role_type == 'wk': candidates = temp_df[temp_df['Role'].str.contains('keeper', case=False)]
        elif role_type == 'bat': candidates = temp_df[temp_df['Role'].str.contains('batsman', case=False)]
        elif role_type == 'ar': candidates = temp_df[temp_df['Role'].str.contains('allrounder', case=False)]
        elif role_type == 'spin': candidates = temp_df[temp_df['is_spinner']]
        elif role_type == 'pace': candidates = temp_df[temp_df['is_pacer']]
        
        candidates = candidates.sort_values(by='Predicted_Score', ascending=False)

        if not candidates.empty:
            selected = candidates.head(count)
            result.extend(selected.to_dict('records'))
            temp_df = temp_df.drop(selected.index)

    # Fill remaining to reach 11
    unique_result = []
    seen = set()
    for d in result:
        if d['Player_Name'] not in seen:
            unique_result.append(d)
            seen.add(d['Player_Name'])
            
    if len(unique_result) < 11:
        req = 11 - len(unique_result)
        existing = [p['Player_Name'] for p in unique_result]
        pool = temp_df[~temp_df['Player_Name'].isin(existing)]
        padding = pool.sort_values(by='Predicted_Score', ascending=False).head(req)
        unique_result.extend(padding.to_dict('records'))

    return unique_result[:11]

# --- MAIN API ENDPOINT ---

@best_xi_bp.route('/api/predict-team', methods=['POST'])
def predict_team():
    try:
        data = request.json
        print(f"🔮 Request: {data}")

        match_type = data.get('match_type', 'ODI')
        pitch_type = data.get('pitch_type', 'balanced')
        weather = data.get('weather', 'clear')
        opposition = data.get('opposition', 'India')

        # 1. Load Data
        df_data = get_player_data(match_type)
        if df_data.empty:
            return jsonify({"status": "error", "message": f"No data for {match_type}"}), 404

        # 2. Prepare Inputs
        df_data['Pitch_Type'] = str(pitch_type)
        df_data['weather'] = str(weather)
        df_data['Opposition'] = str(opposition)
        df_data['main_role'] = df_data['main_role'].fillna('Unknown').astype(str)
        df_data['Bowling_Style'] = df_data['Bowling_Style'].fillna('None').astype(str)

        # 3. Run Prediction based on Format
        if match_type == 'ODI':
            if odi_model is None: return jsonify({"status":"error", "message":"ODI Model Missing"}), 500
            
            features = ['main_role', 'Pitch_Type', 'weather', 'Opposition', 'Bowling_Style',
                        'Avg_Batting_Runs', 'Avg_Wicket_taken', 'Avg_SR', 'Avg_Econ', 'Avg_Fours', 'Avg_Sixes']
            preds = odi_model.predict(df_data[features])
            df_data['Predicted_Score'] = preds[:, 0] + preds[:, 1]

        elif match_type == 'T20':
            if t20_model is None: return jsonify({"status":"error", "message":"T20 Model Missing"}), 500
            
            num_features = ['Avg_Batting_Runs', 'Avg_Wicket_taken', 'Avg_SR', 'Avg_Econ', 'Avg_Fours', 'Avg_Sixes']
            dtest = xgb.DMatrix(df_data[num_features])
            preds = t20_model.predict(dtest)
            df_data['Predicted_Score'] = preds

        else:
            return jsonify({"status":"error", "message":"Invalid Format"}), 400

        # 4. Select Team
        final_team = select_team_logic(df_data, pitch_type, match_type)

        # 5. Response
        response_team = []
        for p in final_team:
            response_team.append({
                "player_name": p['Player_Name'],
                "role": p.get('Role', 'Unknown'),
                "predicted_score": round(float(p.get('Predicted_Score', 0)), 2)
            })

        return jsonify({
            "status": "success",
            "match_details": { "format": match_type },
            "team": response_team
        })

    except Exception as e:
        print(f"Server Error: {e}")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- DROPDOWNS ---
@best_xi_bp.route('/api/ml/match-types', methods=['GET'])
def get_match_types(): return jsonify(["ODI", "T20"])

@best_xi_bp.route('/api/ml/oppositions', methods=['GET'])
def get_ml_oppositions(): return jsonify(["India", "Australia", "England", "New Zealand", "Pakistan", "South Africa", "Bangladesh", "West Indies", "Afghanistan"])

@best_xi_bp.route('/api/ml/pitch-types', methods=['GET'])
def get_ml_pitch_types(): return jsonify(["Batting Friendly", "Bowling Friendly", "Spin Friendly", "Balanced"])

@best_xi_bp.route('/api/ml/weather-conditions', methods=['GET'])
def get_ml_weather_conditions(): return jsonify(["dry", "hot", "cloudy", "humid"])