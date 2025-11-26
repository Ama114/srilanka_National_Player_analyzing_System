"""
Script to update odi_performance table with new columns
This will add all missing columns from the CSV file to the existing table
"""
from app import app, db
from models import ODIPerformance
from sqlalchemy import text

def update_table_structure():
    """Add new columns to existing odi_performance table"""
    with app.app_context():
        try:
            print("Updating odi_performance table structure...")
            
            # List of new columns to add
            new_columns = [
                ("match_type", "VARCHAR(20) DEFAULT 'ODI'"),
                ("batting_style", "VARCHAR(50)"),
                ("main_role", "VARCHAR(50)"),
                ("balls_faced", "INT DEFAULT 0"),
                ("fours", "INT DEFAULT 0"),
                ("sixes", "INT DEFAULT 0"),
                ("bat_position", "INT"),
                ("dismissal", "VARCHAR(50)"),
                ("pitch_type", "VARCHAR(50)"),
                ("date", "DATE"),
                ("weather", "VARCHAR(50)"),
                ("bowling_style", "VARCHAR(50)"),
                ("overs", "FLOAT DEFAULT 0.0"),
                ("maidens", "INT DEFAULT 0"),
                ("runs_conceded", "INT DEFAULT 0"),
                ("bowling_pos", "INT"),
            ]
            
            # Check which columns already exist and add missing ones
            existing_columns = db.session.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'odi_performance'
            """)).fetchall()
            
            existing_column_names = [col[0] for col in existing_columns]
            
            for column_name, column_type in new_columns:
                if column_name not in existing_column_names:
                    try:
                        alter_sql = f"ALTER TABLE odi_performance ADD COLUMN {column_name} {column_type}"
                        db.session.execute(text(alter_sql))
                        db.session.commit()
                        print(f"✅ Added column: {column_name}")
                    except Exception as e:
                        print(f"⚠️  Column {column_name} might already exist or error: {e}")
                        db.session.rollback()
                else:
                    print(f"ℹ️  Column {column_name} already exists")
            
            # Update notes column size if needed
            try:
                db.session.execute(text("ALTER TABLE odi_performance MODIFY COLUMN notes VARCHAR(500)"))
                db.session.commit()
                print("✅ Updated notes column size")
            except Exception as e:
                print(f"ℹ️  Notes column update: {e}")
                db.session.rollback()
            
            print("\n✅ Table structure update completed!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=" * 60)
    print("ODI Performance Table Structure Updater")
    print("=" * 60)
    print("\nThis script will add new columns to the existing")
    print("odi_performance table to match the CSV file structure.\n")
    
    update_table_structure()
    
    print("\n" + "=" * 60)
    print("Update completed!")
    print("=" * 60)
    print("\nNext step: Run seed_odi_performance.py to reload data with all columns")

