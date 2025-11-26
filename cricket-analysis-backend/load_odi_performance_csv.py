"""
Script to load odi_performance.csv file into MySQL odi_performance table
This script reads the CSV file and loads data into the cricket_analysis database
"""
import pandas as pd
from app import app, db
from models import ODIPerformance
from sqlalchemy.exc import SQLAlchemyError

def load_odi_performance_from_csv():
    """Load ODI performance data from odi_performance.csv and insert into database"""
    with app.app_context():
        try:
            # Check if table already has data
            existing_count = ODIPerformance.query.count()
            if existing_count > 0:
                response = input(f"Table already has {existing_count} records. Do you want to clear and reload? (yes/no): ")
                if response.lower() != 'yes':
                    print("Skipping load. Exiting.")
                    return
                else:
                    # Clear existing data
                    ODIPerformance.query.delete()
                    db.session.commit()
                    print("Cleared existing data.")
            
            print("Loading CSV file: odi_performance.csv...")
            df = pd.read_csv('odi_performance.csv', encoding='utf-8')
            df.columns = df.columns.str.strip()
            
            print(f"CSV loaded. Total rows: {len(df)}")
            
            # Filter only ODI records
            df = df[df['match_type'].str.lower() == 'odi']
            print(f"ODI records: {len(df)}")
            
            # Group by player_name, opposition, and ground to aggregate stats
            # This creates one record per player-opposition-ground combination
            grouped = df.groupby(['player_name', 'opposition', 'ground']).agg({
                'matches': 'sum',  # Sum matches (each row is 1 match)
                'batting_runs': 'sum',
                'bf': 'sum',  # Balls faced
                'sr': 'mean',  # Average strike rate
                'wicket_taken': 'sum',
                'runs_conceded': 'sum',
                'overs': 'sum',
                'econ': 'mean'  # Average economy rate
            }).reset_index()
            
            print(f"Aggregated to {len(grouped)} unique player-opposition-ground combinations")
            
            bulk_records = []
            for _, row in grouped.iterrows():
                player_name = str(row['player_name']).strip()
                opposition = str(row['opposition']).strip()
                ground = str(row['ground']).strip()
                
                matches = int(row['matches']) if pd.notna(row['matches']) else 0
                runs = int(row['batting_runs']) if pd.notna(row['batting_runs']) else 0
                balls_faced = int(row['bf']) if pd.notna(row['bf']) else 0
                strike_rate = float(row['sr']) if pd.notna(row['sr']) else 0.0
                wickets = int(row['wicket_taken']) if pd.notna(row['wicket_taken']) else 0
                runs_conceded = int(row['runs_conceded']) if pd.notna(row['runs_conceded']) else 0
                overs = float(row['overs']) if pd.notna(row['overs']) else 0.0
                economy = float(row['econ']) if pd.notna(row['econ']) else 0.0
                
                # Calculate batting average (runs per match, approximate)
                # For more accurate average, we'd need dismissals count
                average = round(runs / matches, 2) if matches > 0 and runs > 0 else 0.0
                
                # Calculate economy if not present but we have overs and runs_conceded
                if economy == 0.0 and overs > 0 and runs_conceded > 0:
                    economy = round(runs_conceded / overs, 2)
                
                # Store runs_conceded in notes field for bowling stats
                notes_value = f"runs_conceded:{runs_conceded}" if runs_conceded > 0 else None
                
                record = ODIPerformance(
                    player_name=player_name,
                    opposition=opposition,
                    ground=ground,
                    matches=matches,
                    runs=runs,
                    strike_rate=round(strike_rate, 2),
                    average=average,
                    wickets=wickets,
                    economy=round(economy, 2),
                    notes=notes_value
                )
                bulk_records.append(record)
            
            print(f"Created {len(bulk_records)} records. Inserting into database...")
            
            # Bulk insert in batches
            batch_size = 100
            total_batches = (len(bulk_records) + batch_size - 1) // batch_size
            for i in range(0, len(bulk_records), batch_size):
                batch = bulk_records[i:i + batch_size]
                db.session.bulk_save_objects(batch)
                db.session.commit()
                batch_num = i//batch_size + 1
                print(f"Inserted batch {batch_num}/{total_batches} ({len(batch)} records)")
            
            print(f"\n✅ Successfully loaded {len(bulk_records)} ODI performance records into database!")
            print(f"   - Players: {df['player_name'].nunique()}")
            print(f"   - Grounds: {df['ground'].nunique()}")
            print(f"   - Oppositions: {df['opposition'].nunique()}")
            
        except FileNotFoundError:
            print("❌ Error: 'odi_performance.csv' file not found in current directory.")
            print("   Please make sure the CSV file is in the cricket-analysis-backend folder.")
        except SQLAlchemyError as err:
            db.session.rollback()
            print(f"❌ Database Error: {err}")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=" * 60)
    print("ODI Performance CSV to Database Loader")
    print("=" * 60)
    print("\nThis script will load data from 'odi_performance.csv'")
    print("into the 'odi_performance' table in MySQL database.\n")
    
    load_odi_performance_from_csv()
    
    print("\n" + "=" * 60)
    print("Load completed!")
    print("=" * 60)

