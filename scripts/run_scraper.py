"""
Script to run the College Basketball data scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import CBBScraper
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main execution"""
    print("=" * 60)
    print("College Basketball Data Scraper")
    print("=" * 60)
    
    # Initialize scraper
    scraper = CBBScraper(db_path='data/database.db')
    
    # Initialize database
    print("\n[1/3] Initializing database...")
    scraper.init_database()
    print("✓ Database initialized")
    
    # Get user input for seasons to scrape
    print("\n[2/4] Choose scraping option:")
    print("  1. Scrape single season (2025 - current)")
    print("  2. Scrape multiple seasons (2021-2025)")
    print("  3. Scrape full historical data (2015-2025)")
    print("  4. Scrape recent games (last 7 days)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    # First, get and save teams
    print("\n[3/4] Fetching team information...")
    teams_df = scraper.get_teams()
    if not teams_df.empty:
        scraper.save_teams_to_db(teams_df)
        print(f"✓ Saved {len(teams_df)} teams")
    
    print("\n[4/4] Scraping data...")
    
    try:
        if choice == "1":
            print("Scraping 2025 season (current)...")
            scraper.scrape_full_season(2025)
        elif choice == "2":
            print("Scraping seasons 2021-2025...")
            scraper.scrape_multiple_seasons(2021, 2025)
        elif choice == "3":
            print("Scraping seasons 2015-2025...")
            print("⚠️  This will take a while (10+ seasons)...")
            scraper.scrape_multiple_seasons(2015, 2025)
        elif choice == "4":
            print("Scraping recent games (last 7 days)...")
            scraper.scrape_recent_games(days=7)
        else:
            print("Invalid choice. Scraping 2025 season by default...")
            scraper.scrape_full_season(2025)
        
        print("\n" + "=" * 60)
        print("✓ Scraping complete!")
        print("=" * 60)
        print(f"\nData saved to: {scraper.db_path}")
        print("Check the database for scraped games and team statistics.")
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        print(f"\n✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
