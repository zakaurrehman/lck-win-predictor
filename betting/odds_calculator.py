# betting/odds_calculator.py
"""
Odds calculator for converting between different odds formats
and calculating implied probabilities
"""

import numpy as np
from typing import Union, Tuple, Dict

class OddsCalculator:
    """Handle odds conversions and probability calculations"""
    
    @staticmethod
    def decimal_to_probability(decimal_odds: float) -> float:
        """Convert decimal odds to implied probability"""
        if decimal_odds <= 1.0:
            raise ValueError("Decimal odds must be greater than 1.0")
        return 1.0 / decimal_odds
    
    @staticmethod
    def american_to_probability(american_odds: int) -> float:
        """Convert American odds to implied probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    @staticmethod
    def probability_to_decimal(probability: float) -> float:
        """Convert probability to decimal odds"""
        if probability <= 0 or probability >= 1:
            raise ValueError("Probability must be between 0 and 1")
        return 1.0 / probability
    
    @staticmethod
    def remove_vig(prob_a: float, prob_b: float) -> Tuple[float, float]:
        """Remove bookmaker vig to get true probabilities"""
        total = prob_a + prob_b
        if total <= 1.0:
            return prob_a, prob_b  # No vig detected
        
        # Remove vig proportionally
        true_prob_a = prob_a / total
        true_prob_b = prob_b / total
        return true_prob_a, true_prob_b
    
    @staticmethod
    def calculate_vig(prob_a: float, prob_b: float) -> float:
        """Calculate bookmaker vig percentage"""
        return (prob_a + prob_b - 1.0) * 100