# config/settings.py
"""
Configuration settings for the betting system
"""

import os
from typing import Dict, Any

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database settings (if you want to use a database instead of CSV files)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///lck_betting.db'
    
    # API Keys for data sources
    ODDS_API_KEY = os.environ.get('ODDS_API_KEY')
    RIOT_API_KEY = os.environ.get('RIOT_API_KEY')
    
    # Data file paths
    ODDS_DATA_PATH = 'data/odds/historical_odds.csv'
    MATCHES_DATA_PATH = 'data/matches/match_results.csv'
    MERGED_DATA_PATH = 'data/merged_betting_data.csv'
    
    # Model settings
    MODEL_PATH = 'models/final_phase3_models.pkl'
    MODEL_ACCURACY = 79.88  # Your reported model accuracy
    
    # Default backtesting parameters
    DEFAULT_BACKTEST_CONFIG = {
        'initial_bankroll': 1000.0,
        'min_edge': 0.05,
        'min_probability': 0.55,
        'use_kelly': True,
        'max_kelly': 0.25,
        'risk_free_rate': 0.02
    }
    
    # Data collection settings
    MAX_SCRAPE_RETRIES = 3
    SCRAPE_DELAY = 1.0  # Seconds between requests
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'

# Get config based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}