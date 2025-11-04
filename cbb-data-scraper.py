import requests
import pandas as pd
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

class ESPNCollegeBasketballScraper:
    def __init__(self, use_google_sheets=False, credentials_file=None):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball"
        self.use_google_sheets = use_google_sheets
        self.credentials_file = credentials_file
        self.gc = None
        
        if use_google_sheets and credentials_file:
            self._setup_google_sheets()
    
    def _setup_google_sheets(self):
        """Setup Google Sheets API connection"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
        ]
        creds = Credentials.from_service_account_file(self.credentials_file, scopes=scopes)
        self.gc = gspread.authorize(creds)
        print("✓ Google Sheets connected")
    
    def get_all_teams(self, group='50'):
        """
        Get all Division I teams
        group='50' for Division I (default)
        """
        url = f"{self.base_url}/teams"
        params = {'limit': 400, 'groups': group}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            teams = []
            if 'sports' in data and len(data['sports']) > 0:
                for team in data['sports'][0]['leagues'][0]['teams']:
                    team_info = team['team']
                    teams.append({
                        'id': team_info['id'],
                        'name': team_info['displayName'],
                        'abbreviation': team_info.get('abbreviation', ''),
                        'location': team_info.get('location', ''),
                        'nickname': team_info.get('nickname', ''),
                        'logo': team_info.get('logos', [{}])[0].get('href', '') if team_info.get('logos') else ''
                    })
            
            print(f"✓ Found {len(teams)} Division I teams")
            return pd.DataFrame(teams)
            
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return pd.DataFrame()
    
    def get_team_schedule(self, team_id, season=2024):
        """
        Get full schedule for a team
        team_id: ESPN team ID
        season: year (e.g., 2024 for 2023-24 season)
        """
        url = f"{self.base_url}/teams/{team_id}/schedule"
        params = {'season': season}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            games = []
            if 'events' in data:
                for event in data['events']:
                    competition = event['competitions'][0]
                    
                    # Get teams
                    home_team = next((t for t in competition['competitors'] if t['homeAway'] == 'home'), None)
                    away_team = next((t for t in competition['competitors'] if t['homeAway'] == 'away'), None)
                    
                    if not home_team or not away_team:
                        continue
                    
                    # Determine if game is complete
                    status = event['status']['type']['name']
                    if status not in ['STATUS_FINAL', 'STATUS_POSTPONED']:
                        continue  # Skip games not yet played
                    
                    game_data = {
                        'game_id': event['id'],
                        'date': event['date'],
                        'name': event['name'],
                        'season': season,
                        'season_type': event.get('seasonType', {}).get('abbreviation', ''),
                        
                        # Home team
                        'home_team_id': home_team['team']['id'],
                        'home_team': home_team['team']['displayName'],
                        'home_score': int(home_team.get('score', 0)),
                        'home_winner': home_team.get('winner', False),
                        
                        # Away team
                        'away_team_id': away_team['team']['id'],
                        'away_team': away_team['team']['displayName'],
                        'away_score': int(away_team.get('score', 0)),
                        'away_winner': away_team.get('winner', False),
                        
                        # Game details
                        'neutral_site': competition.get('neutralSite', False),
                        'conference_game': competition.get('conferenceCompetition', False),
                        'attendance': competition.get('attendance', 0),
                        'venue': competition.get('venue', {}).get('fullName', ''),
                        
                        # Status
                        'status': status,
                        'completed': status == 'STATUS_FINAL'
                    }
                    
                    games.append(game_data)
            
            time.sleep(0.5)  # Be nice to the API
            return pd.DataFrame(games)
            
        except Exception as e:
            print(f"Error fetching schedule for team {team_id}: {e}")
            return pd.DataFrame()
    
    def get_team_stats(self, team_id, season=2024):
        """
        Get team statistics for the season
        """
        url = f"{self.base_url}/teams/{team_id}/statistics"
        params = {'season': season}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            stats = {
                'team_id': team_id,
                'season': season
            }
            
            # Parse statistics
            if 'splits' in data and 'categories' in data['splits']:
                for category in data['splits']['categories']:
                    category_name = category['name']
                    
                    for stat in category.get('stats', []):
                        stat_name = stat['name']
                        stat_value = stat.get('value', 0)
                        
                        # Create clean column name
                        col_name = f"{category_name}_{stat_name}".lower().replace(' ', '_').replace('/', '_')
                        stats[col_name] = stat_value
            
            time.sleep(0.5)
            return stats
            
        except Exception as e:
            print(f"Error fetching stats for team {team_id}: {e}")
            return {}
    
    def get_scoreboard(self, date=None, season=2024):
        """
        Get all games for a specific date
        date: 'YYYYMMDD' format (defaults to today)
        """
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        url = f"{self.base_url}/scoreboard"
        params = {'dates': date, 'limit': 100}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            games = []
            if 'events' in data:
                for event in data['events']:
                    competition = event['competitions'][0]
                    
                    home_team = next((t for t in competition['competitors'] if t['homeAway'] == 'home'), None)
                    away_team = next((t for t in competition['competitors'] if t['homeAway'] == 'away'), None)
                    
                    if home_team and away_team:
                        game_data = {
                            'game_id': event['id'],
                            'date': event['date'],
                            'name': event['name'],
                            'home_team': home_team['team']['displayName'],
                            'home_score': int(home_team.get('score', 0)),
                            'away_team': away_team['team']['displayName'],
                            'away_score': int(away_team.get('score', 0)),
                            'status': event['status']['type']['name'],
                            'neutral_site': competition.get('neutralSite', False),
                            'conference_game': competition.get('conferenceCompetition', False)
                        }
                        games.append(game_data)
            
            return pd.DataFrame(games)
            
        except Exception as e:
            print(f"Error fetching scoreboard for {date}: {e}")
            return pd.DataFrame()
    
    def get_team_roster(self, team_id):
        """Get team roster"""
        url = f"{self.base_url}/teams/{team_id}/roster"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            players = []
            if 'athletes' in data:
                for athlete in data['athletes']:
                    player_data = {
                        'player_id': athlete['id'],
                        'name': athlete['displayName'],
                        'jersey': athlete.get('jersey', ''),
                        'position': athlete.get('position', {}).get('abbreviation', ''),
                        'height': athlete.get('displayHeight', ''),
                        'weight': athlete.get('displayWeight', ''),
                        'year': athlete.get('experience', {}).get('abbreviation', '')
                    }
                    players.append(player_data)
            
            time.sleep(0.5)
            return pd.DataFrame(players)
            
        except Exception as e:
            print(f"Error fetching roster for team {team_id}: {e}")
            return pd.DataFrame()
    
    def calculate_recent_form(self, schedule_df, team_name, last_n_games=10):
        """Calculate recent form from schedule data"""
        if schedule_df.empty:
            return {}
        
        # Filter games for this team
        team_games = schedule_df[
            (schedule_df['home_team'] == team_name) | 
            (schedule_df['away_team'] == team_name)
        ].tail(last_n_games)
        
        if team_games.empty:
            return {}
        
        wins = 0
        total_pts = 0
        total_opp_pts = 0
        
        for _, game in team_games.iterrows():
            is_home = game['home_team'] == team_name
            
            if is_home:
                if game['home_winner']:
                    wins += 1
                total_pts += game['home_score']
                total_opp_pts += game['away_score']
            else:
                if game['away_winner']:
                    wins += 1
                total_pts += game['away_score']
                total_opp_pts += game['home_score']
        
        n_games = len(team_games)
        return {
            f'last_{last_n_games}_wins': wins,
            f'last_{last_n_games}_losses': n_games - wins,
            f'last_{last_n_games}_win_pct': wins / n_games if n_games > 0 else 0,
            f'last_{last_n_games}_avg_pts': total_pts / n_games if n_games > 0 else 0,
            f'last_{last_n_games}_avg_opp_pts': total_opp_pts / n_games if n_games > 0 else 0
        }
    
    def save_to_google_sheets(self, data, spreadsheet_name):
        """Save data to Google Sheets"""
        if not self.gc:
            print("Google Sheets not configured. Saving to CSV instead.")
            return self.save_to_csv(data, spreadsheet_name)
        
        try:
            # Try to open existing spreadsheet or create new one
            try:
                spreadsheet = self.gc.open(spreadsheet_name)
                print(f"✓ Opened existing spreadsheet: {spreadsheet_name}")
            except gspread.SpreadsheetNotFound:
                spreadsheet = self.gc.create(spreadsheet_name)
                print(f"✓ Created new spreadsheet: {spreadsheet_name}")
            
            # Save teams list
            if 'teams' in data and not data['teams'].empty:
                try:
                    worksheet = spreadsheet.worksheet('Teams')
                    worksheet.clear()
                except gspread.WorksheetNotFound:
                    worksheet = spreadsheet.add_worksheet(title='Teams', rows=500, cols=10)
                
                values = [data['teams'].columns.tolist()] + data['teams'].fillna('').values.tolist()
                worksheet.update(values, 'A1')
                print(f"✓ Saved {len(data['teams'])} teams to 'Teams' sheet")
            
            # Save schedules
            if 'schedules' in data and not data['schedules'].empty:
                try:
                    worksheet = spreadsheet.worksheet('Schedules')
                    worksheet.clear()
                except gspread.WorksheetNotFound:
                    worksheet = spreadsheet.add_worksheet(title='Schedules', rows=2000, cols=25)
                
                values = [data['schedules'].columns.tolist()] + data['schedules'].fillna('').values.tolist()
                worksheet.update(values, 'A1')
                print(f"✓ Saved {len(data['schedules'])} games to 'Schedules' sheet")
            
            # Save team stats
            if 'team_stats' in data and not data['team_stats'].empty:
                try:
                    worksheet = spreadsheet.worksheet('Team Stats')
                    worksheet.clear()
                except gspread.WorksheetNotFound:
                    worksheet = spreadsheet.add_worksheet(title='Team Stats', rows=500, cols=50)
                
                values = [data['team_stats'].columns.tolist()] + data['team_stats'].fillna('').values.tolist()
                worksheet.update(values, 'A1')
                print(f"✓ Saved stats for {len(data['team_stats'])} teams to 'Team Stats' sheet")
            
            print(f"\n✓ All data saved to Google Sheets!")
            print(f"View at: {spreadsheet.url}")
            return spreadsheet.url
            
        except Exception as e:
            print(f"Error saving to Google Sheets: {e}")
            print("Falling back to CSV files...")
            return self.save_to_csv(data, spreadsheet_name)
    
    def save_to_csv(self, data, prefix):
        """Fallback method to save to CSV files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for key, df in data.items():
            if not df.empty:
                filename = f'{prefix}_{key}_{timestamp}.csv'
                df.to_csv(filename, index=False)
                print(f"✓ {key.title()} saved to {filename}")
    
    def scrape_full_season(self, team_names=None, season=2024, save_name="ESPN_CBB_Data"):
        """
        Scrape complete data for teams
        team_names: list of team names to search for (e.g., ['Duke', 'North Carolina'])
                   If None, will get data for ALL Division I teams (takes a while!)
        season: season year
        """
        print(f"\n{'='*60}")
        print(f"ESPN College Basketball Data Scraper - {season} Season")
        print(f"{'='*60}\n")
        
        # Get all teams
        print("Fetching all Division I teams...")
        all_teams_df = self.get_all_teams()
        
        if all_teams_df.empty:
            print("Failed to fetch teams list")
            return {}
        
        # Filter teams if specific names provided
        if team_names:
            # Case-insensitive matching
            teams_to_scrape = all_teams_df[
                all_teams_df['name'].str.lower().isin([n.lower() for n in team_names])
            ]
            print(f"✓ Found {len(teams_to_scrape)} matching teams")
        else:
            teams_to_scrape = all_teams_df
            print(f"⚠ Scraping ALL {len(teams_to_scrape)} teams (this will take a while!)")
        
        if teams_to_scrape.empty:
            print("No teams found matching your criteria")
            return {}
        
        # Scrape data for each team
        all_schedules = []
        all_team_stats = []
        
        for i, (_, team) in enumerate(teams_to_scrape.iterrows(), 1):
            team_id = team['id']
            team_name = team['name']
            
            print(f"\n[{i}/{len(teams_to_scrape)}] Scraping {team_name}...")
            
            # Get schedule
            schedule = self.get_team_schedule(team_id, season)
            if not schedule.empty:
                all_schedules.append(schedule)
                print(f"  → Found {len(schedule)} games")
            
            # Get team stats
            stats = self.get_team_stats(team_id, season)
            if stats:
                stats['team_name'] = team_name
                
                # Add recent form
                recent_form = self.calculate_recent_form(schedule, team_name, 10)
                stats.update(recent_form)
                
                all_team_stats.append(stats)
                print(f"  → Collected team stats")
        
        # Combine all data
        schedules_df = pd.concat(all_schedules, ignore_index=True) if all_schedules else pd.DataFrame()
        team_stats_df = pd.DataFrame(all_team_stats) if all_team_stats else pd.DataFrame()
        
        data = {
            'teams': teams_to_scrape,
            'schedules': schedules_df,
            'team_stats': team_stats_df
        }
        
        print(f"\n{'='*60}")
        print("SCRAPING COMPLETE")
        print(f"{'='*60}")
        print(f"Teams: {len(teams_to_scrape)}")
        print(f"Total games: {len(schedules_df)}")
        print(f"Teams with stats: {len(team_stats_df)}")
        print(f"{'='*60}\n")
        
        # Save data
        if self.use_google_sheets:
            self.save_to_google_sheets(data, save_name)
        else:
            self.save_to_csv(data, save_name)
        
        return data


# Example usage
if __name__ == "__main__":
    # SETUP OPTIONS
    USE_GOOGLE_SHEETS = True  # Set to False to use CSV files
    CREDENTIALS_FILE = 'credentials.json'
    
    if USE_GOOGLE_SHEETS:
        scraper = ESPNCollegeBasketballScraper(
            use_google_sheets=True,
            credentials_file=CREDENTIALS_FILE
        )
    else:
        scraper = ESPNCollegeBasketballScraper(use_google_sheets=False)
    
    # OPTION 1: Scrape specific teams (RECOMMENDED)
    teams = [
        'Duke',
        'North Carolina',
        'Kansas',
        'Kentucky',
        'Villanova',
        'Gonzaga',
        'Michigan State',
        'UCLA',
        'Arizona',
        'Houston'
    ]
    
    # OPTION 2: Scrape ALL Division I teams (set teams=None)
    # WARNING: This will take 10-15 minutes!
    # teams = None
    
    season = 2024  # 2023-24 season
    
    # Run the scraper
    data = scraper.scrape_full_season(
        team_names=teams,
        season=season,
        save_name="March_Madness_ESPN_2024"
    )
    
    # Display sample data
    if data:
        print("\n=== Sample Teams Data ===")
        print(data['teams'].head())
        
        print("\n=== Sample Schedule Data ===")
        print(data['schedules'].head())
        
        print("\n=== Sample Team Stats ===")
        print(data['team_stats'].head())


"""
ESPN API FEATURES:
==================

✓ FREE - No authentication required
✓ Real-time data - Updated constantly
✓ Comprehensive stats - Game logs, team stats, rosters
✓ All Division I teams - 350+ teams available
✓ Historical data - Multiple seasons available
✓ No rate limits (but be respectful with delays)

DATA AVAILABLE:
- Game schedules and results
- Team statistics (offense, defense, misc)
- Conference standings
- Neutral site indicators
- Attendance figures
- Venue information
- Player rosters

LIMITATIONS:
- Some advanced metrics not available (efficiency ratings)
- No direct strength of schedule calculations
- Tournament data may need separate calls

TIP: You can also get data by date using:
scraper.get_scoreboard(date='20240215')  # Feb 15, 2024
"""