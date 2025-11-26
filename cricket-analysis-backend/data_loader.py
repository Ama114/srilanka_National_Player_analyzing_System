import pandas as pd
import joblib
import os

# Global Variables
df_batting = pd.DataFrame()
df_bowling = pd.DataFrame()
df_players_ml = pd.DataFrame()
model = None
default_weather = 'Balanced'

WICKET_KEEPER_NAMES = {
    'Kusal Mendis', 'Sadeera Samarawickrama'
}

ALL_ROUNDER_NAMES = {
    'Wanindu Hasaranga', 'Dhananjaya de Silva', 'Dasun Shanaka',
    'Dunith Wellalage', 'Chamika Karunaratne', 'Charith Asalanka', 'Janith Liyanage'
}

# --- Load Batting Data ---
try:
    df_batting = pd.read_csv('best_11_odi_new.csv', encoding='latin1')
    # Map new column names to old column names for backward compatibility
    column_mapping = {
        'Player_Name': 'Player Name',
        'Batting_Runs': 'Runs',
        'Bf': 'BF',
        'Fours': '4s',
        'Sixes': '6s',
        'Bat_Position': 'Pos'
    }
    df_batting = df_batting.rename(columns=column_mapping)
    
    numeric_cols_bat = ['Runs', 'BF', '4s', '6s']
    for col in numeric_cols_bat:
        df_batting[col] = pd.to_numeric(df_batting[col], errors='coerce')
    df_batting.dropna(subset=numeric_cols_bat, inplace=True)
    print("Batting dataset ('best_11_odi_new.csv') loaded successfully.")
except FileNotFoundError:
    print("Warning: 'best_11_odi_new.csv' not found.")
    df_batting = pd.DataFrame()
except Exception as e:
    print(f"Error loading batting dataset: {e}")
    df_batting = pd.DataFrame()

# --- Load Bowling Data ---
try:
    df_bowling = pd.read_csv('best_11_odi_new.csv', encoding='latin1')
    # Map new column names to old column names for backward compatibility
    column_mapping_bowl = {
        'Player_Name': 'Player Name',
        'Runs_Conceded': 'Runs',
        'Wicket_taken': 'Wkts'
    }
    df_bowling = df_bowling.rename(columns=column_mapping_bowl)
    
    # Filter rows that have bowling data (non-empty Overs, Runs, Wkts)
    df_bowling = df_bowling[df_bowling['Overs'].notna() & df_bowling['Runs'].notna() & df_bowling['Wkts'].notna()]
    
    numeric_cols_bowl = ['Overs', 'Runs', 'Wkts']
    for col in numeric_cols_bowl:
        df_bowling[col] = pd.to_numeric(df_bowling[col], errors='coerce')
    df_bowling.dropna(subset=numeric_cols_bowl, inplace=True)
    print("Bowling dataset ('best_11_odi_new.csv') loaded successfully.")
except FileNotFoundError:
    print("Warning: 'best_11_odi_new.csv' not found.")
    df_bowling = pd.DataFrame()
except Exception as e:
    print(f"Error loading bowling dataset: {e}")
    df_bowling = pd.DataFrame()

# --- ML Loading Functions ---
def load_ml_dataset():
    global df_players_ml, default_weather
    try:
        df_players_ml = pd.read_csv('best_11_odi_new.csv', encoding='latin1')
        df_players_ml.columns = df_players_ml.columns.str.strip()
        
        # Map column names to match expected format
        column_mapping_ml = {
            'Opposition': 'Opponent_Team',
            'weather': 'Weather',
            'main_role': 'Role'
        }
        df_players_ml = df_players_ml.rename(columns=column_mapping_ml)
        
        # Derive Player_Type from Role (which was mapped from main_role)
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
        
        df_players_ml['Player_Type'] = df_players_ml.apply(derive_player_type, axis=1)
        
        # Ensure Player_Name column exists (already present as Player_Name in CSV)
        if 'Player_Name' not in df_players_ml.columns and 'Player Name' in df_players_ml.columns:
            df_players_ml['Player_Name'] = df_players_ml['Player Name']
        
        # Set default weather
        if 'Weather' in df_players_ml.columns and not df_players_ml['Weather'].dropna().empty:
            default_weather = df_players_ml['Weather'].mode().iloc[0]
        
        print(f"ML Dataset loaded. Shape: {df_players_ml.shape}")
        return True
    except FileNotFoundError:
        print("Warning: ML dataset CSV file not found.")
        df_players_ml = pd.DataFrame()
        return False
    except Exception as e:
        print(f"Error loading ML dataset: {e}")
        df_players_ml = pd.DataFrame()
        return False

def load_ml_model():
    global model
    try:
        model = joblib.load("best_xi_model.joblib")
        print("ML model 'best_xi_model.joblib' loaded successfully.")
        return True
    except FileNotFoundError:
        print("Warning: ML model file not found.")
        model = None
        return False
    except Exception as e:
        print(f"Error loading ML model: {e}")
        model = None
        return False

# Initialize ML components
load_ml_model()
load_ml_dataset()