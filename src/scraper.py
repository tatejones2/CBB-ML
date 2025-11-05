"""
College Basketball Data Scraper
Uses ESPN's unofficial API to collect game data
"""

import requests
import pandas as pd
import time
import sqlite3
from datetime import datetime, timedelta
import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CBBScraper:
    """Scraper for ESPN College Basketball API"""
    
    # ESPN API endpoints
    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball"
    SCOREBOARD_URL = f"{BASE_URL}/scoreboard"
    TEAMS_URL = f"{BASE_URL}/teams"
    
    def __init__(self, db_path='data/database.db'):
        """Initialize scraper with database connection"""
        self.db_path = db_path
        self.session = requests.Session()
        
    def get_json(self, url, params=None, delay=1):
        """
        Fetch JSON data from API with rate limiting
        
        Args:
            url: URL to fetch
            params: Query parameters
            delay: Seconds to wait between requests
        
        Returns:
            JSON data or None if failed
        """
        try:
            logger.info(f"Fetching: {url}")
            time.sleep(delay)  # Rate limiting
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return None
    
    def get_teams(self):
        """
        Get list of all college basketball teams from ESPN
        
        Returns:
            DataFrame with team information
        """
        data = self.get_json(self.TEAMS_URL, params={'limit': 400})
        
        if not data or 'sports' not in data:
            logger.error("Failed to fetch teams")
            return pd.DataFrame()
        
        teams = []
        sports_data = data['sports'][0] if data['sports'] else {}
        leagues = sports_data.get('leagues', [])
        
        for league in leagues:
            for team in league.get('teams', []):
                team_info = team.get('team', {})
                teams.append({
                    'team_id': team_info.get('id'),
                    'team_name': team_info.get('displayName'),
                    'team_short_name': team_info.get('shortDisplayName'),
                    'abbreviation': team_info.get('abbreviation'),
                    'logo': team_info.get('logo'),
                })
        
        logger.info(f"Found {len(teams)} teams")
        return pd.DataFrame(teams)
    
    def scrape_scoreboard_by_date(self, date):
        """
        Scrape games for a specific date
        
        Args:
            date: Date string in YYYYMMDD format
        
        Returns:
            DataFrame with game data
        """
        params = {'dates': date}
        data = self.get_json(self.SCOREBOARD_URL, params=params)
        
        if not data or 'events' not in data:
            logger.warning(f"No games found for {date}")
            return pd.DataFrame()
        
        games = []
        
        for event in data['events']:
            try:
                game_id = event.get('id')
                game_date = event.get('date')
                status = event.get('status', {})
                
                # Only include completed games
                if status.get('type', {}).get('completed') != True:
                    continue
                
                competitions = event.get('competitions', [])
                if not competitions:
                    continue
                
                competition = competitions[0]
                competitors = competition.get('competitors', [])
                
                if len(competitors) < 2:
                    continue
                
                # Determine home and away teams
                home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)
                away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)
                
                if not home_team or not away_team:
                    continue
                
                game_data = {
                    'game_id': game_id,
                    'date': game_date,
                    'season': event.get('season', {}).get('year'),
                    'home_team_id': home_team.get('team', {}).get('id'),
                    'home_team': home_team.get('team', {}).get('displayName'),
                    'home_score': int(home_team.get('score', 0)),
                    'away_team_id': away_team.get('team', {}).get('id'),
                    'away_team': away_team.get('team', {}).get('displayName'),
                    'away_score': int(away_team.get('score', 0)),
                    'neutral_site': competition.get('neutralSite', False),
                    'conference_game': competition.get('conferenceCompetition', False),
                    'venue': competition.get('venue', {}).get('fullName'),
                    'attendance': competition.get('attendance'),
                }
                
                games.append(game_data)
                
            except Exception as e:
                logger.warning(f"Error parsing game: {e}")
                continue
        
        logger.info(f"Found {len(games)} completed games for {date}")
        return pd.DataFrame(games)
    
    def scrape_date_range(self, start_date, end_date):
        """
        Scrape games for a date range
        
        Args:
            start_date: Start date (datetime object)
            end_date: End date (datetime object)
        
        Returns:
            DataFrame with all games in range
        """
        all_games = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y%m%d')
            games_df = self.scrape_scoreboard_by_date(date_str)
            
            if not games_df.empty:
                all_games.append(games_df)
            
            current_date += timedelta(days=1)
        
        if all_games:
            return pd.concat(all_games, ignore_index=True)
        return pd.DataFrame()
    
    def scrape_season(self, year):
        """
        Scrape all games for a college basketball season
        
        Args:
            year: Season year (e.g., 2024 for 2023-24 season)
        
        Returns:
            DataFrame with game data
        """
        # College basketball season typically runs November to April
        # For 2024 season, that's Nov 2023 - Apr 2024
        start_date = datetime(year - 1, 11, 1)
        end_date = datetime(year, 4, 30)
        
        logger.info(f"Scraping {year} season from {start_date.date()} to {end_date.date()}")
        
        return self.scrape_date_range(start_date, end_date)
    
    def get_team_stats(self, team_id):
        """
        Get statistics for a specific team
        
        Args:
            team_id: ESPN team ID
        
        Returns:
            Dictionary with team statistics
        """
        url = f"{self.TEAMS_URL}/{team_id}"
        data = self.get_json(url)
        
        if not data or 'team' not in data:
            logger.warning(f"Failed to fetch stats for team {team_id}")
            return None
        
        team = data['team']
        
        # Extract basic team info
        stats = {
            'team_id': team.get('id'),
            'team_name': team.get('displayName'),
            'season': None,  # Will be set by caller
        }
        
        # Get record if available
        record = team.get('record', {})
        if 'items' in record and record['items']:
            record_item = record['items'][0]
            stats['wins'] = record_item.get('stats', [{}])[0].get('value', 0)
            stats['losses'] = record_item.get('stats', [{}])[1].get('value', 0) if len(record_item.get('stats', [])) > 1 else 0
        
        return stats
    
    def calculate_team_stats_from_games(self, games_df):
        """
        Calculate team statistics from games DataFrame
        
        Args:
            games_df: DataFrame with game data
        
        Returns:
            DataFrame with calculated team statistics
        """
        if games_df.empty:
            return pd.DataFrame()
        
        team_stats = []
        
        # Get unique teams
        home_teams = games_df[['home_team_id', 'home_team', 'season']].drop_duplicates()
        away_teams = games_df[['away_team_id', 'away_team', 'season']].drop_duplicates()
        
        # Combine and get unique teams
        home_teams.columns = ['team_id', 'team_name', 'season']
        away_teams.columns = ['team_id', 'team_name', 'season']
        all_teams = pd.concat([home_teams, away_teams]).drop_duplicates()
        
        for _, team_row in all_teams.iterrows():
            team_id = team_row['team_id']
            team_name = team_row['team_name']
            season = team_row['season']
            
            # Filter games for this team
            home_games = games_df[games_df['home_team_id'] == team_id]
            away_games = games_df[games_df['away_team_id'] == team_id]
            
            # Calculate statistics
            total_games = len(home_games) + len(away_games)
            
            if total_games == 0:
                continue
            
            # Wins and losses
            home_wins = (home_games['home_score'] > home_games['away_score']).sum()
            away_wins = (away_games['away_score'] > away_games['home_score']).sum()
            total_wins = home_wins + away_wins
            total_losses = total_games - total_wins
            
            # Points scored and allowed
            home_points = home_games['home_score'].sum()
            away_points = away_games['away_score'].sum()
            total_points = home_points + away_points
            
            home_points_allowed = home_games['away_score'].sum()
            away_points_allowed = away_games['home_score'].sum()
            total_points_allowed = home_points_allowed + away_points_allowed
            
            # Calculate averages
            ppg = total_points / total_games if total_games > 0 else 0
            opp_ppg = total_points_allowed / total_games if total_games > 0 else 0
            win_pct = total_wins / total_games if total_games > 0 else 0
            
            team_stats.append({
                'season': season,
                'team_id': team_id,
                'team_name': team_name,
                'games': total_games,
                'wins': total_wins,
                'losses': total_losses,
                'win_pct': win_pct,
                'ppg': ppg,
                'opp_ppg': opp_ppg,
                'point_diff': ppg - opp_ppg,
            })
        
        logger.info(f"Calculated stats for {len(team_stats)} teams")
        return pd.DataFrame(team_stats)
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Games table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                date TEXT,
                season INTEGER,
                home_team_id TEXT,
                home_team TEXT,
                home_score INTEGER,
                away_team_id TEXT,
                away_team TEXT,
                away_score INTEGER,
                neutral_site INTEGER DEFAULT 0,
                conference_game INTEGER DEFAULT 0,
                venue TEXT,
                attendance INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Team stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_stats (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                season INTEGER,
                team_id TEXT,
                team_name TEXT,
                games INTEGER,
                wins INTEGER,
                losses INTEGER,
                win_pct REAL,
                ppg REAL,
                opp_ppg REAL,
                point_diff REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(season, team_id)
            )
        ''')
        
        # Team info table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_info (
                team_id TEXT PRIMARY KEY,
                team_name TEXT,
                team_short_name TEXT,
                abbreviation TEXT,
                logo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def save_games_to_db(self, games_df):
        """Save games DataFrame to database"""
        if games_df.empty:
            logger.warning("No games to save")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert boolean to integer
        games_df['neutral_site'] = games_df['neutral_site'].astype(int)
        games_df['conference_game'] = games_df['conference_game'].astype(int)
        
        # Insert or replace games
        for _, game in games_df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO games (
                    game_id, date, season, home_team_id, home_team, home_score,
                    away_team_id, away_team, away_score, neutral_site, 
                    conference_game, venue, attendance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game['game_id'], game['date'], game['season'],
                game['home_team_id'], game['home_team'], game['home_score'],
                game['away_team_id'], game['away_team'], game['away_score'],
                game['neutral_site'], game['conference_game'],
                game.get('venue'), game.get('attendance')
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(games_df)} games to database")
    
    def save_team_stats_to_db(self, stats_df):
        """Save team stats DataFrame to database"""
        if stats_df.empty:
            logger.warning("No team stats to save")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert or replace team stats
        for _, stat in stats_df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO team_stats (
                    season, team_id, team_name, games, wins, losses,
                    win_pct, ppg, opp_ppg, point_diff
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                stat['season'], stat['team_id'], stat['team_name'],
                stat['games'], stat['wins'], stat['losses'],
                stat['win_pct'], stat['ppg'], stat['opp_ppg'],
                stat['point_diff']
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(stats_df)} team stats to database")
    
    def save_teams_to_db(self, teams_df):
        """Save teams DataFrame to database"""
        if teams_df.empty:
            logger.warning("No teams to save")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert or replace teams
        for _, team in teams_df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO team_info (
                    team_id, team_name, team_short_name, abbreviation, logo
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                team['team_id'], team['team_name'], team['team_short_name'],
                team['abbreviation'], team['logo']
            ))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(teams_df)} teams to database")
    
    def scrape_full_season(self, year):
        """
        Scrape complete season data (games and team stats)
        
        Args:
            year: Season year to scrape
        """
        logger.info(f"Starting full scrape for {year} season")
        
        # Scrape games for the season
        games_df = self.scrape_season(year)
        
        if not games_df.empty:
            # Save games
            self.save_games_to_db(games_df)
            
            # Calculate and save team stats from games
            stats_df = self.calculate_team_stats_from_games(games_df)
            if not stats_df.empty:
                self.save_team_stats_to_db(stats_df)
        else:
            logger.warning(f"No games found for {year} season")
        
        logger.info(f"Completed scrape for {year} season")
    
    def scrape_multiple_seasons(self, start_year, end_year):
        """
        Scrape multiple seasons
        
        Args:
            start_year: First season to scrape
            end_year: Last season to scrape (inclusive)
        """
        logger.info(f"Scraping seasons {start_year} to {end_year}")
        
        for year in range(start_year, end_year + 1):
            try:
                self.scrape_full_season(year)
                time.sleep(2)  # Delay between seasons
            except Exception as e:
                logger.error(f"Error scraping {year} season: {e}")
                continue
        
        logger.info("Completed multi-season scrape")
    
    def scrape_recent_games(self, days=7):
        """
        Scrape games from the last N days
        
        Args:
            days: Number of days to look back
        
        Returns:
            DataFrame with recent games
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        logger.info(f"Scraping games from {start_date.date()} to {end_date.date()}")
        
        games_df = self.scrape_date_range(start_date, end_date)
        
        if not games_df.empty:
            self.save_games_to_db(games_df)
        
        return games_df


def main():
    """Main execution function"""
    # Initialize scraper
    scraper = CBBScraper(db_path='data/database.db')
    
    # Initialize database
    scraper.init_database()
    
    # Get and save team information
    logger.info("Fetching team information...")
    teams_df = scraper.get_teams()
    if not teams_df.empty:
        scraper.save_teams_to_db(teams_df)
    
    # Scrape 2025 season (current season) as a test
    logger.info("Starting scrape of 2025 season...")
    scraper.scrape_full_season(2025)
    
    logger.info("Scraping complete!")


if __name__ == "__main__":
    main()
