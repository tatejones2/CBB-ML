"""
Feature Engineering Module for College Basketball ML
Creates features from raw game data for model training
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CBBFeatureEngine:
    """Feature engineering for college basketball predictions"""
    
    def __init__(self, db_path='data/database.db'):
        """Initialize feature engine with database connection"""
        self.db_path = db_path
        
    def load_games(self, season=None):
        """
        Load games from database
        
        Args:
            season: Optional season filter
            
        Returns:
            DataFrame with games
        """
        conn = sqlite3.connect(self.db_path)
        
        if season:
            query = "SELECT * FROM games WHERE season = ? ORDER BY date"
            games_df = pd.read_sql_query(query, conn, params=(season,))
        else:
            query = "SELECT * FROM games ORDER BY date"
            games_df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        # Convert date to datetime
        games_df['date'] = pd.to_datetime(games_df['date'])
        
        logger.info(f"Loaded {len(games_df)} games")
        return games_df
    
    def calculate_basic_stats(self, games_df):
        """
        Calculate basic team statistics from games
        
        Args:
            games_df: DataFrame with game data
            
        Returns:
            DataFrame with team statistics
        """
        stats_list = []
        
        # Get unique teams
        home_teams = set(games_df['home_team_id'].unique())
        away_teams = set(games_df['away_team_id'].unique())
        all_teams = home_teams.union(away_teams)
        
        for team_id in all_teams:
            # Get all games for this team
            home_games = games_df[games_df['home_team_id'] == team_id].copy()
            away_games = games_df[games_df['away_team_id'] == team_id].copy()
            
            if len(home_games) == 0 and len(away_games) == 0:
                continue
            
            # Get team name
            if len(home_games) > 0:
                team_name = home_games.iloc[0]['home_team']
            else:
                team_name = away_games.iloc[0]['away_team']
            
            # Calculate statistics
            total_games = len(home_games) + len(away_games)
            
            # Points scored
            home_points = home_games['home_score'].sum()
            away_points = away_games['away_score'].sum()
            total_points = home_points + away_points
            ppg = total_points / total_games if total_games > 0 else 0
            
            # Points allowed
            home_allowed = home_games['away_score'].sum()
            away_allowed = away_games['home_score'].sum()
            total_allowed = home_allowed + away_allowed
            opp_ppg = total_allowed / total_games if total_games > 0 else 0
            
            # Wins/Losses
            home_wins = (home_games['home_score'] > home_games['away_score']).sum()
            away_wins = (away_games['away_score'] > away_games['home_score']).sum()
            total_wins = home_wins + away_wins
            total_losses = total_games - total_wins
            win_pct = total_wins / total_games if total_games > 0 else 0
            
            stats_list.append({
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
        
        stats_df = pd.DataFrame(stats_list)
        logger.info(f"Calculated stats for {len(stats_df)} teams")
        return stats_df
    
    def calculate_rolling_stats(self, games_df, window=5):
        """
        Calculate rolling statistics for each team
        
        Args:
            games_df: DataFrame with game data
            window: Number of games to look back
            
        Returns:
            DataFrame with rolling stats
        """
        games_df = games_df.sort_values('date').copy()
        rolling_stats = []
        
        # Get unique teams
        all_teams = set(games_df['home_team_id'].unique()).union(
            set(games_df['away_team_id'].unique())
        )
        
        for team_id in all_teams:
            # Get team's game history
            team_games = []
            
            for idx, game in games_df.iterrows():
                is_home = game['home_team_id'] == team_id
                is_away = game['away_team_id'] == team_id
                
                if is_home or is_away:
                    points_scored = game['home_score'] if is_home else game['away_score']
                    points_allowed = game['away_score'] if is_home else game['home_score']
                    won = points_scored > points_allowed
                    
                    team_games.append({
                        'game_id': game['game_id'],
                        'date': game['date'],
                        'team_id': team_id,
                        'points_scored': points_scored,
                        'points_allowed': points_allowed,
                        'won': won,
                        'is_home': is_home,
                    })
            
            # Calculate rolling stats
            team_df = pd.DataFrame(team_games)
            if len(team_df) == 0:
                continue
            
            team_df = team_df.sort_values('date')
            
            # Rolling averages
            team_df[f'rolling_ppg_{window}'] = team_df['points_scored'].rolling(
                window=window, min_periods=1
            ).mean()
            
            team_df[f'rolling_opp_ppg_{window}'] = team_df['points_allowed'].rolling(
                window=window, min_periods=1
            ).mean()
            
            team_df[f'rolling_win_pct_{window}'] = team_df['won'].rolling(
                window=window, min_periods=1
            ).mean()
            
            rolling_stats.append(team_df)
        
        if rolling_stats:
            all_rolling = pd.concat(rolling_stats, ignore_index=True)
            logger.info(f"Calculated rolling stats with window={window}")
            return all_rolling
        
        return pd.DataFrame()
    
    def create_matchup_features(self, games_df, rolling_stats_df, window=5):
        """
        Create features for game predictions based on matchups
        
        Args:
            games_df: DataFrame with game data
            rolling_stats_df: DataFrame with rolling statistics
            window: Rolling window size
            
        Returns:
            DataFrame with matchup features
        """
        features = []
        
        for idx, game in games_df.iterrows():
            # Get rolling stats for both teams UP TO (but not including) this game
            home_stats = rolling_stats_df[
                (rolling_stats_df['team_id'] == game['home_team_id']) &
                (rolling_stats_df['date'] < game['date'])
            ].sort_values('date').tail(1)
            
            away_stats = rolling_stats_df[
                (rolling_stats_df['team_id'] == game['away_team_id']) &
                (rolling_stats_df['date'] < game['date'])
            ].sort_values('date').tail(1)
            
            if home_stats.empty or away_stats.empty:
                continue
            
            home_row = home_stats.iloc[0]
            away_row = away_stats.iloc[0]
            
            # Create feature vector
            feature_dict = {
                'game_id': game['game_id'],
                'date': game['date'],
                'season': game['season'],
                'home_team_id': game['home_team_id'],
                'away_team_id': game['away_team_id'],
                
                # Home team features
                f'home_ppg_{window}': home_row[f'rolling_ppg_{window}'],
                f'home_opp_ppg_{window}': home_row[f'rolling_opp_ppg_{window}'],
                f'home_win_pct_{window}': home_row[f'rolling_win_pct_{window}'],
                
                # Away team features
                f'away_ppg_{window}': away_row[f'rolling_ppg_{window}'],
                f'away_opp_ppg_{window}': away_row[f'rolling_opp_ppg_{window}'],
                f'away_win_pct_{window}': away_row[f'rolling_win_pct_{window}'],
                
                # Differential features
                f'ppg_diff_{window}': home_row[f'rolling_ppg_{window}'] - away_row[f'rolling_ppg_{window}'],
                f'def_diff_{window}': away_row[f'rolling_opp_ppg_{window}'] - home_row[f'rolling_opp_ppg_{window}'],
                f'win_pct_diff_{window}': home_row[f'rolling_win_pct_{window}'] - away_row[f'rolling_win_pct_{window}'],
                
                # Target variables
                'home_score': game['home_score'],
                'away_score': game['away_score'],
                'home_win': 1 if game['home_score'] > game['away_score'] else 0,
                'point_differential': game['home_score'] - game['away_score'],
            }
            
            features.append(feature_dict)
        
        features_df = pd.DataFrame(features)
        logger.info(f"Created {len(features_df)} matchup features")
        return features_df
    
    def engineer_all_features(self, season=None, rolling_windows=[5, 10]):
        """
        Run complete feature engineering pipeline
        
        Args:
            season: Optional season filter
            rolling_windows: List of rolling window sizes
            
        Returns:
            Dictionary with features DataFrames
        """
        logger.info("Starting feature engineering pipeline...")
        
        # Load games
        games_df = self.load_games(season)
        
        if len(games_df) == 0:
            logger.warning("No games found!")
            return None
        
        # Calculate basic stats
        basic_stats = self.calculate_basic_stats(games_df)
        
        # Calculate rolling stats for each window
        all_features = {}
        
        for window in rolling_windows:
            logger.info(f"Processing rolling window: {window} games")
            rolling_stats = self.calculate_rolling_stats(games_df, window=window)
            
            if not rolling_stats.empty:
                matchup_features = self.create_matchup_features(
                    games_df, rolling_stats, window=window
                )
                all_features[f'window_{window}'] = matchup_features
        
        return {
            'basic_stats': basic_stats,
            'features': all_features,
            'games': games_df,
        }
    
    def save_features(self, features_dict, output_path='data/processed/features.csv'):
        """
        Save features to CSV
        
        Args:
            features_dict: Dictionary with features
            output_path: Path to save CSV
        """
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the first window's features (usually most important)
        if 'features' in features_dict and features_dict['features']:
            first_window = list(features_dict['features'].keys())[0]
            features_df = features_dict['features'][first_window]
            features_df.to_csv(output_path, index=False)
            logger.info(f"Saved features to {output_path}")
            
            # Also save basic stats
            if 'basic_stats' in features_dict:
                stats_path = output_path.replace('features.csv', 'team_stats.csv')
                features_dict['basic_stats'].to_csv(stats_path, index=False)
                logger.info(f"Saved team stats to {stats_path}")


def main():
    """Example usage"""
    engine = CBBFeatureEngine()
    
    # Engineer features
    results = engine.engineer_all_features(rolling_windows=[5, 10])
    
    if results:
        print("\n" + "="*70)
        print("FEATURE ENGINEERING RESULTS")
        print("="*70)
        
        print(f"\nBasic Stats: {len(results['basic_stats'])} teams")
        print(results['basic_stats'].head())
        
        for window_name, features_df in results['features'].items():
            print(f"\n{window_name}: {len(features_df)} games with features")
            print(features_df.head())
        
        # Save features
        engine.save_features(results)
        print("\n✓ Features saved to data/processed/")


if __name__ == "__main__":
    main()
