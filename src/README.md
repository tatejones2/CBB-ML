# Source Code Documentation

This directory contains the core Python modules for the CBB ML project.

## Modules

### `scraper.py`
ESPN API scraper for collecting college basketball game data.

**Key Classes:**
- `CBBScraper`: Main scraper class with methods for:
  - Fetching team information
  - Scraping games by date/date range
  - Scraping full seasons
  - Database management

**Usage:**
```python
from src.scraper import CBBScraper

scraper = CBBScraper(db_path='data/database.db')
scraper.init_database()
scraper.scrape_full_season(2025)
```

### `feature_engineering.py`
Feature engineering pipeline for creating ML features from raw game data.

**Key Classes:**
- `CBBFeatureEngine`: Feature engineering engine with methods for:
  - Loading games from database
  - Calculating basic team statistics
  - Computing rolling averages (last N games)
  - Creating matchup features for prediction

**Features Created:**
- Basic stats: PPG, Opp PPG, Win %, Point Differential
- Rolling stats: Performance over last 5/10 games
- Matchup features: Team A vs Team B comparisons
- Differential features: Offensive/defensive advantages

**Usage:**
```python
from src.feature_engineering import CBBFeatureEngine

engine = CBBFeatureEngine()
results = engine.engineer_all_features(rolling_windows=[5, 10])
engine.save_features(results)
```

### `model_training.py`
Model training and evaluation pipeline.

**Key Classes:**
- `CBBModelTrainer`: Model training manager with methods for:
  - Loading engineered features
  - Preparing train/test splits (time-series aware)
  - Training multiple models
  - Evaluating and comparing performance

**Models Supported:**
- Baseline (predict mean)
- Linear Regression
- Ridge Regression
- Random Forest
- (Future: XGBoost, LightGBM, Neural Networks)

**Usage:**
```python
from src.model_training import CBBModelTrainer

trainer = CBBModelTrainer()
results = trainer.train_all_models()
trainer.print_results_summary()
trainer.save_models()
```

## Workflow

### 1. Data Collection
```bash
python scripts/run_scraper.py
```

### 2. Feature Engineering
```bash
python src/feature_engineering.py
```

### 3. Model Training
```bash
python src/model_training.py
```

### 4. Analysis
```bash
jupyter notebook notebooks/01_exploratory_analysis.ipynb
```

## Key Concepts

### Time-Series Splits
- Always use chronological splits for train/test
- Never train on future data
- Prevents data leakage and overfitting

### Rolling Statistics
- Calculate team performance over recent games
- More relevant than season-long averages
- Captures momentum and current form

### Feature Importance
Most predictive features typically:
- Point differential (offensive - defensive)
- Recent win percentage
- Offensive efficiency vs opponent's defense
- Home court advantage

## Next Steps

1. **Add Advanced Features:**
   - Opponent-adjusted metrics
   - Strength of schedule
   - Rest days between games
   - Travel distance

2. **Improve Models:**
   - Gradient boosting (XGBoost/LightGBM)
   - Hyperparameter tuning
   - Ensemble methods
   - Deep learning models

3. **Production Pipeline:**
   - Daily prediction updates
   - Performance tracking
   - Model retraining automation
   - API for predictions
