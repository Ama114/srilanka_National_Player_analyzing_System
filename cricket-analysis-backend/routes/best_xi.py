from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
import os
from models import db, ODIPerformance, T20Performance, TestPerformance

best_xi_bp = Blueprint('best_xi', __name__)

# --- 1. ML MODELS LOADING ---
ODI_MODEL_PATH = 'multi_target_odi_model.joblib'
T20_MODEL_PATH = 't20_model.json'

odi_model = None
t20_model = None

try:
    if os.path.exists(ODI_MODEL_PATH):
        odi_model = joblib.load(ODI_MODEL_PATH)
        print("✅ ODI AI Model Loaded!")
    else:
        print(f"⚠️ Warning: ODI Model '{ODI_MODEL_PATH}' not found.")
except Exception as e:
    print(f"❌ ODI Model Error: {e}")

try:
    if os.path.exists(T20_MODEL_PATH):
        t20_model = xgb.Booster()
        t20_model.load_model(T20_MODEL_PATH)
        print("✅ T20 AI Model Loaded!")
    else:
        print(f"⚠️ Warning: T20 Model '{T20_MODEL_PATH}' not found.")
except Exception as e:
    print(f"❌ T20 Model Error: {e}")


# --- 2. DATA FETCHING (THE FIX) ---
def get_player_data_from_db(match_format):
    """
    FIXED: Uses pure SQLAlchemy to fetch data, avoiding pd.read_sql errors.
    """
    match_format = match_format.upper()
    
    # 1. Select the correct Model
    if match_format == 'ODI':
        model = ODIPerformance
    elif match_format == 'T20':
        model = T20Performance
    elif match_format == 'TEST':
        model = TestPerformance
    else:
        return pd.DataFrame()

    try:
        # 2. Fetch all records using SQLAlchemy (Safer than read_sql)
        records = model.query.all()
        
        if not records:
            return pd.DataFrame()

        # 3. Convert SQLAlchemy Objects to List of Dictionaries
        # This manually grabs all columns from the database row
        data_list = []
        for r in records:
            row_dict = {col.name: getattr(r, col.name) for col in r.__table__.columns}
            data_list.append(row_dict)

        # 4. Create Pandas DataFrame
        df = pd.DataFrame(data_list)

    except Exception as e:
        print(f"DB Fetch Error: {e}")
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    # 5. Handle 'odi' vs 'ODI' inside the DataFrame (just in case)
    if 'match_type' in df.columns:
        df['match_type'] = df['match_type'].str.upper()

    # 6. Column Standardization
    rename_map = {
        'player_name': 'Player_Name',
        'main_role': 'Role',
        'bowling_style': 'Bowling_Style',
        'batting_runs': 'Runs',       # ODI Name
        'runs': 'Runs',               # T20/Test Name
        'wicket_taken': 'Wickets',    # ODI Name
        'wickets': 'Wickets',         # T20/Test Name
        'sr': 'SR',                   # ODI Name
        'strike_rate': 'SR',          # T20/Test Name
        'econ': 'Econ',               # ODI Name
        'economy': 'Econ',            # T20/Test Name
        'fours': 'Fours',
        'sixes': 'Sixes'
    }
    df = df.rename(columns=rename_map)

    # 7. Convert to Numeric
    numeric_cols = ['Runs', 'SR', 'Wickets', 'Econ', 'Fours', 'Sixes']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0 

    # 8. Aggregation (Average Stats per Player)
    df_agg = df.groupby('Player_Name').agg({
        'Role': 'first',             
        'Bowling_Style': 'first',    
        'Runs': 'mean',              
        'SR': 'mean',
        'Wickets': 'mean',           
        'Econ': 'mean',
        'Fours': 'mean',
        'Sixes': 'mean'
    }).reset_index()

    # Rename for ML Models
    df_agg = df_agg.rename(columns={
        'Runs': 'Avg_Batting_Runs',
        'SR': 'Avg_SR',
        'Wickets': 'Avg_Wicket_taken',
        'Econ': 'Avg_Econ',
        'Fours': 'Avg_Fours',
        'Sixes': 'Avg_Sixes'
    })

    return df_agg

# --- 3. TEAM SELECTION LOGIC ---
def select_best_11(df, pitch_type, match_format):
    df = df.sort_values(by='Predicted_Score', ascending=False)
    
    # Normalize Roles
    df['Role'] = df['Role'].astype(str).str.lower()
    df['Role'] = df['Role'].replace({
        'bat': 'Batsman', 'batsman': 'Batsman', 'rhb': 'Batsman', 'lhb': 'Batsman',
        'bowler': 'Bowler', 'pace bowler': 'Bowler', 'spin bowler': 'Bowler',
        'allrounder': 'Allrounder', 'batting alrounder': 'Allrounder', 'bowling alrounder': 'Allrounder',
        'wicket keeper': 'Wicket Keeper', 'keeper': 'Wicket Keeper', 'wk batsman': 'Wicket Keeper'
    })

    pitch_lower = pitch_type.lower()
    
    # Default Composition
    composition = {'Wicket Keeper': 1, 'Batsman': 4, 'Allrounder': 2, 'Bowler': 4}

    # Format Specific Rules
    if match_format == 'T20':
        if 'batting' in pitch_lower:
            composition = {'Wicket Keeper': 1, 'Batsman': 4, 'Allrounder': 3, 'Bowler': 3}
        elif 'spin' in pitch_lower:
            composition = {'Wicket Keeper': 1, 'Batsman': 3, 'Allrounder': 4, 'Bowler': 3}
            
    elif match_format == 'TEST':
        if 'bowling' in pitch_lower or 'green' in pitch_lower:
            composition = {'Wicket Keeper': 1, 'Batsman': 4, 'Allrounder': 1, 'Bowler': 5}
        else:
            composition = {'Wicket Keeper': 1, 'Batsman': 5, 'Allrounder': 1, 'Bowler': 4}

    # Selection Loop
    final_team = []
    for role, count in composition.items():
        candidates = df[df['Role'] == role].head(count)
        final_team.extend(candidates.to_dict('records'))
        df = df.drop(candidates.index)

    # Fill remaining spots if needed
    if len(final_team) < 11:
        needed = 11 - len(final_team)
        extras = df.head(needed)
        final_team.extend(extras.to_dict('records'))

    return final_team[:11]

# --- 4. PREDICTION ENDPOINT (Strict Type Handling for Model) ---
@best_xi_bp.route('/api/predict-team', methods=['POST'])
def predict_team():
    try:
        data = request.json
        match_type = data.get('match_type', 'ODI').upper()
        pitch_type = data.get('pitch_type', 'Balanced')
        weather = data.get('weather', 'Clear')      # Frontend එකෙන් එන Weather
        opposition = data.get('opposition', 'India') # Frontend එකෙන් එන Opposition
        
        # 1. Get Data from DB
        df_data = get_player_data_from_db(match_type)
        
        if df_data.empty:
            return jsonify({"status": "error", "message": f"No player data found for {match_type} in Database."}), 404

        # 2. Assign Frontend Inputs to DataFrame (හැම ප්ලේයර්ටම අදාළයි)
        # මෙතන අපි දත්ත පුරවන්නේ හරියටම Model එක ඉල්ලන විදියට (Strings නම් Strings)
        df_data['Pitch_Type'] = str(pitch_type)
        df_data['weather'] = str(weather)
        df_data['Opposition'] = str(opposition)
        
        # Role සහ Bowling Style දැනටමත් DB එකෙන් එනවා, ඒත් හිස් නම් 'Unknown' දාමු
        if 'Role' in df_data.columns:
             df_data['main_role'] = df_data['Role'] # Model එකේ නම 'main_role' නම්
        else:
             df_data['main_role'] = 'Unknown'

        if 'Bowling_Style' not in df_data.columns:
            df_data['Bowling_Style'] = 'None'

        # --- 🔥 THE REAL FIX: Data Type Cleaning 🔥 ---
        
        # A. CATEGORICAL COLUMNS (වචන) -> String වලට හරවන්න ඕනේ (0 දාන්න බෑ)
        cat_features = ['main_role', 'Pitch_Type', 'weather', 'Opposition', 'Bowling_Style']
        
        for col in cat_features:
            # Column එක නැත්නම් හදනවා
            if col not in df_data.columns:
                df_data[col] = 'Unknown'
            
            # Nan/Null තිබුණොත් 'Unknown' දාලා String බවට හරවනවා
            df_data[col] = df_data[col].fillna('Unknown').astype(str)

        # B. NUMERICAL COLUMNS (ඉලක්කම්) -> Float/Int වලට හරවන්න ඕනේ
        num_features = ['Avg_Batting_Runs', 'Avg_Wicket_taken', 'Avg_SR', 'Avg_Econ', 'Avg_Fours', 'Avg_Sixes']
        
        for col in num_features:
            if col not in df_data.columns:
                df_data[col] = 0.0
            
            # වචන තිබුණොත් අයින් කරලා ඉලක්කම් බවට හරවනවා
            df_data[col] = pd.to_numeric(df_data[col], errors='coerce').fillna(0.0)

        # 3. PREDICTION WITH MODEL
        if match_type == 'ODI' and odi_model:
            # Model එකට යවන Column ලිස්ට් එක (හරියටම Train කරපු පිළිවෙලට)
            model_cols = cat_features + num_features
            
            try:
                # දත්ත ටික හරියටම සකස් වුණා, දැන් Predict කරනවා
                preds = odi_model.predict(df_data[model_cols])
                
                # Result Handling
                if preds.ndim > 1:
                    df_data['Predicted_Score'] = preds[:, 0] + preds[:, 1]
                else:
                    df_data['Predicted_Score'] = preds
                
                print("✅ ODI Model Prediction Successful")

            except Exception as model_error:
                print(f"❌ Model Error Details: {model_error}")
                raise model_error # ඇත්ත Error එක පෙන්නන්න

        elif match_type == 'T20' and t20_model:
            # T20 Model එකට ඕනේ Numbers විතරයි
            dtest = xgb.DMatrix(df_data[num_features])
            preds = t20_model.predict(dtest)
            df_data['Predicted_Score'] = preds

        else:
            # Test Match හෝ Model නැති විට
            print(f"ℹ️ Using Calculation Logic for {match_type}")
            wkt_points = 25 if match_type == 'TEST' else 20
            df_data['Predicted_Score'] = (
                (df_data['Avg_Batting_Runs'] * 1.0) + 
                (df_data['Avg_Wicket_taken'] * wkt_points) + 
                (df_data['Avg_Fours'] * 1) + 
                (df_data['Avg_Sixes'] * 2)
            )

        # 4. Select Best XI
        final_team = select_best_11(df_data, pitch_type, match_type)

        response = []
        for p in final_team:
            response.append({
                "player_name": p['Player_Name'],
                "role": p['Role'],
                "predicted_score": round(float(p.get('Predicted_Score', 0)), 2)
            })

        return jsonify({
            "status": "success",
            "match_details": {"format": match_type, "pitch": pitch_type},
            "team": response
        })

    except Exception as e:
        import traceback
        traceback.print_exc() # Error එක Terminal එකේ පෙන්නන්න
        return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500
    

# --- 5. DROPDOWNS ---
@best_xi_bp.route('/api/ml/match-types', methods=['GET'])
def get_match_types(): return jsonify(["ODI", "T20", "TEST"])

@best_xi_bp.route('/api/ml/pitch-types', methods=['GET'])
def get_pitch_types(): return jsonify(["Batting Friendly", "Bowling Friendly", "Spin Friendly", "Balanced", "Green", "Dusty"])

@best_xi_bp.route('/api/ml/weather-conditions', methods=['GET'])
def get_ml_weather_conditions(): return jsonify(["Clear", "Sunny", "Cloudy", "Overcast", "Rainy", "Humid", "Dry"])

@best_xi_bp.route('/api/ml/oppositions', methods=['GET'])
def get_ml_oppositions(): return jsonify(["India", "Australia", "England", "New Zealand", "Pakistan", "South Africa", "Bangladesh", "West Indies", "Afghanistan"])