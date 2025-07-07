# backtesting/odds_calculator.py
"""
Kelly Criterion calculator for optimal betting sizes
"""

import numpy as np

class KellyCriterion:
    """Calculate optimal bet sizes using Kelly Criterion"""
    
    def __init__(self, max_kelly_fraction=0.25, risk_free_rate=0.02):
        self.max_kelly_fraction = max_kelly_fraction
        self.risk_free_rate = risk_free_rate
    
    def calculate_kelly_fraction(self, probability, odds):
        """Calculate Kelly fraction for a single bet"""
        if probability <= 0 or probability >= 1:
            return 0
        
        if odds <= 1:
            return 0
        
        q = 1 - probability
        b = odds - 1
        
        kelly_fraction = (probability * b - q) / b
        kelly_fraction = max(0, kelly_fraction)
        kelly_fraction = min(kelly_fraction, self.max_kelly_fraction)
        
        return kelly_fraction
    
    def calculate_bet_size(self, bankroll, probability, odds):
        """Calculate actual bet size in dollars"""
        kelly_fraction = self.calculate_kelly_fraction(probability, odds)
        return bankroll * kelly_fraction
    
    def calculate_expected_value(self, probability, odds, bet_size=1):
        """Calculate expected value of a bet"""
        win_amount = bet_size * (odds - 1)
        loss_amount = bet_size
        
        ev = (probability * win_amount) - ((1 - probability) * loss_amount)
        return ev
    
    def calculate_edge(self, probability, odds):
        """Calculate betting edge"""
        if odds <= 0:
            return 0
        
        implied_prob = 1 / odds
        edge = probability - implied_prob
        return edge
