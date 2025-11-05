"""
Baseline Model Training for College Basketball Predictions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CBBModelTrainer:
    """Train and evaluate basketball prediction models"""
    
    def __init__(self, features_path='data/processed/features.csv'):
        """Initialize trainer with features"""
        self.features_path = features_path
        self.models = {}
        self.results = {}
        
    def load_features(self):
        """Load engineered features"""
        if not os.path.exists(self.features_path):
            logger.error(f"Features file not found: {self.features_path}")
            return None
        
        df = pd.read_csv(self.features_path)
        logger.info(f"Loaded {len(df)} samples with {len(df.columns)} columns")
        return df
    
    def prepare_data(self, df, target='point_differential', test_size=0.2):
        """
        Prepare data for training
        
        Args:
            df: Features DataFrame
            target: Target variable to predict
            test_size: Proportion for test set
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test, feature_cols)
        """
        # Identify feature columns (exclude metadata and targets)
        exclude_cols = [
            'game_id', 'date', 'season', 'home_team_id', 'away_team_id',
            'home_score', 'away_score', 'home_win', 'point_differential'
        ]
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        if len(feature_cols) == 0:
            logger.error("No feature columns found!")
            return None
        
        logger.info(f"Using {len(feature_cols)} features: {feature_cols}")
        
        # Prepare X and y
        X = df[feature_cols].copy()
        y = df[target].copy()
        
        # Handle any missing values
        X = X.fillna(X.mean())
        
        # Time-series split (don't shuffle - maintain temporal order)
        if 'date' in df.columns:
            df = df.sort_values('date')
            split_idx = int(len(df) * (1 - test_size))
            X_train = X.iloc[:split_idx]
            X_test = X.iloc[split_idx:]
            y_train = y.iloc[:split_idx]
            y_test = y.iloc[split_idx:]
            logger.info("Using time-series split")
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            logger.info("Using random split")
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        return X_train, X_test, y_train, y_test, feature_cols
    
    def train_baseline_model(self, X_train, y_train):
        """
        Train a simple baseline model (predict average)
        
        Returns:
            Baseline predictions (all samples = mean of training set)
        """
        baseline_pred = np.full(len(y_train), y_train.mean())
        return baseline_pred, y_train.mean()
    
    def train_linear_regression(self, X_train, y_train, X_test):
        """Train Linear Regression model"""
        logger.info("Training Linear Regression...")
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        self.models['linear_regression'] = model
        return train_pred, test_pred
    
    def train_ridge_regression(self, X_train, y_train, X_test, alpha=1.0):
        """Train Ridge Regression model"""
        logger.info(f"Training Ridge Regression (alpha={alpha})...")
        model = Ridge(alpha=alpha)
        model.fit(X_train, y_train)
        
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        self.models['ridge_regression'] = model
        return train_pred, test_pred
    
    def train_random_forest(self, X_train, y_train, X_test, n_estimators=100):
        """Train Random Forest model"""
        logger.info(f"Training Random Forest (n_estimators={n_estimators})...")
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        self.models['random_forest'] = model
        return train_pred, test_pred
    
    def evaluate_model(self, y_true, y_pred, model_name, dataset='Test'):
        """
        Evaluate model performance
        
        Returns:
            Dictionary with metrics
        """
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        
        results = {
            'model': model_name,
            'dataset': dataset,
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'n_samples': len(y_true),
        }
        
        logger.info(f"{model_name} - {dataset}: MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.3f}")
        
        return results
    
    def train_all_models(self, target='point_differential'):
        """
        Train all models and compare performance
        
        Returns:
            DataFrame with results
        """
        # Load and prepare data
        df = self.load_features()
        if df is None or len(df) == 0:
            logger.error("No data available for training")
            return None
        
        data = self.prepare_data(df, target=target)
        if data is None:
            return None
        
        X_train, X_test, y_train, y_test, feature_cols = data
        
        results_list = []
        
        # Baseline model
        logger.info("\n" + "="*70)
        logger.info("BASELINE MODEL (Predict Mean)")
        logger.info("="*70)
        baseline_train_pred, baseline_mean = self.train_baseline_model(X_train, y_train)
        baseline_test_pred = np.full(len(y_test), baseline_mean)
        
        results_list.append(self.evaluate_model(y_train, baseline_train_pred, 'Baseline', 'Train'))
        results_list.append(self.evaluate_model(y_test, baseline_test_pred, 'Baseline', 'Test'))
        
        # Linear Regression
        logger.info("\n" + "="*70)
        logger.info("LINEAR REGRESSION")
        logger.info("="*70)
        lr_train_pred, lr_test_pred = self.train_linear_regression(X_train, y_train, X_test)
        
        results_list.append(self.evaluate_model(y_train, lr_train_pred, 'Linear Regression', 'Train'))
        results_list.append(self.evaluate_model(y_test, lr_test_pred, 'Linear Regression', 'Test'))
        
        # Ridge Regression
        logger.info("\n" + "="*70)
        logger.info("RIDGE REGRESSION")
        logger.info("="*70)
        ridge_train_pred, ridge_test_pred = self.train_ridge_regression(X_train, y_train, X_test)
        
        results_list.append(self.evaluate_model(y_train, ridge_train_pred, 'Ridge Regression', 'Train'))
        results_list.append(self.evaluate_model(y_test, ridge_test_pred, 'Ridge Regression', 'Test'))
        
        # Random Forest
        logger.info("\n" + "="*70)
        logger.info("RANDOM FOREST")
        logger.info("="*70)
        rf_train_pred, rf_test_pred = self.train_random_forest(X_train, y_train, X_test)
        
        results_list.append(self.evaluate_model(y_train, rf_train_pred, 'Random Forest', 'Train'))
        results_list.append(self.evaluate_model(y_test, rf_test_pred, 'Random Forest', 'Test'))
        
        # Create results DataFrame
        results_df = pd.DataFrame(results_list)
        self.results = results_df
        
        return results_df
    
    def save_models(self, output_dir='models'):
        """Save trained models"""
        os.makedirs(output_dir, exist_ok=True)
        
        for model_name, model in self.models.items():
            path = os.path.join(output_dir, f'{model_name}.joblib')
            joblib.dump(model, path)
            logger.info(f"Saved {model_name} to {path}")
    
    def print_results_summary(self):
        """Print formatted results summary"""
        if self.results is None or len(self.results) == 0:
            print("No results available")
            return
        
        print("\n" + "="*70)
        print("MODEL COMPARISON SUMMARY")
        print("="*70)
        print(self.results.to_string(index=False))
        
        # Best model by test MAE
        test_results = self.results[self.results['dataset'] == 'Test']
        if not test_results.empty:
            best_model = test_results.loc[test_results['mae'].idxmin()]
            print("\n" + "-"*70)
            print(f"🏆 Best Model (by Test MAE): {best_model['model']}")
            print(f"   MAE: {best_model['mae']:.2f} points")
            print(f"   RMSE: {best_model['rmse']:.2f} points")
            print(f"   R²: {best_model['r2']:.3f}")
            print("-"*70)


def main():
    """Example usage"""
    trainer = CBBModelTrainer()
    
    # Train all models
    results = trainer.train_all_models()
    
    if results is not None:
        # Print summary
        trainer.print_results_summary()
        
        # Save models
        trainer.save_models()
        print("\n✓ Models saved to models/")
    else:
        print("\n⚠️  Not enough data to train models yet")
        print("Waiting for scraper to collect more historical data...")


if __name__ == "__main__":
    main()
