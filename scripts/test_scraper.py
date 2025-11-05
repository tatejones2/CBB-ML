"""
Quick test of the scraper functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import CBBScraper
from datetime import datetime, timedelta

def test_scraper():
    """Test the scraper with a small sample"""
    
    print("=" * 60)
    print("Testing CBB Scraper")
    print("=" * 60)
    
    # Initialize scraper
    scraper = CBBScraper(db_path='data/test_database.db')
    
    # Initialize database
    print("\n[1/4] Initializing database...")
    scraper.init_database()
    print("✓ Database initialized")
    
    # Get teams
    print("\n[2/4] Fetching teams...")
    teams_df = scraper.get_teams()
    print(f"✓ Found {len(teams_df)} teams")
    if not teams_df.empty:
        scraper.save_teams_to_db(teams_df)
        print("✓ Teams saved to database")
    
    # Scrape games from a specific date (Jan 15, 2024 - known to have games)
    print("\n[3/4] Scraping games from January 15, 2024...")
    games_df = scraper.scrape_scoreboard_by_date('20240115')
    print(f"✓ Found {len(games_df)} games")
    
    if not games_df.empty:
        print("\nSample games:")
        for i, game in games_df.head(3).iterrows():
            print(f"  {game['away_team']} ({game['away_score']}) @ {game['home_team']} ({game['home_score']})")
        
        scraper.save_games_to_db(games_df)
        print("\n✓ Games saved to database")
    
    # Calculate stats from the games
    print("\n[4/4] Calculating team statistics...")
    stats_df = scraper.calculate_team_stats_from_games(games_df)
    print(f"✓ Calculated stats for {len(stats_df)} teams")
    
    if not stats_df.empty:
        scraper.save_team_stats_to_db(stats_df)
        print("✓ Team stats saved to database")
        
        print("\nTop 5 teams by PPG:")
        top_teams = stats_df.nlargest(5, 'ppg')[['team_name', 'wins', 'losses', 'ppg', 'opp_ppg']]
        print(top_teams.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("✓ Scraper test complete!")
    print("=" * 60)
    print(f"\nTest database created at: data/test_database.db")
    print("Run 'python scripts/inspect_data.py --db data/test_database.db' to view data")


if __name__ == "__main__":
    test_scraper()
