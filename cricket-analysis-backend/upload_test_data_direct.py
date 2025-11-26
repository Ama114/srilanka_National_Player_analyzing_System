"""
Script to upload Test_performance.csv data directly to MySQL without Flask
"""
import pandas as pd
import pymysql
from datetime import datetime
import sys

# Database connection parameters
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'admin123'
DB_NAME = 'cricket_analysis'

def connect_to_database():
    """Create database connection"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.Error as err:
        print(f"❌ Database Connection Error: {err}")
        return None

def upload_test_performance_data(csv_file_path):
    """
    Load Test_performance.csv and upload all records to test_performance table
    """
    try:
        print("=" * 70)
        print("TEST PERFORMANCE DATA UPLOAD TO MYSQL")
        print("=" * 70)
        
        # Read CSV file
        print(f"\n1. Reading CSV file: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        print(f"   ✓ CSV loaded successfully")
        print(f"   Total records in CSV: {len(df)}")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        print(f"\n2. Column names cleaned")
        
        # Connect to database
        print(f"\n3. Connecting to MySQL database...")
        connection = connect_to_database()
        if not connection:
            return False
        print(f"   ✓ Connected to database '{DB_NAME}'")
        
        cursor = connection.cursor()
        
        # Check if table exists and has data
        try:
            cursor.execute("SELECT COUNT(*) as count FROM test_performance")
            result = cursor.fetchone()
            existing_count = result['count'] if result else 0
            
            if existing_count > 0:
                print(f"\n   ⚠ WARNING: test_performance table already has {existing_count} records")
                response = input("   Do you want to DELETE existing records and replace? (yes/no): ").lower()
                if response == 'yes':
                    print("   Deleting existing records...")
                    cursor.execute("DELETE FROM test_performance")
                    connection.commit()
                    print("   ✓ Existing records deleted")
                else:
                    print("   Upload cancelled")
                    connection.close()
                    return False
        except Exception as e:
            print(f"   ℹ Table is empty or doesn't exist yet: {str(e)[:50]}")
        
        print(f"\n4. Processing records for upload...")
        
        # Prepare insert query
        insert_query = """
        INSERT INTO test_performance 
        (player_name, opposition, ground, matches, runs, strike_rate, average, wickets, economy,
         main_role, balls_faced, fours, sixes, bat_position, dismissal, pitch_type, 
         weather, bowling_style, overs, maidens, runs_conceded, bowling_pos, date, match_type)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s,
         %s, %s, %s, %s, %s, %s, %s,
         %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        records_to_insert = []
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                # Convert data types and handle missing values
                player_name = str(row.get('Player Name', '')).strip()
                opposition = str(row.get('Opposition', '')).strip()
                ground = str(row.get('Ground', '')).strip()
                matches = int(float(row.get('Matches', 0))) if pd.notna(row.get('Matches')) else 0
                runs = int(float(row.get('Runs_Scored', 0))) if pd.notna(row.get('Runs_Scored')) else 0
                strike_rate = float(row.get('SR', 0)) if pd.notna(row.get('SR')) else 0.0
                average = float(row.get('Ave', 0)) if pd.notna(row.get('Ave')) else 0.0
                wickets = int(float(row.get('Wickets', 0))) if pd.notna(row.get('Wickets')) else 0
                economy = float(row.get('Econ', 0)) if pd.notna(row.get('Econ')) else 0.0
                
                main_role = str(row.get('Role', '')).strip()
                balls_faced = int(float(row.get('Balls_Faced', 0))) if pd.notna(row.get('Balls_Faced')) else 0
                fours = int(float(row.get('4s', 0))) if pd.notna(row.get('4s')) else 0
                sixes = int(float(row.get('6s', 0))) if pd.notna(row.get('6s')) else 0
                bat_position = int(float(row.get('Pos_Bat', 0))) if pd.notna(row.get('Pos_Bat')) else None
                dismissal = str(row.get('Dismissal', '')).strip() if pd.notna(row.get('Dismissal')) else None
                pitch_type = str(row.get('Pitch_Type', '')).strip()
                weather = str(row.get('Weather', '')).strip()
                bowling_style = str(row.get('Bowling_Action', '')).strip() if pd.notna(row.get('Bowling_Action')) else None
                
                overs = float(row.get('Overs', 0)) if pd.notna(row.get('Overs')) else 0.0
                maidens = int(float(row.get('Maidens', 0))) if pd.notna(row.get('Maidens')) else 0
                runs_conceded = int(float(row.get('Runs_Conceded', 0))) if pd.notna(row.get('Runs_Conceded')) else 0
                bowling_pos = int(float(row.get('Pos_Bowl', 0))) if pd.notna(row.get('Pos_Bowl')) else None
                
                # Parse date
                date = None
                if pd.notna(row.get('Date')):
                    try:
                        date = pd.to_datetime(row.get('Date')).date()
                    except:
                        date = None
                
                record_data = (
                    player_name, opposition, ground, matches, runs, strike_rate, average, wickets, economy,
                    main_role, balls_faced, fours, sixes, bat_position, dismissal, pitch_type,
                    weather, bowling_style, overs, maidens, runs_conceded, bowling_pos, date, 'Test'
                )
                
                records_to_insert.append(record_data)
                
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Only show first 5 errors
                    print(f"   Error processing row {idx + 2}: {str(e)[:50]}")
        
        print(f"\n   Records processed: {len(records_to_insert)}")
        print(f"   Errors encountered: {error_count}")
        
        if len(records_to_insert) == 0:
            print("\n❌ No valid records to insert!")
            connection.close()
            return False
        
        # Insert records in batches
        print(f"\n5. Inserting {len(records_to_insert)} records into database...")
        batch_size = 500
        total_inserted = 0
        
        for i in range(0, len(records_to_insert), batch_size):
            batch = records_to_insert[i:i + batch_size]
            try:
                cursor.executemany(insert_query, batch)
                connection.commit()
                total_inserted += len(batch)
                percentage = (total_inserted / len(records_to_insert)) * 100
                print(f"   Inserted: {total_inserted}/{len(records_to_insert)} records ({percentage:.1f}%)")
            except pymysql.Error as e:
                connection.rollback()
                print(f"   ❌ Error during batch insert: {str(e)}")
                connection.close()
                return False
        
        # Verify insertion
        print(f"\n6. Verifying insertion...")
        cursor.execute("SELECT COUNT(*) as count FROM test_performance")
        result = cursor.fetchone()
        final_count = result['count'] if result else 0
        print(f"   ✓ Total records in test_performance table: {final_count}")
        
        # Show sample records
        print(f"\n7. Sample records uploaded:")
        cursor.execute("SELECT player_name, opposition, ground, runs, wickets FROM test_performance LIMIT 3")
        samples = cursor.fetchall()
        for rec in samples:
            print(f"   - {rec['player_name']} vs {rec['opposition']} at {rec['ground']} (Runs: {rec['runs']}, Wickets: {rec['wickets']})")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 70)
        print("✓ UPLOAD COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        return True
    
    except Exception as e:
        print(f"\n❌ UPLOAD FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    csv_path = 'Test_performance.csv'
    success = upload_test_performance_data(csv_path)
    sys.exit(0 if success else 1)
