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
    df_batting = pd.read_csv('odi_batting_cleaned.csv', encoding='latin1')
    numeric_cols_bat = ['Runs', 'BF', '4s', '6s']
    for col in numeric_cols_bat:
        df_batting[col] = pd.to_numeric(df_batting[col], errors='coerce')
    df_batting.dropna(subset=numeric_cols_bat, inplace=True)
    print("Batting dataset ('odi_batting_cleaned.csv') loaded successfully.")
except FileNotFoundError:
    print("Warning: 'odi_batting_cleaned.csv' not found.")
    df_batting = pd.DataFrame()

# --- Load Bowling Data ---
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

# --- ML Loading Functions ---
def load_ml_dataset():
    global df_players_ml, default_weather
    try:
        df_players_ml = pd.read_csv('srilanka player 11 dataset.csv')
        df_players_ml.columns = df_players_ml.columns.str.strip()
        
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