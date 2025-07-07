# scripts/run_backtest.py
"""
Main script to run backtesting with various configurations
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtesting.backtest_engine import LCKBacktestEngine
from backtesting.performance_metrics import PerformanceAnalyzer
from backtesting.visualization import BacktestVisualizer
from data_collection.data_validator import DataValidator

def run_single_backtest(config: dict) -> dict:
    """Run a single backtest with given configuration"""
    
    print(f"🚀 Starting backtest: {config['name']}")
    print(f"📊 Parameters: Bankroll=${config['initial_bankroll']}, "
          f"Min Edge={config['min_edge']*100:.1f}%, "
          f"Min Prob={config['min_probability']*100:.1f}%")
    
    # Initialize backtest engine
    engine = LCKBacktestEngine(
        initial_bankroll=config['initial_bankroll'],
        min_edge=config['min_edge'],
        min_probability=config['min_probability'],
        use_kelly=config.get('use_kelly', True),
        max_kelly=config.get('max_kelly', 0.25)
    )
    
    # Load historical data
    historical_data = engine.load_historical_data(
        config['odds_file'],
        config['matches_file']
    )
    
    if len(historical_data) == 0:
        print("❌ No historical data loaded. Check your data files.")
        return {}
    
    # Run backtest
    results = engine.run_backtest(
        historical_data,
        start_date=config.get('start_date'),
        end_date=config.get('end_date')
    )
    
    # Analyze results
    analyzer = PerformanceAnalyzer()
    analysis = analyzer.analyze_results(results)
    
    # Create visualizations
    visualizer = BacktestVisualizer()
    charts = visualizer.create_performance_dashboard(results, analysis)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = f"reports/backtest_results/{config['name']}_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    # Save data
    with open(f"{results_dir}/results.json", 'w') as f:
        json.dump({
            'config': config,
            'results': results,
            'analysis': analysis
        }, f, indent=2, default=str)
    
    # Save charts
    for chart_name, chart_data in charts.items():
        with open(f"{results_dir}/{chart_name}.png", 'wb') as f:
            import base64
            f.write(base64.b64decode(chart_data))
    
    # Save summary report
    summary_report = visualizer.create_summary_report(results, analysis)
    with open(f"{results_dir}/summary_report.txt", 'w') as f:
        f.write(summary_report)
    
    print(f"✅ Backtest completed. Results saved to: {results_dir}")
    print(f"📈 Final ROI: {analysis['summary']['roi']:+.2f}%")
    print(f"🎯 Win Rate: {analysis['summary']['win_rate']:.1%}")
    print(f"💰 Total Profit: ${analysis['summary']['total_profit']:+,.2f}")
    
    return {
        'config': config,
        'results': results,
        'analysis': analysis,
        'charts': charts,
        'results_dir': results_dir
    }

def run_parameter_sweep():
    """Run backtests with different parameter combinations"""
    
    base_config = {
        'name': 'parameter_sweep',
        'odds_file': 'data/odds/historical_odds.csv',
        'matches_file': 'data/matches/match_results.csv',
        'initial_bankroll': 1000.0,
        'use_kelly': True,
        'max_kelly': 0.25
    }
    
    # Parameter combinations to test
    parameter_combinations = [
        {'min_edge': 0.03, 'min_probability': 0.53},  # Aggressive
        {'min_edge': 0.05, 'min_probability': 0.55},  # Balanced
        {'min_edge': 0.08, 'min_probability': 0.58},  # Conservative
        {'min_edge': 0.10, 'min_probability': 0.60},  # Very Conservative
    ]
    
    sweep_results = []
    
    for i, params in enumerate(parameter_combinations):
        config = base_config.copy()
        config.update(params)
        config['name'] = f"sweep_{i+1}_edge{params['min_edge']*100:.0f}_prob{params['min_probability']*100:.0f}"
        
        result = run_single_backtest(config)
        if result:
            sweep_results.append(result)
    
    # Compare results
    print("\n" + "="*60)
    print("PARAMETER SWEEP COMPARISON")
    print("="*60)
    
    for result in sweep_results:
        analysis = result['analysis']
        config = result['config']
        print(f"\n{config['name']}:")
        print(f"  Edge: {config['min_edge']*100:.1f}%, Prob: {config['min_probability']*100:.1f}%")
        print(f"  ROI: {analysis['summary']['roi']:+.2f}%")
        print(f"  Win Rate: {analysis['summary']['win_rate']:.1%}")
        print(f"  Total Bets: {analysis['summary']['total_bets']:,}")
        print(f"  Max Drawdown: {analysis['risk_metrics']['max_drawdown']:.2f}%")
    
    return sweep_results

def run_time_period_analysis():
    """Run backtests for different time periods"""
    
    base_config = {
        'name': 'time_analysis',
        'odds_file': 'data/odds/historical_odds.csv',
        'matches_file': 'data/matches/match_results.csv',
        'initial_bankroll': 1000.0,
        'min_edge': 0.05,
        'min_probability': 0.55,
        'use_kelly': True
    }
    
    # Time periods to test
    time_periods = [
        {'start_date': '2019-01-01', 'end_date': '2019-12-31', 'name': '2019'},
        {'start_date': '2020-01-01', 'end_date': '2020-12-31', 'name': '2020'},
        {'start_date': '2021-01-01', 'end_date': '2021-12-31', 'name': '2021'},
        {'start_date': '2022-01-01', 'end_date': '2022-12-31', 'name': '2022'},
        {'start_date': '2023-01-01', 'end_date': '2023-12-31', 'name': '2023'},
        {'start_date': '2024-01-01', 'end_date': '2024-12-31', 'name': '2024'},
    ]
    
    period_results = []
    
    for period in time_periods:
        config = base_config.copy()
        config.update(period)
        config['name'] = f"period_{period['name']}"
        
        result = run_single_backtest(config)
        if result:
            period_results.append(result)
    
    # Analyze year-over-year performance
    print("\n" + "="*60)
    print("YEAR-OVER-YEAR PERFORMANCE")
    print("="*60)
    
    for result in period_results:
        analysis = result['analysis']
        config = result['config']
        print(f"\n{config['name']}:")
        print(f"  ROI: {analysis['summary']['roi']:+.2f}%")
        print(f"  Win Rate: {analysis['summary']['win_rate']:.1%}")
        print(f"  Total Bets: {analysis['summary']['total_bets']:,}")
        print(f"  Sharpe Ratio: {analysis.get('risk_metrics', {}).get('sharpe_ratio', 'N/A')}")
    
    return period_results

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Run LCK betting backtests')
    parser.add_argument('--mode', choices=['single', 'sweep', 'time'], default='single',
                       help='Backtest mode: single, parameter sweep, or time analysis')
    parser.add_argument('--config', type=str, help='Path to config JSON file')
    
    args = parser.parse_args()
    
    if args.mode == 'single':
        if args.config:
            with open(args.config, 'r') as f:
                config = json.load(f)
        else:
            # Default single backtest configuration
            config = {
                'name': 'default_backtest',
                'odds_file': 'data/odds/historical_odds.csv',
                'matches_file': 'data/matches/match_results.csv',
                'initial_bankroll': 1000.0,
                'min_edge': 0.05,
                'min_probability': 0.55,
                'use_kelly': True,
                'max_kelly': 0.25,
                'start_date': '2020-01-01',
                'end_date': '2024-12-31'
            }
        
        run_single_backtest(config)
    
    elif args.mode == 'sweep':
        run_parameter_sweep()
    
    elif args.mode == 'time':
        run_time_period_analysis()

if __name__ == "__main__":
    main()