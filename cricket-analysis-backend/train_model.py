import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

print("Starting model training process...")

# 1. දත්ත කියවීම සහ පිරිසිදු කිරීම (Load and Clean Data)
try:
    # --- මෙතන තමයි අවසාන fix එක තියෙන්නේ ---
    # මුලින්ම file එක single column එකක් විදියට කියවනවා
    df_raw = pd.read_csv('srilanka player 11 dataset.csv', header=None)
    
    # ඒ column එක comma (,) එකෙන් split කරලා, අලුත් columns හදනවා
    df = df_raw[0].str.split(',', expand=True)
    
    # පළවෙනි row එක header එක විදියට සකසනවා
    df.columns = df.iloc[0]
    df = df[1:]
    
    # Column නම් වල තියෙන අනවශ්‍ය quotes (") අයින් කරනවා
    df.columns = df.columns.str.replace('"', '').str.strip()
    
    # අනවශ්‍ය columns අයින් කිරීම සහ දත්ත පිරිසිදු කිරීම
    df.drop(columns=['Role'], inplace=True, errors='ignore')
    df.fillna(0, inplace=True)
    
    # දත්ත වල type එක numeric වලට හරවනවා
    numeric_cols = ['Runs', 'Balls_Faced', 'Strike_Rate', 'Wickets_Taken', 'Overs_Bowled', 'Runs_Conceded']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    print("Dataset loaded and cleaned successfully.")
    # print(df.columns.tolist()) # You can uncomment this to check the final column names

except FileNotFoundError:
    print("Error: 'srilanka player 11 dataset.csv' not found.")
    exit()
except Exception as e:
    print(f"An error occurred during data loading: {e}")
    exit()

# 2. Performance Score එක හැදීම (Feature Engineering)
def calculate_performance(row):
    try:
        if row['Player_Type'] == 'Batsman':
            return (row['Runs'] * 1.5) + (row['Strike_Rate'] * 0.5)
        elif row['Player_Type'] == 'Bowler':
            return (row['Wickets_Taken'] * 25) - (row['Runs_Conceded'] * 0.5)
        else:
            return 0
    except (ValueError, TypeError):
        return 0

df['Performance_Score'] = df.apply(calculate_performance, axis=1)
print("Performance Score calculated for each player.")

# 3. Model එකට අවශ්‍ය දත්ත සකස් කිරීම
# දැන් column නම් හරියටම තියෙන නිසා මේක වැඩ කරනවා
X = df[['Opponent_Team', 'Pitch_Type', 'Weather', 'Player_Name', 'Player_Type']]
y = df['Performance_Score']

categorical_features = ['Opponent_Team', 'Pitch_Type', 'Weather', 'Player_Name', 'Player_Type']
one_hot_encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)

preprocessor = ColumnTransformer(
    transformers=[('cat', one_hot_encoder, categorical_features)],
    remainder='passthrough'
)

# 4. Model එක තෝරාගෙන Train කිරීම
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

model.fit(X, y)
print("Model training completed successfully.")

# 5. Train කරපු Model එක Save කිරීම
joblib.dump(model, 'best_xi_model.joblib')
print("Model saved as 'best_xi_model.joblib'. You can now use it in app.py!")