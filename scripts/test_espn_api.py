"""
Quick test script to verify ESPN API access
"""

import requests
from datetime import datetime

def test_espn_api():
    """Test if we can access ESPN's API"""
    
    print("=" * 60)
    print("Testing ESPN College Basketball API")
    print("=" * 60)
    
    # Test 1: Get scoreboard for today
    print("\n[Test 1] Fetching today's scoreboard...")
    today = datetime.now().strftime('%Y%m%d')
    scoreboard_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
    
    try:
        response = requests.get(scoreboard_url, params={'dates': today}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        events = data.get('events', [])
        print(f"✓ Success! Found {len(events)} games for {today}")
        
        if events:
            print("\nSample game:")
            event = events[0]
            competitors = event['competitions'][0]['competitors']
            home = next((c for c in competitors if c['homeAway'] == 'home'), None)
            away = next((c for c in competitors if c['homeAway'] == 'away'), None)
            
            if home and away:
                print(f"  {away['team']['displayName']} vs {home['team']['displayName']}")
                print(f"  Status: {event['status']['type']['description']}")
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 2: Get teams
    print("\n[Test 2] Fetching teams list...")
    teams_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams"
    
    try:
        response = requests.get(teams_url, params={'limit': 400}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        sports_data = data['sports'][0] if data.get('sports') else {}
        leagues = sports_data.get('leagues', [])
        
        team_count = 0
        for league in leagues:
            team_count += len(league.get('teams', []))
        
        print(f"✓ Success! Found {team_count} teams")
        
        if team_count > 0:
            # Show sample team
            first_team = leagues[0]['teams'][0]['team']
            print(f"\nSample team:")
            print(f"  Name: {first_team['displayName']}")
            print(f"  ID: {first_team['id']}")
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 3: Get a specific date with games (use a past date)
    print("\n[Test 3] Fetching games from January 15, 2024...")
    test_date = "20240115"
    
    try:
        response = requests.get(scoreboard_url, params={'dates': test_date}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        events = data.get('events', [])
        completed = sum(1 for e in events if e['status']['type'].get('completed') == True)
        
        print(f"✓ Success! Found {len(events)} games, {completed} completed")
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed! ESPN API is accessible.")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    test_espn_api()
