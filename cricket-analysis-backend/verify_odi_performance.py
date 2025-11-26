"""
Script to verify odi_performance table data
Check how many records are in the database and show sample data
"""
from app import app, db
from models import ODIPerformance
from sqlalchemy import func

def verify_odi_performance():
    """Verify ODI performance data in database"""
    with app.app_context():
        try:
            # Count total records
            total_count = ODIPerformance.query.count()
            print(f"\n📊 Total records in odi_performance table: {total_count}")
            
            if total_count == 0:
                print("❌ No records found in database!")
                return
            
            # Count unique players
            unique_players = db.session.query(func.count(func.distinct(ODIPerformance.player_name))).scalar()
            print(f"👥 Unique players: {unique_players}")
            
            # Count unique grounds
            unique_grounds = db.session.query(func.count(func.distinct(ODIPerformance.ground))).scalar()
            print(f"🏟️  Unique grounds: {unique_grounds}")
            
            # Count unique oppositions
            unique_oppositions = db.session.query(func.count(func.distinct(ODIPerformance.opposition))).scalar()
            print(f"🌍 Unique oppositions: {unique_oppositions}")
            
            # Show sample records
            print(f"\n📋 Sample records (first 5):")
            print("-" * 80)
            samples = ODIPerformance.query.limit(5).all()
            for i, record in enumerate(samples, 1):
                print(f"\n{i}. Player: {record.player_name}")
                print(f"   Opposition: {record.opposition} | Ground: {record.ground}")
                print(f"   Matches: {record.matches} | Runs: {record.runs} | Wickets: {record.wickets}")
                print(f"   Strike Rate: {record.strike_rate} | Average: {record.average} | Economy: {record.economy}")
            
            # Count players with batting data
            batsmen_count = ODIPerformance.query.filter(ODIPerformance.runs > 0).distinct(ODIPerformance.player_name).count()
            print(f"\n🏏 Players with batting data (runs > 0): {batsmen_count}")
            
            # Count players with bowling data
            bowlers_count = ODIPerformance.query.filter(ODIPerformance.wickets > 0).distinct(ODIPerformance.player_name).count()
            print(f"🎳 Players with bowling data (wickets > 0): {bowlers_count}")
            
            print("\n✅ Database verification completed!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=" * 80)
    print("ODI Performance Database Verification")
    print("=" * 80)
    verify_odi_performance()
    print("=" * 80)

