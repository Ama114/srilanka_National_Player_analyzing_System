#!/usr/bin/env python3
"""
T20 Performance Data Loader
Loads T20 cricket data from CSV into MySQL database
"""

import pandas as pd
import sys
from app import app, db
from models import T20Performance

def load_t20_performance():
    """Load T20 performance data from CSV into database"""
    
    try:
        print("\n" + "="*70)
        print("T20 PERFORMANCE DATA LOADER")
        print("="*70)
        
        # Read CSV file
        csv_file = 'data/T20/t20_performance.csv'
        print(f"\n📂 Reading CSV file: {csv_file}")
        
        df = pd.read_csv(csv_file, encoding='latin1')
        print(f"✓ CSV loaded successfully!")
        print(f"  Total rows: {len(df)}")
        print(f"  Columns: {df.shape[1]}")
        
        # Clean column names
        df.columns = df.columns.str.strip().str.replace('"', '')
        
        # Map column names to database fields
        column_mapping = {
            'Player Name': 'player_name',
            'Opposition': 'opposition',
            'Ground': 'ground',
            'Runs_Scored': 'runs',
            'Balls_Faced': 'balls_faced',
            'SR': 'strike_rate',
            '4s': 'fours',
            '6s': 'sixes',
            'Pos_Bat': 'bat_position',
            'Dismissal': 'dismissal',
            'Runs_Conceded': 'runs_conceded',
            'Wickets': 'wickets',
            'Overs': 'overs',
            'Maidens': 'maidens',
            'Econ': 'economy',
            'Pos_Bowl': 'bowling_pos',
            'Pitch_Type': 'pitch_type',
            'Date': 'date',
            'Weather': 'weather',
            'Role': 'main_role',
            'Bowling_Style': 'bowling_style'
        }
        
        # Start database transaction
        with app.app_context():
            try:
                # Delete existing T20 data
                count_before = db.session.query(T20Performance).count()
                if count_before > 0:
                    print(f"\n🗑️  Removing {count_before} existing T20 records...")
                    db.session.query(T20Performance).delete()
                    db.session.commit()
                
                # Prepare records for insertion
                print(f"\n⏳ Processing {len(df)} records for insertion...")
                records = []
                
                for idx, row in df.iterrows():
                    try:
                        # Create record with mapped columns
                        record = T20Performance()
                        record.match_type = 'T20'
                        
                        # Map each column
                        for csv_col, db_col in column_mapping.items():
                            if csv_col in df.columns:
                                value = row[csv_col]
                                
                                # Handle NaN values
                                if pd.isna(value):
                                    value = None
                                
                                # Type conversion for numeric fields
                                if db_col in ['runs', 'balls_faced', 'wickets', 'fours', 'sixes', 
                                             'bat_position', 'maidens', 'runs_conceded', 'bowling_pos']:
                                    try:
                                        value = int(float(value)) if value is not None else 0
                                    except (ValueError, TypeError):
                                        value = 0
                                
                                elif db_col in ['strike_rate', 'economy', 'overs']:
                                    try:
                                        value = float(value) if value is not None else 0.0
                                    except (ValueError, TypeError):
                                        value = 0.0
                                
                                # Set the attribute
                                if hasattr(record, db_col):
                                    setattr(record, db_col, value)
                        
                        # Set default values for missing fields
                        if not record.player_name:
                            record.player_name = 'Unknown'
                        if not record.opposition:
                            record.opposition = 'Unknown'
                        if not record.ground:
                            record.ground = 'Unknown'
                        
                        records.append(record)
                        
                        # Progress indicator
                        if (idx + 1) % 100 == 0:
                            print(f"  ✓ Processed {idx + 1}/{len(df)} records")
                    
                    except Exception as e:
                        print(f"  ⚠️  Warning: Error processing row {idx}: {str(e)[:50]}")
                        continue
                
                # Bulk insert records
                print(f"\n💾 Inserting {len(records)} records into database...")
                db.session.bulk_save_objects(records, return_defaults=False)
                db.session.commit()
                
                print(f"✅ Successfully inserted {len(records)} T20 records!")
                
                # Verify insertion
                count_after = db.session.query(T20Performance).count()
                print(f"   Database now contains: {count_after} T20 records")
                
                # Show data summary
                print(f"\n📊 DATA SUMMARY:")
                players = db.session.query(T20Performance.player_name).distinct().count()
                print(f"   • Unique Players: {players}")
                
                oppositions = db.session.query(T20Performance.opposition).distinct().count()
                print(f"   • Unique Oppositions: {oppositions}")
                
                grounds = db.session.query(T20Performance.ground).distinct().count()
                print(f"   • Unique Grounds: {grounds}")
                
                total_runs = db.session.query(db.func.sum(T20Performance.runs)).scalar() or 0
                print(f"   • Total Runs: {int(total_runs)}")
                
                total_wickets = db.session.query(db.func.sum(T20Performance.wickets)).scalar() or 0
                print(f"   • Total Wickets: {int(total_wickets)}")
                
                print("\n" + "="*70)
                print("✅ T20 DATA LOADING COMPLETE!")
                print("="*70 + "\n")
                
                return True
                
            except Exception as db_error:
                db.session.rollback()
                print(f"\n❌ Database Error: {db_error}")
                print("   Rolling back transaction...")
                return False
    
    except FileNotFoundError:
        print(f"\n❌ CSV file not found: {csv_file}")
        print("   Please ensure the file exists in the data/T20/ folder")
        return False
    except Exception as error:
        print(f"\n❌ Error: {error}")
        return False

if __name__ == '__main__':
    success = load_t20_performance()
    sys.exit(0 if success else 1)
