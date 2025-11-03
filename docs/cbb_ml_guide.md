# College Basketball ML Prediction System - Complete Guide

## Overview

This guide provides a comprehensive roadmap for building a machine learning system to predict college basketball game outcomes. College basketball is ideal for ML prediction due to the large volume of games (350+ teams, 30+ games each season), providing substantial training data.

---

## Phase 1: Setup & Data Collection (Weeks 1-2)

### 1.1 Development Environment

**Required Software:**
- Python 3.9+
- pandas, numpy, scikit-learn, matplotlib, seaborn
- requests (for API calls)
- sqlite3 (data storage)

### 1.2 Primary Data Sources

**Best Free Source: Sports Reference (College Basketball Reference)**
- Historical game results back to 2000s
- Team statistics (offensive/defensive efficiency)
- Player statistics
- Can be scraped (respectfully) or use their Stathead service

**Alternative/Supplementary Sources:**
- ESPN API (unofficial but accessible)
- KenPom.com (paid subscription but gold standard for analytics)
- Barttorvik.com (free advanced metrics)
- NCAA.com (official stats)

### 1.3 What Data to Collect

**Game-Level Data:**
- Date, home team, away team, final scores
- Location (neutral site games matter in March Madness)
- Conference game indicator
- Overtime games

**Team Statistics (per game averages):**
- Points scored/allowed
- Field goal %, 3-point %, free throw %
- Rebounds (offensive/defensive)
- Assists, turnovers, steals, blocks
- Pace (possessions per game)
- Efficiency metrics (points per possession)

**Advanced Metrics:**
- Adjusted offensive/defensive efficiency (opponent-adjusted)
- Strength of schedule
- Recent form (last 5-10 games)

---

## Phase 2: Data Pipeline (Week 2-3)

### 2.1 Build Web Scraper (if using Sports Reference)

**Pseudo-structure:**
- Scrape season schedules for all teams
- Collect box scores for each game
- Calculate rolling statistics
- Store in SQLite database

### 2.2 Database Schema

**Recommended Tables:**
- **games**: game_id, date, home_team, away_team, home_score, away_score, neutral_site
- **team_stats**: team_id, date, ppg, opp_ppg, fg_pct, 3p_pct, etc.
- **team_info**: team_id, conference, division

### 2.3 Historical Data Collection

- Start with 5-10 seasons (2015-2024 recommended)
- More recent seasons weighted more heavily
- Include tournament games but flag them (different dynamics)

---

## Phase 3: Feature Engineering (Week 3-5)

### 3.1 Basic Features

**Team Strength Metrics:**
- Offensive efficiency (points per 100 possessions)
- Defensive efficiency (points allowed per 100 possessions)
- Net efficiency (offensive - defensive)
- Tempo/pace adjusted stats

**Matchup Features:**
- Efficiency differential (home off. eff. - away def. eff.)
- Style contrast (high pace vs. slow pace teams)
- Home court advantage (historically ~3-4 points in college basketball)

### 3.2 Rolling/Recent Performance

- Last 5 games: average points, efficiency
- Last 10 games: trend (improving or declining)
- Season-to-date averages
- Conference record vs. non-conference

### 3.3 Contextual Features

- Days rest since last game
- Back-to-back games indicator
- Travel distance (home team advantage varies)
- Time of season (early vs. late season form)
- Rivalry game indicator

### 3.4 Opponent-Adjusted Metrics

- Don't just use raw PPG - adjust for opponent strength
- Calculate "strength of schedule" for each team
- Weight recent games against quality opponents more

### 3.5 Feature Examples

**For a game: Duke vs. UNC**

Features might include:
- Duke offensive efficiency (last 10 games)
- Duke defensive efficiency (last 10 games)
- UNC offensive efficiency (last 10 games)
- UNC defensive efficiency (last 10 games)
- Duke home court advantage (~4 pts)
- Days rest for each team
- Duke net efficiency vs. top 50 teams
- Head-to-head history
- Pace differential
- Rebound margin differential

---

## Phase 4: Model Development (Week 5-8)

### 4.1 Target Variable Options

**Choose one to start:**
1. **Point spread** (home team margin of victory) - most common
2. **Total points** (over/under)
3. **Win probability** (classification)

**Recommendation:** Start with **point spread** - it's continuous and captures game dynamics well.

### 4.2 Train/Test Split Strategy

**Critical for sports: Time-series split**

```
Training: 2015-2022 seasons
Validation: 2022-2023 season
Test: 2023-2024 season

Never train on future data!
```

### 4.3 Baseline Models

**Simple baseline to beat:**
- Home team wins by average home court advantage (~3.5 points)
- Calculate average margin by efficiency differential

### 4.4 Machine Learning Models

**Start with:**
1. **Linear Regression** - simple, interpretable
2. **Ridge/Lasso Regression** - handles multicollinearity
3. **Random Forest** - captures non-linear relationships
4. **Gradient Boosting (XGBoost/LightGBM)** - usually best performer

**Model Training Approach:**
```python
# Simplified workflow:
1. Load features for all games
2. Split by season (time-series)
3. Train model on historical seasons
4. Predict validation season
5. Tune hyperparameters
6. Test on final holdout season
```

### 4.5 Key Metrics

**For point spread prediction:**
- **Mean Absolute Error (MAE)** - average points off
- **Root Mean Squared Error (RMSE)** - penalizes big misses
- **Accuracy vs. Vegas lines** - can you beat the spread?
- **Calibration** - are 60% win probability predictions right 60% of the time?

**Good Performance Benchmarks:**
- MAE under 10 points is decent
- MAE under 8 points is good
- Beating Vegas lines >53% is extremely good (they're at ~70% accuracy)

---

## Phase 5: Evaluation & Iteration (Week 8-10)

### 5.1 Error Analysis

**Look for patterns:**
- Does model struggle with blowouts vs. close games?
- Performance in conference vs. non-conference games?
- Early season vs. late season accuracy?
- Favorites vs. underdogs?
- High-scoring vs. low-scoring games?

### 5.2 Common Issues

**Overfitting Indicators:**
- Great training accuracy, poor test accuracy
- Model too complex for amount of data
- Fix: Regularization, fewer features, more data

**Data Leakage:**
- Using future information (season averages that include the game being predicted)
- Fix: Only use stats from games BEFORE the predicted game

**Insufficient Feature Engineering:**
- Model plateaus in performance
- Fix: Add opponent-adjusted metrics, interaction terms

### 5.3 Refinement Loop

1. Identify weakest predictions
2. Hypothesize why (missing feature, wrong model, bad data)
3. Test hypothesis
4. Implement fix
5. Re-evaluate
6. Repeat

---

## Phase 6: Advanced Features (Week 10-12)

### 6.1 Player-Level Data

- Injury reports (major impact)
- Key player usage rates
- Depth of roster
- Freshman vs. senior heavy teams

### 6.2 Situational Factors

- "Trap game" indicators (looking ahead to big opponent)
- Rivalry intensity
- Conference tournament implications
- NCAA tournament resume building

### 6.3 Market Data

- Opening betting lines (Vegas has information too)
- Line movement (sharp money vs. public money)
- Historical line vs. result analysis

---

## Phase 7: Production System (Week 12+)

### 7.1 Daily Update Pipeline

**Automated Workflow:**
1. Scrape previous day's results
2. Update team statistics
3. Recalculate rolling averages
4. Generate predictions for upcoming games
5. Output to CSV or dashboard

### 7.2 Prediction Output Format

```
Game: Duke vs UNC
Predicted Spread: Duke -6.5
Confidence: 65%
Key Factors: Duke superior defense, home court
Model Agreement: 4/5 models predict Duke cover
```

### 7.3 Performance Tracking

- Log every prediction with timestamp
- Track accuracy over time
- Calculate ROI if hypothetically betting
- Monitor for model drift

---

## Phase 8: March Madness Special (Optional)

### 8.1 Tournament-Specific Challenges

- Neutral sites (no home court advantage)
- Single elimination (no bad game forgiveness)
- Seeding matters (rest, momentum)
- Recency bias (conference tournament form)

### 8.2 Bracket Prediction

- Simulate tournament thousands of times
- Calculate upset probability
- Balance high-probability picks vs. differentiated bracket

---

## Recommended Starting Point

### Week 1 Concrete Tasks:

1. Set up Python environment
2. Choose Sports Reference as data source
3. Write script to scrape 2023-2024 season game results
4. Store in SQLite database
5. Calculate basic team statistics (PPG, opponent PPG)
6. Create train/test split
7. Build simple linear regression predicting point spread
8. Calculate baseline MAE

**This gives you:**
- Working data pipeline
- Basic model
- Benchmark to improve upon

---

## Key Principles Throughout

- **Start simple, add complexity gradually** - a working simple model beats a broken complex one
- **Document everything** - your decisions, failed experiments, successful features
- **Version your data and models** - track what data/code produced which results
- **Be skeptical of good results** - always check for data leakage
- **Compare to benchmarks** - Vegas lines are incredibly accurate; beating them is very hard
- **Use time-series splits** - never train on future data when testing historical performance

---

## Project Structure

```
college-basketball-ml/
│
├── data/
│   ├── raw/              # Scraped data
│   ├── processed/        # Cleaned and featured data
│   └── database.db       # SQLite database
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_training.ipynb
│
├── scripts/
│   ├── scrape_data.py
│   ├── process_data.py
│   ├── train_model.py
│   └── make_predictions.py
│
├── models/
│   └── saved_models/     # Trained model files
│
├── results/
│   ├── predictions/      # Daily predictions
│   └── performance/      # Accuracy tracking
│
└── README.md
```

---

## Resources

**Learning Materials:**
- "Basketball on Paper" by Dean Oliver (analytics fundamentals)
- KenPom.com blog posts (understanding efficiency metrics)
- Kaggle March Madness competitions (see winning approaches)

**Technical Resources:**
- Scikit-learn documentation
- XGBoost documentation
- Pandas documentation for data manipulation

**Domain Knowledge:**
- Follow college basketball analytics Twitter community
- Read team-specific analytics blogs
- Understand conference strength dynamics

---

## Next Steps

Once you have a working baseline system:
1. Experiment with different feature combinations
2. Try ensemble methods (combining multiple models)
3. Add player-level data for injury adjustments
4. Incorporate betting market data
5. Build visualization dashboard for predictions
6. Test live predictions during current season
7. Document what works and what doesn't

Good luck with your project!