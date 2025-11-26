import pandas as pd
import joblib
import os

# Global Variables - Organized by Match Type
datasets = {
    'ODI': {'batting': pd.DataFrame(), 'bowling': pd.DataFrame()},
    'T20': {'batting': pd.DataFrame(), 'bowling': pd.DataFrame()},
    'Test': {'batting': pd.DataFrame(), 'bowling': pd.DataFrame()}
}

df_players_ml = pd.DataFrame()
model = None
model_info = None  # Will contain encoders and feature info
default_weather = 'Balanced'

WICKET_KEEPER_NAMES = {
    'Kusal Mendis', 'Sadeera Samarawickrama'
}

ALL_ROUNDER_NAMES = {
    'Wanindu Hasaranga', 'Dhananjaya de Silva', 'Dasun Shanaka',
    'Dunith Wellalage', 'Chamika Karunaratne', 'Charith Asalanka', 'Janith Liyanage'
}

# Backward compatibility aliases
df_batting = None  # Will be set to ODI data
df_bowling = None  # Will be set to ODI data

def load_data_by_match_type():
    """Load data for all match types from database"""
    global datasets, df_batting, df_bowling
    
    try:
        from models import ODIPerformance, T20Performance, TestPerformance
        from app import db
        
        # Map match types to database models
        model_map = {
            'ODI': ODIPerformance,
            'T20': T20Performance,
            'Test': TestPerformance
        }
        
        for match_type, model_class in model_map.items():
            try:
                # Query all records for this match type
                records = db.session.query(model_class).all()
                
                if records:
                    # Convert to dataframe
                    data = [record.to_dict() for record in records]
                    
                    # Separate batting and bowling
                    batting_data = [d for d in data if d.get('runs', 0) > 0]
                    bowling_data = [d for d in data if d.get('wickets', 0) > 0]
                    
                    datasets[match_type]['batting'] = pd.DataFrame(batting_data) if batting_data else pd.DataFrame()
                    datasets[match_type]['bowling'] = pd.DataFrame(bowling_data) if bowling_data else pd.DataFrame()
                    
                    print(f"✓ Loaded {match_type}: {len(batting_data)} batting, {len(bowling_data)} bowling records")
                else:
                    print(f"⚠ No {match_type} data in database")
                    
            except Exception as e:
                print(f"⚠ Error loading {match_type} from database: {e}")
        
        # Set backward compatibility variables (default to ODI)
        df_batting = datasets['ODI']['batting']
        df_bowling = datasets['ODI']['bowling']
        
    except Exception as e:
        print(f"Error in load_data_by_match_type: {e}")
        # Fallback: try loading from CSV
        load_data_from_csv()

def load_data_from_csv():
    """Fallback: Load data from CSV files if database unavailable"""
    global datasets, df_batting, df_bowling
    
    csv_files = {
        'data/ODI/odi_performance.csv': 'ODI',
        'data/T20/t20_performance.csv': 'T20',
        'data/Test/test_performance.csv': 'Test'
    }
    
    for filename, match_type in csv_files.items():
        try:
            df = pd.read_csv(filename, encoding='latin1')
            df.columns = df.columns.str.strip().str.replace('"', '')
            
            # Separate batting and bowling
            batting = df[df.get('runs', 0) > 0] if 'runs' in df.columns else df
            bowling = df[df.get('wickets', 0) > 0] if 'wickets' in df.columns else pd.DataFrame()
            
            datasets[match_type]['batting'] = batting
            datasets[match_type]['bowling'] = bowling
            
            print(f"✓ Loaded {match_type} from CSV ({filename})")
        except FileNotFoundError:
            print(f"⚠ CSV file not found: {filename}")
        except Exception as e:
            print(f"⚠ Error loading {match_type} from CSV: {e}")
    
    # Set backward compatibility
    df_batting = datasets['ODI']['batting']
    df_bowling = datasets['ODI']['bowling']

# Try loading from database first, fallback to CSV
try:
    # Will attempt database load in initialization
    print("Data loading: Initializing from database...")
except:
    print("Data loading: Attempting CSV fallback...")

# --- ML Loading Functions ---
def load_ml_dataset():
    global df_players_ml, default_weather
    try:
        # Try multiple file names in data folder
        possible_files = [
            'data/best_11_odi_new.csv',
            'data/ODI/best_11_odi_new.csv',
            'data/ODI/odi_performance.csv',
            'best_11_odi_new.csv',
            'odi_performance.csv',
            'srilanka player 11 dataset.csv'
        ]
        df_temp = None
        loaded_file = None
        
        for filename in possible_files:
            try:
                df_temp = pd.read_csv(filename, encoding='latin1')
                loaded_file = filename
                print(f"✓ Successfully loaded ML dataset from: {filename}")
                break
            except FileNotFoundError:
                continue
        
        if df_temp is None:
            print("✗ No ML dataset file found. Checked:", possible_files)
            raise FileNotFoundError("No dataset file found")
        
        df_players_ml = df_temp
        df_players_ml.columns = df_players_ml.columns.str.strip().str.replace('"', '')
        
        # Map column names to match expected format (case-insensitive)
        columns_lower = {col.lower(): col for col in df_players_ml.columns}
        column_mapping_ml = {}
        
        if 'opposition' in columns_lower:
            column_mapping_ml[columns_lower['opposition']] = 'Opponent_Team'
        if 'weather' in columns_lower:
            column_mapping_ml[columns_lower['weather']] = 'Weather'
        if 'main_role' in columns_lower:
            column_mapping_ml[columns_lower['main_role']] = 'Role'
        
        if column_mapping_ml:
            df_players_ml = df_players_ml.rename(columns=column_mapping_ml)
        
        # Ensure required columns exist
        if 'Player_Name' not in df_players_ml.columns and 'Player Name' in df_players_ml.columns:
            df_players_ml['Player_Name'] = df_players_ml['Player Name']
        if 'Player_Name' not in df_players_ml.columns:
            # Use first suitable column as player names
            for col in df_players_ml.columns:
                if any(keyword in col.lower() for keyword in ['player', 'name']):
                    df_players_ml['Player_Name'] = df_players_ml[col]
                    break
            if 'Player_Name' not in df_players_ml.columns:
                df_players_ml['Player_Name'] = df_players_ml.iloc[:, 0]
        
        # Derive Player_Type from Role if not present
        def derive_player_type(row):
            role = str(row.get('Role', '')).lower()
            
            if 'keeper' in role or 'wicket' in role:
                return 'Wicket Keeper'
            elif 'allrounder' in role or 'alrounder' in role or ('batting' in role and 'bowling' in role):
                return 'All-Rounder'
            elif 'bowler' in role or 'bowling' in role:
                return 'Bowler'
            else:
                return 'Batsman'
        
        if 'Player_Type' not in df_players_ml.columns:
            df_players_ml['Player_Type'] = df_players_ml.apply(derive_player_type, axis=1)
        
        # Set default weather
        if 'Weather' in df_players_ml.columns and not df_players_ml['Weather'].dropna().empty:
            default_weather = df_players_ml['Weather'].mode().iloc[0]
        
        print(f"✓ ML Dataset loaded. Shape: {df_players_ml.shape}")
        print(f"  Available columns: {df_players_ml.columns.tolist()}")
        return True
    except FileNotFoundError as e:
        print(f"✗ Warning: ML dataset CSV file not found. {e}")
        df_players_ml = pd.DataFrame()
        return False
    except Exception as e:
        print(f"✗ Error loading ML dataset: {e}")
        df_players_ml = pd.DataFrame()
        return False

def load_ml_model():
    global model, model_info
    try:
        if os.path.exists("best_xi_model.joblib"):
            model = joblib.load("best_xi_model.joblib")
            print("✓ ML model 'best_xi_model.joblib' loaded successfully.")
            
            # Try to load encoders
            if os.path.exists("best_xi_model_encoders.joblib"):
                model_info = joblib.load("best_xi_model_encoders.joblib")
                print("✓ Model encoders loaded successfully.")
            else:
                print("⚠ Model encoders file not found - will attempt predictions without encoders")
                model_info = None
            
            return True
        else:
            print("⚠ ML model file 'best_xi_model.joblib' not found - continuing without model")
            model = None
            model_info = None
            return False
    except Exception as e:
        print(f"⚠ Error loading ML model: {str(e)[:100]} - continuing without model")
        model = None
        model_info = None
        return False

# Initialize ML components
load_ml_model()
load_ml_dataset()

# Initialize match type data (will be called after app initialization)
def initialize_match_type_data(app=None):
    """Initialize data for all match types - call after app context is ready"""
    try:
        if app:
            with app.app_context():
                load_data_by_match_type()
        else:
            load_data_from_csv()
    except Exception as e:
        print(f"Error initializing match type data: {e}")
        load_data_from_csv()

# Expose datasets for other modules
def get_dataset(match_type='ODI', data_type='batting'):
    """Get dataset for specific match type (batting or bowling)"""
    match_type = match_type.upper()
    if match_type in datasets and data_type in datasets[match_type]:
        return datasets[match_type][data_type]
    return pd.DataFrame()

def get_all_match_types():
    """Get list of all available match types"""
    return list(datasets.keys())

# ========================================================================
# PREDICTION HELPER
# ========================================================================
def predict_player_scores(opposition, pitch_type, weather, player_name, player_role):
    """
    Predict player scores using the ML model with proper feature encoding
    
    Args:
        opposition: String (e.g., 'India')
        pitch_type: String (e.g., 'spin', 'bouncy')
        weather: String (e.g., 'humid', 'sunny')
        player_name: String (player name)
        player_role: String (e.g., 'batting', 'bowling')
    
    Returns:
        Tuple of (batting_score, bowling_score) or None if prediction fails
    """
    global model, model_info, df_players_ml
    
    if model is None:
        print("Error: ML model not loaded")
        return None
    
    if model_info is None:
        print("Error: Model encoders not loaded")
        return None
    
    if df_players_ml.empty:
        print("Error: ML dataset not loaded")
        return None
    
    try:
        # Get encoders
        encoders = model_info.get('encoders', {})
        feature_columns = model_info.get('feature_columns', [])
        
        # Encode categorical features
        encoded_role = encoders['main_role'].transform([player_role])[0] if player_role in encoders['main_role'].classes_ else 0
        encoded_opposition = encoders['opposition'].transform([opposition])[0] if opposition in encoders['opposition'].classes_ else 0
        encoded_pitch = encoders['pitch_type'].transform([pitch_type])[0] if pitch_type in encoders['pitch_type'].classes_ else 0
        encoded_weather = encoders['weather'].transform([weather])[0] if weather in encoders['weather'].classes_ else 0
        encoded_style = encoders['batting_style'].transform(['No_Bowling'])[0]  # Default batting style
        
        # Create input DataFrame with all required features
        input_data = pd.DataFrame({
            'main_role_encoded': [encoded_role],
            'opposition_encoded': [encoded_opposition],
            'pitch_type_encoded': [encoded_pitch],
            'weather_encoded': [encoded_weather],
            'batting_style_encoded': [encoded_style],
            'runs': [0],
            'strike_rate': [0],
            'wickets': [0],
            'economy': [0],
            'average': [0],
            'balls_faced': [0],
            'fours': [0],
            'sixes': [0]
        })
        
        # Reorder to match training features
        input_data = input_data[feature_columns]
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        batting_score, bowling_score = prediction
        
        return float(batting_score), float(bowling_score)
    except Exception as e:
        print(f"Error predicting for {player_name}: {e}")
        import traceback
        traceback.print_exc()
        return None