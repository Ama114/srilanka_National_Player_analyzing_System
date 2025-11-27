import joblib
import sklearn
import pandas as pd
import os
import sys

print("="*50)
print("🔍 ML MODEL DEBUGGER")
print("="*50)

# 1. Check Versions
print(f"✅ Python Version: {sys.version.split()[0]}")
print(f"✅ Scikit-learn Version: {sklearn.__version__}")
print(f"✅ Pandas Version: {pd.__version__}")
print(f"✅ Joblib Version: {joblib.__version__}")

# 2. Check Files
MODEL_PATH = 'multi_target_odi_model.joblib'
DATA_PATH = 'odi_performance.csv'

print("-" * 20)
if os.path.exists(MODEL_PATH):
    print(f"✅ Model File Found: {MODEL_PATH}")
else:
    print(f"❌ Model File NOT Found! Please upload {MODEL_PATH}")

if os.path.exists(DATA_PATH):
    print(f"✅ Data File Found: {DATA_PATH}")
else:
    print(f"❌ Data File NOT Found! Please upload {DATA_PATH}")

# 3. Try Loading Model
print("-" * 20)
print("⏳ Attempting to load model...")
try:
    model = joblib.load(MODEL_PATH)
    print("✅ Model Loaded Successfully!")
    print(f"   Type: {type(model)}")
except Exception as e:
    print("❌ ERROR LOADING MODEL:")
    print(f"   {str(e)}")
    print("\n💡 SUGGESTION:")
    if "sparse_output" in str(e) or "sklearn" in str(e):
        print("   Your scikit-learn version is too old for this model.")
        print("   Please run: pip install scikit-learn==1.6.1")

# 4. Try Loading Data
print("-" * 20)
print("⏳ Attempting to load and process data...")
try:
    df = pd.read_csv(DATA_PATH)
    print(f"✅ CSV Loaded. Rows: {len(df)}")
    
    # Check if we can create features
    print("   Checking feature creation logic...")
    # (Simple logic check)
    numeric_cols = ['batting_runs', 'wicket_taken', 'sr', 'econ', 'fours', 'sixes']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    print("✅ Data processing check passed.")

except Exception as e:
    print(f"❌ Error processing data: {e}")

print("="*50)