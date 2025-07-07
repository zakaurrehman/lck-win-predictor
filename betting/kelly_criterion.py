
# betting/kelly_criterion.py
"""
Kelly Criterion for optimal bet sizing
"""

class KellyCriterion:
    """Calculate optimal bet sizes using Kelly Criterion"""
    
    def __init__(self, max_kelly: float = 0.25, min_bet: float = 0.01):
        """
        Args:
            max_kelly: Maximum Kelly fraction to prevent overbetting
            min_bet: Minimum bet size as fraction of bankroll
        """
        self.max_kelly = max_kelly
        self.min_bet = min_bet
    
    def calculate_kelly_fraction(self, predicted_prob: float, decimal_odds: float) -> float:
        """
        Calculate Kelly fraction
        
        Kelly = (bp - q) / b
        where:
        b = decimal odds - 1 (net odds)
        p = predicted probability of winning
        q = predicted probability of losing (1 - p)
        """
        if predicted_prob <= 0 or predicted_prob >= 1:
            return 0.0
        
        b = decimal_odds - 1  # Net odds
        p = predicted_prob
        q = 1 - predicted_prob
        
        kelly = (b * p - q) / b
        
        # Cap at maximum Kelly to prevent overbetting
        kelly = min(kelly, self.max_kelly)
        
        # Don't bet if Kelly is negative or too small
        if kelly < self.min_bet:
            return 0.0
        
        return kelly
    
    def calculate_bet_size(self, bankroll: float, predicted_prob: float, decimal_odds: float) -> Dict:
        """
        Calculate actual bet size based on bankroll and Kelly fraction
        """
        kelly_fraction = self.calculate_kelly_fraction(predicted_prob, decimal_odds)
        bet_amount = bankroll * kelly_fraction
        
        return {
            'kelly_fraction': kelly_fraction,
            'bet_amount': bet_amount,
            'bankroll_percentage': kelly_fraction * 100
        }