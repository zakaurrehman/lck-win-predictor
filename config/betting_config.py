


# config/betting_config.py
"""
Betting-specific configuration parameters
"""

class BettingConfig:
    """Configuration for betting strategies and parameters"""
    
    # Edge calculation settings
    MIN_EDGE_THRESHOLD = 0.05  # 5% minimum edge
    MAX_EDGE_THRESHOLD = 0.50  # 50% maximum edge (sanity check)
    
    # Probability thresholds
    MIN_PROBABILITY = 0.55  # Don't bet on anything below 55% confidence
    MAX_PROBABILITY = 0.95  # Cap at 95% to avoid overconfidence
    
    # Kelly Criterion settings
    USE_KELLY_CRITERION = True
    MAX_KELLY_FRACTION = 0.25  # Never bet more than 25% of bankroll
    MIN_KELLY_FRACTION = 0.01  # Minimum 1% bet size
    
    # Fixed betting settings (alternative to Kelly)
    FIXED_BET_PERCENTAGE = 0.02  # 2% of bankroll per bet
    
    # Risk management
    MAX_DAILY_LOSS = 0.10  # Stop betting if daily loss exceeds 10%
    MAX_DRAWDOWN = 0.20   # Stop betting if drawdown exceeds 20%
    
    # Odds validation
    MIN_DECIMAL_ODDS = 1.01
    MAX_DECIMAL_ODDS = 50.0
    
    # Market efficiency filters
    MIN_MARKET_VOLUME = 1000  # Minimum betting volume (if available)
    BOOKMAKER_RANKINGS = {
        'pinnacle': 10,     # Most efficient
        'bet365': 8,
        'betway': 7,
        'unibet': 6,
        'smaller_books': 5
    }
    
    # Team and league filters
    SUPPORTED_LEAGUES = ['LCK', 'LPL', 'LEC', 'LCS']  # Expand as needed
    BLACKLISTED_TEAMS = []  # Teams to never bet on
    
    # Time-based filters
    MIN_TIME_BEFORE_MATCH = 1  # Hours before match starts
    MAX_TIME_BEFORE_MATCH = 168  # 1 week max
    
    # Performance thresholds for strategy adjustments
    PERFORMANCE_REVIEW_PERIOD = 30  # Days
    MIN_ROI_FOR_CONTINUATION = -0.05  # Continue if ROI > -5%
    MIN_SAMPLE_SIZE = 50  # Minimum bets before performance evaluation