from app import app
from models import db, PlayerPerformanceRecord
import pandas as pd
import os

def debug_seeding():
    print("=== Debugging Process Started ===")
    
    # 1. File Exist වෙනවද බැලීම
    csv_file = 'srilanka player 11 dataset.csv'
    if not os.path.exists(csv_file):
        print(f"ERROR: '{csv_file}' file එක සොයාගත නොහැක. File path එක පරීක්ෂා කරන්න.")
        return

    print(f"SUCCESS: '{csv_file}' file එක සොයාගත්තා.")

    with app.app_context():
        try:
            # 2. CSV එක කියවීම
            df = pd.read_csv(csv_file)
            print(f"CSV Loaded. Rows: {len(df)}")
            print(f"Columns Found: {df.columns.tolist()}")
            
            # Columns සුද්ද කිරීම
            df.columns = df.columns.str.strip()

            # 3. Data Loop එක
            print("Attempting to add records...")
            added_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Data Map කිරීම
                    record = PlayerPerformanceRecord(
                        player_name=row.get('Player_Name') or row.get('Player Name'),
                        player_type=row.get('Player_Type', 'Batsman'),
                        role=row.get('Role', 'Batsman'),
                        opponent_team=row.get('Opponent_Team') or row.get('Opponent Team'),
                        pitch_type=row.get('Pitch_Type') or row.get('Pitch Type'),
                        weather=row.get('Weather', 'Balanced'),
                        runs=row.get('Runs', 0),
                        wickets_taken=row.get('Wickets', 0)
                    )
                    db.session.add(record)
                    added_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Row {index} Error: {e}")

            # 4. Commit කිරීම
            db.session.commit()
            print(f"=== Process Complete ===")
            print(f"Successfully Added: {added_count}")
            print(f"Errors/Skipped: {error_count}")
            
            # 5. Final Check
            final_count = PlayerPerformanceRecord.query.count()
            print(f"Total Records in Database Now: {final_count}")

        except Exception as e:
            db.session.rollback()
            print(f"CRITICAL DATABASE ERROR: {str(e)}")

if __name__ == "__main__":
    debug_seeding()