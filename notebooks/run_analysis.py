"""
Run exploratory data analysis on collected basketball data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import sys
sys.path.append('..')

from src.feature_engineering import CBBFeatureEngine

# Visualization settings
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')

print("="*70)
print("COLLEGE BASKETBALL DATA - EXPLORATORY ANALYSIS")
print("="*70)

# 1. Load Data
print("\n[1/5] Loading data from database...")
conn = sqlite3.connect('../data/database.db')

games_df = pd.read_sql_query('SELECT * FROM games', conn)
games_df['date'] = pd.to_datetime(games_df['date'])

teams_df = pd.read_sql_query('SELECT * FROM team_info', conn)

conn.close()

print(f"✓ Total games: {len(games_df):,}")
print(f"✓ Total teams: {len(teams_df):,}")
print(f"✓ Seasons: {sorted(games_df['season'].unique())}")
print(f"✓ Date range: {games_df['date'].min().date()} to {games_df['date'].max().date()}")

# 2. Basic Statistics
print("\n[2/5] Calculating basic statistics...")
games_df['point_diff'] = games_df['home_score'] - games_df['away_score']
games_df['total_points'] = games_df['home_score'] + games_df['away_score']
games_df['home_win'] = (games_df['home_score'] > games_df['away_score']).astype(int)

print(f"✓ Average home score: {games_df['home_score'].mean():.1f}")
print(f"✓ Average away score: {games_df['away_score'].mean():.1f}")
print(f"✓ Average total points: {games_df['total_points'].mean():.1f}")
print(f"✓ Average point differential: {abs(games_df['point_diff']).mean():.1f}")
print(f"✓ Home win percentage: {games_df['home_win'].mean()*100:.1f}%")

# 3. Team Analysis
print("\n[3/5] Analyzing team performance...")
engine = CBBFeatureEngine(db_path='../data/database.db')
team_stats = engine.calculate_basic_stats(games_df)

print(f"✓ Calculated stats for {len(team_stats)} teams")
print("\nTop 10 teams by point differential:")
top_teams = team_stats.nlargest(10, 'point_diff')[['team_name', 'wins', 'losses', 'ppg', 'opp_ppg', 'point_diff']]
print(top_teams.to_string(index=False))

print("\nBottom 5 teams by point differential:")
bottom_teams = team_stats.nsmallest(5, 'point_diff')[['team_name', 'wins', 'losses', 'ppg', 'opp_ppg', 'point_diff']]
print(bottom_teams.to_string(index=False))

# 4. Feature Analysis
print("\n[4/5] Analyzing engineered features...")
features_df = pd.read_csv('../data/processed/features.csv')
print(f"✓ Features created for {len(features_df)} games")

# Correlation with target
numeric_cols = features_df.select_dtypes(include=[np.number]).columns
exclude = ['game_id', 'season', 'home_team_id', 'away_team_id']
numeric_cols = [col for col in numeric_cols if col not in exclude]

if 'point_differential' in features_df.columns:
    correlations = features_df[numeric_cols].corr()['point_differential'].sort_values(ascending=False)
    print("\nTop 5 features correlated with point differential:")
    for i, (feature, corr) in enumerate(correlations.head(6).items(), 1):
        if feature != 'point_differential':
            print(f"  {i}. {feature}: {corr:.3f}")

# 5. Create Visualizations
print("\n[5/5] Creating visualizations...")
print("Generating plots (this may take a moment)...")

fig = plt.figure(figsize=(16, 12))

# Score distributions
ax1 = plt.subplot(3, 3, 1)
ax1.scatter(games_df['home_score'], games_df['away_score'], alpha=0.3, s=10)
ax1.plot([40, 120], [40, 120], 'r--', label='Equal scores')
ax1.set_xlabel('Home Score')
ax1.set_ylabel('Away Score')
ax1.set_title('Home vs Away Scores')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Point Differential Distribution
ax2 = plt.subplot(3, 3, 2)
ax2.hist(games_df['point_diff'], bins=50, edgecolor='black', alpha=0.7)
ax2.axvline(x=0, color='r', linestyle='--', linewidth=2, label='Tied')
ax2.set_xlabel('Point Differential (Home - Away)')
ax2.set_ylabel('Frequency')
ax2.set_title('Point Differential Distribution')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Total Points Distribution
ax3 = plt.subplot(3, 3, 3)
ax3.hist(games_df['total_points'], bins=30, edgecolor='black', color='green', alpha=0.7)
ax3.set_xlabel('Total Points')
ax3.set_ylabel('Frequency')
ax3.set_title('Total Points Distribution')
ax3.grid(True, alpha=0.3)

# Games by Season
ax4 = plt.subplot(3, 3, 4)
season_counts = games_df.groupby('season').size()
ax4.bar(season_counts.index, season_counts.values, color='steelblue')
ax4.set_xlabel('Season')
ax4.set_ylabel('Number of Games')
ax4.set_title('Games by Season')
ax4.grid(True, alpha=0.3, axis='y')

# PPG vs Opp PPG
ax5 = plt.subplot(3, 3, 5)
ax5.scatter(team_stats['ppg'], team_stats['opp_ppg'], 
            s=team_stats['games']*20, alpha=0.5, c=team_stats['win_pct'], cmap='RdYlGn')
ax5.plot([50, 90], [50, 90], 'r--', label='Equal')
ax5.set_xlabel('Points Per Game')
ax5.set_ylabel('Opponent Points Per Game')
ax5.set_title('Team Offensive vs Defensive Performance')
ax5.legend()
ax5.grid(True, alpha=0.3)
cbar = plt.colorbar(ax5.collections[0], ax=ax5)
cbar.set_label('Win %')

# Win % vs Point Differential
ax6 = plt.subplot(3, 3, 6)
ax6.scatter(team_stats['point_diff'], team_stats['win_pct'], alpha=0.6, s=50)
ax6.set_xlabel('Average Point Differential')
ax6.set_ylabel('Win Percentage')
ax6.set_title('Point Differential vs Win Percentage')
ax6.grid(True, alpha=0.3)

# Home/Away Score Distribution
ax7 = plt.subplot(3, 3, 7)
ax7.hist(games_df['home_score'], bins=30, alpha=0.5, label='Home', color='blue')
ax7.hist(games_df['away_score'], bins=30, alpha=0.5, label='Away', color='red')
ax7.set_xlabel('Score')
ax7.set_ylabel('Frequency')
ax7.set_title('Home vs Away Score Distribution')
ax7.legend()
ax7.grid(True, alpha=0.3)

# Win Distribution
ax8 = plt.subplot(3, 3, 8)
win_counts = games_df['home_win'].value_counts()
ax8.bar(['Away Win', 'Home Win'], [win_counts[0], win_counts[1]], color=['red', 'blue'], alpha=0.7)
ax8.set_ylabel('Number of Games')
ax8.set_title('Home vs Away Wins')
ax8.grid(True, alpha=0.3, axis='y')
for i, v in enumerate([win_counts[0], win_counts[1]]):
    ax8.text(i, v + 10, f'{v} ({v/len(games_df)*100:.1f}%)', ha='center')

# Games over time
ax9 = plt.subplot(3, 3, 9)
games_by_date = games_df.groupby(games_df['date'].dt.date).size()
ax9.plot(games_by_date.index, games_by_date.values, alpha=0.7)
ax9.set_xlabel('Date')
ax9.set_ylabel('Number of Games')
ax9.set_title('Games Over Time')
ax9.grid(True, alpha=0.3)
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('../data/processed/exploratory_analysis.png', dpi=150, bbox_inches='tight')
print("✓ Visualizations saved to: data/processed/exploratory_analysis.png")

print("\n" + "="*70)
print("ANALYSIS COMPLETE!")
print("="*70)
print(f"\nKey Insights:")
print(f"1. Home court advantage: {(games_df['home_win'].mean() - 0.5) * 100:.1f}% boost")
print(f"2. Average margin of victory: {abs(games_df['point_diff']).mean():.1f} points")
print(f"3. Typical total score: {games_df['total_points'].mean():.1f} points")
print(f"4. Games collected: {len(games_df)} across {len(games_df['season'].unique())} season(s)")
print(f"5. Teams analyzed: {len(team_stats)}")

print("\nTo view the visualization: open data/processed/exploratory_analysis.png")
print("To run full Jupyter notebook: jupyter lab notebooks/01_exploratory_analysis.ipynb")
