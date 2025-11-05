# College Basketball ML Prediction System

## Project Overview

This project aims to build a machine learning system to predict college basketball game outcomes, scores, and performances.

## Project Status

🚧 **In Development** - Basic project structure setup complete

## Getting Started

### Prerequisites

- Python 3.9+
- pip or conda package manager

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
# College Basketball ML Prediction System

A machine learning system for predicting college basketball game outcomes using data from ESPN's API.

## Overview

This project implements a complete pipeline for:
- Collecting college basketball game data
- Engineering features from historical statistics
- Training ML models to predict game outcomes
- Evaluating model performance

## Project Structure

```
CBB-ML-clean/
├── data/
│   ├── raw/              # Raw scraped data
│   ├── processed/        # Cleaned and featured data
│   └── database.db       # SQLite database with games and stats
├── src/
│   └── scraper.py        # ESPN API scraper
├── scripts/
│   ├── run_scraper.py    # Main scraping script
│   ├── test_scraper.py   # Test scraper functionality
│   ├── test_espn_api.py  # Test ESPN API access
│   └── inspect_data.py   # Database inspection tool
├── notebooks/            # Jupyter notebooks for analysis
├── models/               # Trained model files
├── docs/
│   └── cbb_ml_guide.md   # Complete implementation guide
└── requirements.txt      # Python dependencies
```

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/tatejones2/CBB-ML.git
cd CBB-ML-clean
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Data Collection

#### Test ESPN API Access

```bash
python scripts/test_espn_api.py
```

#### Test Scraper

```bash
python scripts/test_scraper.py
```

#### Scrape Data

Run the interactive scraper:

```bash
python scripts/run_scraper.py
```

Options:
1. Scrape single season (2025 - current)
2. Scrape multiple seasons (2021-2025)
3. Scrape full historical data (2015-2025)
4. Scrape recent games (last 7 days)

#### Inspect Database

View scraped data:

```bash
python scripts/inspect_data.py
```

Export to CSV:

```bash
python scripts/inspect_data.py --export
```

### Data Structure

#### Games Table
- `game_id`: Unique game identifier
- `date`: Game date and time
- `season`: Season year
- `home_team_id`, `away_team_id`: Team IDs
- `home_team`, `away_team`: Team names
- `home_score`, `away_score`: Final scores
- `neutral_site`: Whether game is at neutral location
- `conference_game`: Whether it's a conference game
- `venue`: Venue name
- `attendance`: Attendance count

#### Team Stats Table
- `season`: Season year
- `team_id`, `team_name`: Team identification
- `games`, `wins`, `losses`: Record
- `win_pct`: Win percentage
- `ppg`: Points per game
- `opp_ppg`: Opponent points per game
- `point_diff`: Average point differential

#### Team Info Table
- `team_id`: ESPN team ID
- `team_name`: Full team name
- `team_short_name`: Short name
- `abbreviation`: Team abbreviation
- `logo`: Logo URL

## Development Roadmap

Following the guide in `docs/cbb_ml_guide.md`:

- [x] **Phase 1**: Setup & Data Collection
  - [x] Environment setup
  - [x] ESPN API scraper
  - [x] Database schema
  - [x] Historical data collection

- [ ] **Phase 2**: Data Pipeline
  - [ ] Data cleaning
  - [ ] Rolling statistics calculation
  - [ ] Data validation

- [ ] **Phase 3**: Feature Engineering
  - [ ] Basic team metrics
  - [ ] Matchup features
  - [ ] Rolling performance metrics
  - [ ] Contextual features

- [ ] **Phase 4**: Model Development
  - [ ] Baseline models
  - [ ] Linear regression
  - [ ] Random Forest
  - [ ] Gradient Boosting (XGBoost/LightGBM)

- [ ] **Phase 5**: Evaluation & Iteration
  - [ ] Error analysis
  - [ ] Model refinement
  - [ ] Performance tracking

## Data Source

This project uses ESPN's unofficial public API:
- **Scoreboard API**: Game results and scores
- **Teams API**: Team information and rosters
- **No authentication required**
- **Rate limiting**: Built-in delays to be respectful

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Acknowledgments

- ESPN for providing accessible APIs
- Sports Reference for inspiration
- College basketball analytics community

## Contact

- GitHub: [@tatejones2](https://github.com/tatejones2)
- Repository: [CBB-ML](https://github.com/tatejones2/CBB-ML)/
├── data/
│   ├── raw/          # Raw data from sources
│   └── processed/    # Cleaned and processed data
├── notebooks/        # Jupyter notebooks for exploration
├── src/              # Source code
├── models/           # Trained models
├── tests/            # Unit tests
├── docs/             # Documentation
└── requirements.txt  # Python dependencies
```

## Roadmap

See `docs/cbb_ml_guide.md` for the complete development roadmap.

## License

TBD

## Contact

TBD
