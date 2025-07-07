# backtesting/visualization.py
"""Visualization for backtesting"""

class BacktestVisualizer:
    """Create visualizations (simplified)"""
    
    def create_performance_dashboard(self, results, analysis):
        """Return empty charts for now"""
        return {
            'bankroll_curve': {},
            'profit_distribution': {},
            'win_rate_by_odds': {}
        }
    
    def create_summary_report(self, results, analysis):
        """Create text summary report"""
        summary = analysis.get('summary', {})
        
        report = f"""
BACKTESTING SUMMARY REPORT
==========================

OVERALL PERFORMANCE
-------------------
Total Bets: {summary.get('total_bets', 0)}
Winning Bets: {summary.get('winning_bets', 0)}
Win Rate: {summary.get('win_rate', 0):.1%}
Total Profit: ${summary.get('total_profit', 0):.2f}
ROI: {summary.get('roi', 0):.2f}%
Final Bankroll: ${summary.get('final_bankroll', 0):.2f}
"""
        return report
