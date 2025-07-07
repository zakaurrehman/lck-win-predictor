# backtesting/performance_metrics.py
"""Performance analysis for backtesting"""

import pandas as pd
import numpy as np

class PerformanceAnalyzer:
    """Analyze backtest performance"""
    
    def analyze_results(self, results):
        """Calculate performance metrics"""
        bets = results.get('bets', [])
        
        if not bets:
            return {'summary': self._empty_summary()}
        
        bets_df = pd.DataFrame(bets)
        
        total_bets = len(bets_df)
        winning_bets = len(bets_df[bets_df['outcome'] == 'Win'])
        total_wagered = bets_df['bet_size'].sum()
        total_profit = bets_df['profit'].sum()
        
        summary = {
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'losing_bets': total_bets - winning_bets,
            'win_rate': winning_bets / total_bets if total_bets > 0 else 0,
            'total_wagered': total_wagered,
            'total_profit': total_profit,
            'roi': (total_profit / total_wagered * 100) if total_wagered > 0 else 0,
            'final_bankroll': results.get('final_bankroll', 0),
            'avg_bet_size': total_wagered / total_bets if total_bets > 0 else 0,
            'avg_profit_per_bet': total_profit / total_bets if total_bets > 0 else 0,
            'biggest_win': bets_df['profit'].max() if not bets_df.empty else 0,
            'biggest_loss': bets_df['profit'].min() if not bets_df.empty else 0,
            'avg_odds': bets_df['odds'].mean() if not bets_df.empty else 0,
            'avg_edge': bets_df['edge'].mean() if not bets_df.empty else 0
        }
        
        return {'summary': summary}
    
    def _empty_summary(self):
        """Return empty summary"""
        return {
            'total_bets': 0,
            'winning_bets': 0,
            'losing_bets': 0,
            'win_rate': 0,
            'total_wagered': 0,
            'total_profit': 0,
            'roi': 0,
            'final_bankroll': 0,
            'avg_bet_size': 0,
            'avg_profit_per_bet': 0,
            'biggest_win': 0,
            'biggest_loss': 0,
            'avg_odds': 0,
            'avg_edge': 0
        }
