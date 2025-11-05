"""
Monitor scraping progress in real-time
"""

import sqlite3
import time
import os
from datetime import datetime

def monitor_progress(db_path='data/database.db', interval=5):
    """Monitor the database as it's being populated"""
    
    print("=" * 70)
    print("SCRAPING PROGRESS MONITOR")
    print("=" * 70)
    print("Press Ctrl+C to stop monitoring\n")
    
    last_game_count = 0
    last_team_count = 0
    start_time = time.time()
    
    try:
        while True:
            if not os.path.exists(db_path):
                print("⏳ Waiting for database to be created...")
                time.sleep(interval)
                continue
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get counts
                cursor.execute("SELECT COUNT(*) FROM games")
                game_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM team_stats")
                team_stat_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT season) FROM games")
                seasons = cursor.fetchone()[0]
                
                # Get latest game info
                cursor.execute("""
                    SELECT season, COUNT(*) as count 
                    FROM games 
                    GROUP BY season 
                    ORDER BY season
                """)
                season_breakdown = cursor.fetchall()
                
                conn.close()
                
                # Calculate progress
                games_added = game_count - last_game_count
                elapsed = time.time() - start_time
                rate = game_count / elapsed if elapsed > 0 else 0
                
                # Clear screen and display
                os.system('clear' if os.name != 'nt' else 'cls')
                
                print("=" * 70)
                print("SCRAPING PROGRESS MONITOR")
                print("=" * 70)
                print(f"Time elapsed: {int(elapsed)} seconds ({elapsed/60:.1f} minutes)")
                print(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
                print()
                
                print(f"📊 TOTALS")
                print(f"  Games collected:      {game_count:,}")
                print(f"  Team stats records:   {team_stat_count:,}")
                print(f"  Seasons in database:  {seasons}")
                print(f"  Collection rate:      {rate:.1f} games/second")
                print()
                
                if games_added > 0:
                    print(f"  📈 +{games_added} games since last check")
                print()
                
                print(f"🏀 SEASON BREAKDOWN")
                if season_breakdown:
                    for season, count in season_breakdown:
                        print(f"  Season {season}: {count:,} games")
                else:
                    print("  No games yet...")
                
                print()
                print("=" * 70)
                print("Press Ctrl+C to stop monitoring")
                
                last_game_count = game_count
                last_team_count = team_stat_count
                
            except sqlite3.Error as e:
                print(f"Database error: {e}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring stopped")
        print(f"\nFinal counts:")
        print(f"  Total games: {last_game_count:,}")
        print(f"  Team stats: {last_team_count:,}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor scraping progress')
    parser.add_argument('--db', default='data/database.db', help='Database path')
    parser.add_argument('--interval', type=int, default=5, help='Update interval in seconds')
    
    args = parser.parse_args()
    
    monitor_progress(args.db, args.interval)
