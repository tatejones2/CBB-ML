"""
Utility script to inspect the scraped data in the database
"""

import sqlite3
import pandas as pd
import sys


def inspect_database(db_path='data/database.db'):
    """Inspect the contents of the database"""
    try:
        conn = sqlite3.connect(db_path)
        
        print("=" * 70)
        print("DATABASE INSPECTION")
        print("=" * 70)
        
        # Check tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"\n📊 Tables in database: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "-" * 70)
        
        # Games table
        print("\n🏀 GAMES TABLE")
        print("-" * 70)
        games_df = pd.read_sql_query("SELECT * FROM games LIMIT 5", conn)
        print(f"Total games: {pd.read_sql_query('SELECT COUNT(*) as count FROM games', conn)['count'][0]}")
        print("\nSample games:")
        print(games_df.to_string())
        
        # Games by season
        print("\n\nGames by season:")
        season_counts = pd.read_sql_query(
            "SELECT season, COUNT(*) as game_count FROM games GROUP BY season ORDER BY season",
            conn
        )
        print(season_counts.to_string(index=False))
        
        print("\n" + "-" * 70)
        
        # Team stats table
        print("\n📈 TEAM STATS TABLE")
        print("-" * 70)
        stats_df = pd.read_sql_query("SELECT * FROM team_stats LIMIT 5", conn)
        print(f"Total team records: {pd.read_sql_query('SELECT COUNT(*) as count FROM team_stats', conn)['count'][0]}")
        print("\nSample team stats:")
        print(stats_df.to_string())
        
        # Top teams by PPG
        print("\n\nTop 10 teams by PPG:")
        top_teams = pd.read_sql_query(
            """
            SELECT season, team, ppg, opp_ppg, wins, losses 
            FROM team_stats 
            ORDER BY ppg DESC 
            LIMIT 10
            """,
            conn
        )
        print(top_teams.to_string(index=False))
        
        print("\n" + "=" * 70)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


def export_to_csv(db_path='data/database.db', output_dir='data/processed'):
    """Export database tables to CSV files"""
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Export games
        games_df = pd.read_sql_query("SELECT * FROM games", conn)
        games_path = os.path.join(output_dir, 'games.csv')
        games_df.to_csv(games_path, index=False)
        print(f"✓ Exported games to: {games_path}")
        
        # Export team stats
        stats_df = pd.read_sql_query("SELECT * FROM team_stats", conn)
        stats_path = os.path.join(output_dir, 'team_stats.csv')
        stats_df.to_csv(stats_path, index=False)
        print(f"✓ Exported team stats to: {stats_path}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error exporting: {e}")
        return 1
    
    return 0


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Inspect CBB database')
    parser.add_argument('--db', default='data/database.db', help='Database path')
    parser.add_argument('--export', action='store_true', help='Export to CSV files')
    
    args = parser.parse_args()
    
    if args.export:
        print("Exporting database to CSV files...\n")
        return export_to_csv(args.db)
    else:
        return inspect_database(args.db)


if __name__ == "__main__":
    sys.exit(main())
