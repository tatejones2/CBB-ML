#!/bin/bash
# Quick status check for scraper progress

cd /home/tatejones/CBB-ML-clean
source venv/bin/activate

echo "=========================================="
echo "SCRAPER PROGRESS CHECK"
echo "=========================================="
echo ""

# Check if scraper is running
if pgrep -f "run_scraper.py" > /dev/null; then
    echo "✓ Scraper is running (PID: $(pgrep -f run_scraper.py))"
else
    echo "✗ Scraper is not running"
fi

echo ""

# Query database
python << EOF
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/database.db')

# Get counts
games = pd.read_sql('SELECT COUNT(*) as cnt FROM games', conn)['cnt'][0]
teams = pd.read_sql('SELECT COUNT(*) as cnt FROM team_info', conn)['cnt'][0]
stats = pd.read_sql('SELECT COUNT(*) as cnt FROM team_stats', conn)['cnt'][0]

print(f"📊 Current Status:")
print(f"  Total games:      {games:,}")
print(f"  Team info:        {teams:,}")
print(f"  Team stats:       {stats:,}")
print()

# Games by season
seasons_df = pd.read_sql('SELECT season, COUNT(*) as games FROM games GROUP BY season ORDER BY season', conn)
if not seasons_df.empty:
    print(f"🏀 Games by Season:")
    for _, row in seasons_df.iterrows():
        print(f"  {row['season']}: {row['games']:,} games")
else:
    print("  No games collected yet")

conn.close()
EOF

echo ""
echo "To monitor continuously: python scripts/monitor_progress.py"
echo "To view full database: python scripts/inspect_data.py"
