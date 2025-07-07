# betting/edge_calculator.py
"""
Calculate betting edge and expected value
"""

class EdgeCalculator:
    """Calculate betting edges and expected values"""
    
    def __init__(self, min_edge: float = 0.05, min_probability: float = 0.55):
        """
        Args:
            min_edge: Minimum edge required to place bet (default 5%)
            min_probability: Minimum predicted probability to consider betting
        """
        self.min_edge = min_edge
        self.min_probability = min_probability
    
    def calculate_edge(self, predicted_prob: float, market_prob: float) -> float:
        """
        Calculate betting edge
        
        Edge = (Predicted Probability / Market Probability) - 1
        Positive edge means bet has value
        """
        if market_prob <= 0:
            return 0.0
        return (predicted_prob / market_prob) - 1.0
    
    def calculate_expected_value(self, predicted_prob: float, decimal_odds: float, stake: float = 1.0) -> float:
        """
        Calculate expected value of a bet
        
        EV = (Win Probability × Win Amount) - (Lose Probability × Stake)
        """
        win_amount = (decimal_odds - 1) * stake
        lose_amount = stake
        
        ev = (predicted_prob * win_amount) - ((1 - predicted_prob) * lose_amount)
        return ev
    
    def should_bet(self, predicted_prob: float, market_prob: float) -> Dict:
        """
        Determine if bet should be placed based on edge and probability thresholds
        """
        edge = self.calculate_edge(predicted_prob, market_prob)
        
        result = {
            'should_bet': False,
            'edge': edge,
            'predicted_prob': predicted_prob,
            'market_prob': market_prob,
            'reason': ''
        }
        
        if predicted_prob < self.min_probability:
            result['reason'] = f'Predicted probability {predicted_prob:.3f} below minimum {self.min_probability}'
        elif edge < self.min_edge:
            result['reason'] = f'Edge {edge:.3f} below minimum {self.min_edge}'
        else:
            result['should_bet'] = True
            result['reason'] = f'Positive edge: {edge:.3f} ({edge*100:.1f}%)'
        
        return result

