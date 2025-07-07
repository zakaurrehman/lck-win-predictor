#!/usr/bin/env python3
"""
Quick setup script to get backtesting working
Run this once to set up everything needed for backtesting
"""

import os
import sys

def setup_backtesting():
    print("Setting up LCK Backtesting System...")
    
    # 1. Create necessary directories
    directories = [
        'backtesting',
        'data',
        'data/odds',
        'data/matches',
        'data_collection',
        'templates',
        'reports',
        'reports/backtest_results'
    ]
    
    for dir in directories:
        os.makedirs(dir, exist_ok=True)
        print(f"Created directory: {dir}")
    
    # 2. Create __init__.py files
    init_files = [
        'backtesting/__init__.py',
        'data_collection/__init__.py'
    ]
    
    for file in init_files:
        with open(file, 'w', encoding='utf-8') as f:
            f.write('# Auto-generated init file\n')
        print(f"Created: {file}")
    
    # 3. Save the backtesting module files
    print("\nCreating backtesting modules...")
    
    # Save odds_calculator.py
    with open('backtesting/odds_calculator.py', 'w', encoding='utf-8') as f:
        f.write('''# backtesting/odds_calculator.py
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
''')
    print("Created: backtesting/odds_calculator.py")
    
    # Update __init__.py with proper imports
    with open('backtesting/__init__.py', 'w', encoding='utf-8') as f:
        f.write('''"""Backtesting module for LCK predictions"""

from .backtest_engine import LCKBacktestEngine
from .performance_metrics import PerformanceAnalyzer
from .visualization import BacktestVisualizer
from .odds_calculator import KellyCriterion

__all__ = ['LCKBacktestEngine', 'PerformanceAnalyzer', 'BacktestVisualizer', 'KellyCriterion']
''')
    
    # Save simplified backtest_engine.py
    with open('backtesting/backtest_engine.py', 'w', encoding='utf-8') as f:
        f.write('''# backtesting/backtest_engine.py
"""Simplified backtest engine"""

import pandas as pd
import numpy as np
from typing import Dict
import logging

class LCKBacktestEngine:
    """Simplified backtesting engine"""
    
    def __init__(self, initial_bankroll=1000, min_edge=0.05, 
                 min_probability=0.55, use_kelly=True, max_kelly=0.25):
        self.initial_bankroll = initial_bankroll
        self.bankroll = initial_bankroll
        self.min_edge = min_edge
        self.min_probability = min_probability
        self.use_kelly = use_kelly
        self.max_kelly = max_kelly
        self.bets = []
        self.bankroll_history = []
        self.logger = logging.getLogger(__name__)
        
    def load_historical_data(self, odds_file, matches_file):
        """Load and merge historical data"""
        try:
            odds_df = pd.read_csv(odds_file)
            matches_df = pd.read_csv(matches_file)
            
            # Simple merge on teams and date
            odds_df['date'] = pd.to_datetime(odds_df['commence_time']).dt.date
            matches_df['date'] = pd.to_datetime(matches_df['date']).dt.date
            
            merged = []
            for _, odds in odds_df.iterrows():
                match = matches_df[
                    (matches_df['date'] == odds['date']) &
                    (matches_df['team1'] == odds['team1']) &
                    (matches_df['team2'] == odds['team2'])
                ]
                if not match.empty:
                    merged.append({
                        **odds.to_dict(),
                        'winner': match.iloc[0]['winner']
                    })
            
            return pd.DataFrame(merged)
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def run_backtest(self, historical_data, start_date=None, end_date=None):
        """Run simplified backtest"""
        self.bets = []
        self.bankroll = self.initial_bankroll
        self.bankroll_history = []
        
        for _, match in historical_data.iterrows():
            # Simple prediction (random for demo)
            prediction = np.random.uniform(0.3, 0.7)
            
            # Check betting criteria
            implied_prob = 1 / match['team1_odds']
            edge = prediction - implied_prob
            
            if edge >= self.min_edge and prediction >= self.min_probability:
                # Calculate bet size
                if self.use_kelly:
                    kelly = (prediction * (match['team1_odds'] - 1) - (1 - prediction)) / (match['team1_odds'] - 1)
                    kelly = max(0, min(kelly, self.max_kelly))
                    bet_size = self.bankroll * kelly
                else:
                    bet_size = self.bankroll * 0.02
                
                # Determine outcome
                if match['winner'] == 1:
                    profit = bet_size * (match['team1_odds'] - 1)
                    outcome = 'Win'
                else:
                    profit = -bet_size
                    outcome = 'Loss'
                
                self.bankroll += profit
                
                # Record bet
                self.bets.append({
                    'date': match['commence_time'],
                    'team1': match['team1'],
                    'team2': match['team2'],
                    'bet_on': match['team1'],
                    'odds': match['team1_odds'],
                    'probability': prediction,
                    'edge': edge,
                    'bet_size': bet_size,
                    'outcome': outcome,
                    'profit': profit,
                    'bankroll': self.bankroll
                })
                
                self.bankroll_history.append({
                    'date': match['commence_time'],
                    'bankroll': self.bankroll
                })
        
        return {
            'bets': self.bets,
            'bankroll_history': self.bankroll_history,
            'final_bankroll': self.bankroll,
            'total_profit': self.bankroll - self.initial_bankroll
        }
''')
    print("Created: backtesting/backtest_engine.py")
    
    # Save simplified performance_metrics.py
    with open('backtesting/performance_metrics.py', 'w', encoding='utf-8') as f:
        f.write('''# backtesting/performance_metrics.py
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
''')
    print("Created: backtesting/performance_metrics.py")
    
    # Save simplified visualization.py
    with open('backtesting/visualization.py', 'w', encoding='utf-8') as f:
        f.write('''# backtesting/visualization.py
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
''')
    print("Created: backtesting/visualization.py")
    
    # Save data_validator.py if it doesn't exist
    if not os.path.exists('data_collection/data_validator.py'):
        with open('data_collection/data_validator.py', 'w', encoding='utf-8') as f:
            f.write('''# data_collection/data_validator.py
"""Data validation for odds and match results"""

import pandas as pd
import numpy as np
from typing import Tuple, List

class DataValidator:
    """Validate and clean betting data"""
    
    def validate_odds_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Validate odds data"""
        issues = []
        
        # Check required columns
        required_cols = ['bookmaker', 'commence_time', 'team1', 'team2', 'team1_odds', 'team2_odds']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")
        
        # Validate odds
        if 'team1_odds' in df.columns and 'team2_odds' in df.columns:
            invalid_odds = df[(df['team1_odds'] <= 1) | (df['team2_odds'] <= 1)]
            if len(invalid_odds) > 0:
                issues.append(f"{len(invalid_odds)} rows with invalid odds")
                df = df[(df['team1_odds'] > 1) & (df['team2_odds'] > 1)]
        
        return df, issues
    
    def validate_match_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Validate match results data"""
        issues = []
        
        # Check required columns
        required_cols = ['date', 'team1', 'team2', 'winner']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")
        
        # Validate winner
        if 'winner' in df.columns:
            invalid_winners = df[~df['winner'].isin([1, 2])]
            if len(invalid_winners) > 0:
                issues.append(f"{len(invalid_winners)} rows with invalid winner")
                df = df[df['winner'].isin([1, 2])]
        
        return df, issues
    
    def merge_odds_and_matches(self, odds_df: pd.DataFrame, matches_df: pd.DataFrame) -> pd.DataFrame:
        """Merge odds and match result data"""
        return pd.merge(odds_df, matches_df, on=['team1', 'team2'], how='inner')
''')
        print("Created: data_collection/data_validator.py")
    
    # 4. Create the backtesting HTML template
    print("\nCreating HTML template...")
    # First, let me save the template without emojis to avoid encoding issues
    html_template = open('backtesting_template.html', 'w', encoding='utf-8')
    html_template.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LCK Backtesting Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            color: #667eea;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        .nav-back {
            display: inline-block;
            margin-bottom: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .nav-back:hover {
            transform: translateX(-5px);
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .tab {
            padding: 15px 30px;
            background: none;
            border: none;
            font-size: 1rem;
            font-weight: 500;
            color: #666;
            cursor: pointer;
            position: relative;
            transition: all 0.3s;
        }
        
        .tab.active {
            color: #667eea;
        }
        
        .tab.active::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            right: 0;
            height: 2px;
            background: #667eea;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .config-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .config-group {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
        }
        
        .config-group h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.2rem;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 500;
        }
        
        .form-group input,
        .form-group select {
            width: 100%;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .form-group input[type="checkbox"] {
            width: auto;
            margin-right: 10px;
        }
        
        .checkbox-label {
            display: flex;
            align-items: center;
            cursor: pointer;
        }
        
        .data-status {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .data-status.error {
            background: #ffebee;
            color: #c62828;
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }
        
        .btn:hover {
            background: #5a67d8;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn.loading {
            position: relative;
            color: transparent;
        }
        
        .btn.loading::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            top: 50%;
            left: 50%;
            margin-left: -10px;
            margin-top: -10px;
            border: 2px solid #ffffff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spinner 0.8s linear infinite;
        }
        
        @keyframes spinner {
            to { transform: rotate(360deg); }
        }
        
        .results-section {
            margin-top: 40px;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        
        .summary-card h4 {
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 10px;
            opacity: 0.9;
        }
        
        .summary-card .value {
            font-size: 2rem;
            font-weight: 700;
        }
        
        .summary-card.positive {
            background: linear-gradient(135deg, #43a047 0%, #66bb6a 100%);
        }
        
        .summary-card.negative {
            background: linear-gradient(135deg, #e53935 0%, #ef5350 100%);
        }
        
        .chart-container {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        
        .chart-container h3 {
            color: #333;
            margin-bottom: 20px;
        }
        
        .bets-table {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
        }
        
        .bets-table table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .bets-table th {
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #555;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .bets-table td {
            padding: 15px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .bets-table tr:hover {
            background: #f8f9fa;
        }
        
        .outcome-win {
            color: #43a047;
            font-weight: 600;
        }
        
        .outcome-loss {
            color: #e53935;
            font-weight: 600;
        }
        
        .profit-positive {
            color: #43a047;
        }
        
        .profit-negative {
            color: #e53935;
        }
        
        #loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        #loading-overlay.active {
            display: flex;
        }
        
        .loading-content {
            background: white;
            padding: 40px;
            border-radius: 20px;
            text-align: center;
        }
        
        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid #f0f0f0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spinner 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        .loading-text {
            color: #666;
            font-size: 1.1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="nav-back">← Back to Predictions</a>
        
        <div class="header">
            <h1>LCK Backtesting Dashboard</h1>
            <p>Test your betting strategies with historical data</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('config')">Configuration</button>
            <button class="tab" onclick="switchTab('results')">Results</button>
            <button class="tab" onclick="switchTab('history')">Bet History</button>
            <button class="tab" onclick="switchTab('data')">Data Status</button>
        </div>
        
        <!-- Configuration Tab -->
        <div id="config-tab" class="tab-content active">
            <div id="data-validation" class="data-status">
                <span id="data-status-text">Checking data files...</span>
            </div>
            
            <div class="config-section">
                <div class="config-group">
                    <h3>Bankroll Settings</h3>
                    <div class="form-group">
                        <label for="initial-bankroll">Initial Bankroll ($)</label>
                        <input type="number" id="initial-bankroll" value="1000" min="100" max="100000" step="100">
                    </div>
                    <div class="form-group">
                        <label for="max-bet-size">Maximum Bet Size (%)</label>
                        <input type="number" id="max-bet-size" value="25" min="1" max="100" step="1">
                    </div>
                </div>
                
                <div class="config-group">
                    <h3>Betting Strategy</h3>
                    <div class="form-group">
                        <label for="min-edge">Minimum Edge (%)</label>
                        <input type="number" id="min-edge" value="5" min="0" max="50" step="1">
                    </div>
                    <div class="form-group">
                        <label for="min-probability">Minimum Probability (%)</label>
                        <input type="number" id="min-probability" value="55" min="50" max="90" step="1">
                    </div>
                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" id="use-kelly" checked>
                            <span>Use Kelly Criterion</span>
                        </label>
                    </div>
                </div>
                
                <div class="config-group">
                    <h3>Date Range</h3>
                    <div class="form-group">
                        <label for="start-date">Start Date</label>
                        <input type="date" id="start-date">
                    </div>
                    <div class="form-group">
                        <label for="end-date">End Date</label>
                        <input type="date" id="end-date">
                    </div>
                </div>
            </div>
            
            <div style="text-align: center;">
                <button class="btn" id="run-backtest-btn" onclick="runBacktest()">
                    <span>Run Backtest</span>
                </button>
            </div>
        </div>
        
        <!-- Results Tab -->
        <div id="results-tab" class="tab-content">
            <div id="results-content">
                <p style="text-align: center; color: #666; padding: 40px;">
                    No backtest results yet. Run a backtest to see results here.
                </p>
            </div>
        </div>
        
        <!-- History Tab -->
        <div id="history-tab" class="tab-content">
            <div id="history-content">
                <p style="text-align: center; color: #666; padding: 40px;">
                    No betting history yet. Run a backtest to see bet details here.
                </p>
            </div>
        </div>
        
        <!-- Data Status Tab -->
        <div id="data-tab" class="tab-content">
            <div id="data-validation-details">
                <p style="text-align: center; color: #666; padding: 40px;">
                    Loading data validation details...
                </p>
            </div>
        </div>
    </div>
    
    <!-- Loading Overlay -->
    <div id="loading-overlay">
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <div class="loading-text">Running backtest...</div>
        </div>
    </div>
    
    <script>
        // Chart instances
        let bankrollChart = null;
        let winrateChart = null;
        let profitChart = null;
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            validateData();
            setDefaultDates();
        });
        
        function setDefaultDates() {
            const today = new Date();
            const threeMonthsAgo = new Date(today);
            threeMonthsAgo.setMonth(today.getMonth() - 3);
            
            document.getElementById('end-date').value = today.toISOString().split('T')[0];
            document.getElementById('start-date').value = threeMonthsAgo.toISOString().split('T')[0];
        }
        
        function switchTab(tabName) {
            // Update tab buttons
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Update tab content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${tabName}-tab`).classList.add('active');
        }
        
        async function validateData() {
            try {
                const response = await fetch('/api/validate-data');
                const data = await response.json();
                
                const statusElement = document.getElementById('data-status-text');
                const validationElement = document.getElementById('data-validation');
                
                let statusText = '';
                let allValid = true;
                
                // Check odds file
                if (data.odds_file.exists && data.odds_file.valid) {
                    statusText += 'Odds data: ' + data.odds_file.records + ' records. ';
                } else {
                    statusText += 'Odds data: ' + (data.odds_file.exists ? 'Invalid format' : 'File missing') + '. ';
                    allValid = false;
                }
                
                // Check matches file
                if (data.matches_file.exists && data.matches_file.valid) {
                    statusText += 'Match data: ' + data.matches_file.records + ' records.';
                } else {
                    statusText += 'Match data: ' + (data.matches_file.exists ? 'Invalid format' : 'File missing') + '.';
                    allValid = false;
                }
                
                statusElement.textContent = statusText;
                validationElement.className = allValid ? 'data-status' : 'data-status error';
                
                // Disable backtest button if data is invalid
                document.getElementById('run-backtest-btn').disabled = !allValid;
                
                // Show detailed validation in data status tab
                showDataValidationDetails(data);
                
            } catch (error) {
                console.error('Error validating data:', error);
                document.getElementById('data-status-text').textContent = 'Error checking data files';
                document.getElementById('data-validation').className = 'data-status error';
            }
        }
        
        function showDataValidationDetails(data) {
            const detailsElement = document.getElementById('data-validation-details');
            
            let html = '<div class="config-section">';
            
            // Odds file details
            html += '<div class="config-group">';
            html += '<h3>Odds Data</h3>';
            html += '<p><strong>File exists:</strong> ' + (data.odds_file.exists ? 'Yes' : 'No') + '</p>';
            html += '<p><strong>Valid format:</strong> ' + (data.odds_file.valid ? 'Yes' : 'No') + '</p>';
            html += '<p><strong>Records:</strong> ' + data.odds_file.records.toLocaleString() + '</p>';
            if (data.odds_file.issues.length > 0) {
                html += '<p><strong>Issues:</strong> ' + data.odds_file.issues.join(', ') + '</p>';
            }
            html += '</div>';
            
            // Matches file details
            html += '<div class="config-group">';
            html += '<h3>Match Results Data</h3>';
            html += '<p><strong>File exists:</strong> ' + (data.matches_file.exists ? 'Yes' : 'No') + '</p>';
            html += '<p><strong>Valid format:</strong> ' + (data.matches_file.valid ? 'Yes' : 'No') + '</p>';
            html += '<p><strong>Records:</strong> ' + data.matches_file.records.toLocaleString() + '</p>';
            if (data.matches_file.issues.length > 0) {
                html += '<p><strong>Issues:</strong> ' + data.matches_file.issues.join(', ') + '</p>';
            }
            html += '</div>';
            
            html += '</div>';
            
            if (!data.odds_file.exists || !data.matches_file.exists) {
                html += '<div class="data-status error" style="margin-top: 20px;">';
                html += '<p>Sample data will be automatically created when you run your first backtest.</p>';
                html += '</div>';
            }
            
            detailsElement.innerHTML = html;
        }
        
        async function runBacktest() {
            const btn = document.getElementById('run-backtest-btn');
            btn.classList.add('loading');
            btn.disabled = true;
            
            document.getElementById('loading-overlay').classList.add('active');
            
            const config = {
                initial_bankroll: parseFloat(document.getElementById('initial-bankroll').value),
                max_kelly: parseFloat(document.getElementById('max-bet-size').value) / 100,
                min_edge: parseFloat(document.getElementById('min-edge').value) / 100,
                min_probability: parseFloat(document.getElementById('min-probability').value) / 100,
                use_kelly: document.getElementById('use-kelly').checked,
                start_date: document.getElementById('start-date').value,
                end_date: document.getElementById('end-date').value
            };
            
            try {
                const response = await fetch('/api/run-backtest', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(config)
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    displayResults(data);
                    displayHistory(data);
                    
                    // Switch to results tab
                    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                    document.querySelectorAll('.tab')[1].classList.add('active');
                    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                    document.getElementById('results-tab').classList.add('active');
                }
                
            } catch (error) {
                console.error('Backtest error:', error);
                alert('Error running backtest: ' + error.message);
            } finally {
                btn.classList.remove('loading');
                btn.disabled = false;
                document.getElementById('loading-overlay').classList.remove('active');
            }
        }
        
        function displayResults(data) {
            const summary = data.summary;
            const resultsContent = document.getElementById('results-content');
            
            let html = '<div class="summary-cards">';
            
            // Summary cards
            html += '<div class="summary-card">';
            html += '<h4>Total Bets</h4>';
            html += '<div class="value">' + summary.total_bets + '</div>';
            html += '</div>';
            
            html += '<div class="summary-card">';
            html += '<h4>Win Rate</h4>';
            html += '<div class="value">' + (summary.win_rate * 100).toFixed(1) + '%</div>';
            html += '</div>';
            
            html += '<div class="summary-card ' + (summary.total_profit >= 0 ? 'positive' : 'negative') + '">';
            html += '<h4>Total Profit</h4>';
            html += '<div class="value"> + summary.total_profit.toFixed(2) + '</div>';
            html += '</div>';
            
            html += '<div class="summary-card ' + (summary.roi >= 0 ? 'positive' : 'negative') + '">';
            html += '<h4>ROI</h4>';
            html += '<div class="value">' + summary.roi.toFixed(1) + '%</div>';
            html += '</div>';
            
            html += '<div class="summary-card">';
            html += '<h4>Final Bankroll</h4>';
            html += '<div class="value"> + summary.final_bankroll.toFixed(2) + '</div>';
            html += '</div>';
            
            html += '<div class="summary-card">';
            html += '<h4>Avg Bet Size</h4>';
            html += '<div class="value"> + summary.avg_bet_size.toFixed(2) + '</div>';
            html += '</div>';
            
            html += '</div>';
            
            // Charts
            html += '<div class="chart-container">';
            html += '<h3>Bankroll Growth</h3>';
            html += '<canvas id="bankroll-chart"></canvas>';
            html += '</div>';
            
            html += '<div class="chart-container">';
            html += '<h3>Win Rate Over Time</h3>';
            html += '<canvas id="winrate-chart"></canvas>';
            html += '</div>';
            
            html += '<div class="chart-container">';
            html += '<h3>Profit Distribution</h3>';
            html += '<canvas id="profit-chart"></canvas>';
            html += '</div>';
            
            resultsContent.innerHTML = html;
            
            // Create charts
            setTimeout(() => {
                createBankrollChart(data.charts.bankroll);
                createWinrateChart(data.charts.winrate);
                createProfitChart(data.charts.profit_distribution);
            }, 100);
        }
        
        function displayHistory(data) {
            const historyContent = document.getElementById('history-content');
            const bets = data.bets || [];
            
            if (bets.length === 0) {
                historyContent.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">No bets placed in this backtest.</p>';
                return;
            }
            
            let html = '<div class="bets-table"><table>';
            html += '<thead><tr>';
            html += '<th>Date</th>';
            html += '<th>Match</th>';
            html += '<th>Bet On</th>';
            html += '<th>Odds</th>';
            html += '<th>Probability</th>';
            html += '<th>Edge</th>';
            html += '<th>Bet Size</th>';
            html += '<th>Outcome</th>';
            html += '<th>Profit</th>';
            html += '</tr></thead><tbody>';
            
            bets.reverse().forEach(bet => {
                const outcomeClass = bet.outcome === 'Win' ? 'outcome-win' : 'outcome-loss';
                const profitClass = bet.profit >= 0 ? 'profit-positive' : 'profit-negative';
                
                html += '<tr>';
                html += '<td>' + new Date(bet.date).toLocaleDateString() + '</td>';
                html += '<td>' + bet.team1 + ' vs ' + bet.team2 + '</td>';
                html += '<td>' + bet.bet_on + '</td>';
                html += '<td>' + bet.odds.toFixed(2) + '</td>';
                html += '<td>' + (bet.probability * 100).toFixed(1) + '%</td>';
                html += '<td>' + (bet.edge * 100).toFixed(1) + '%</td>';
                html += '<td> + bet.bet_size.toFixed(2) + '</td>';
                html += '<td class="' + outcomeClass + '">' + bet.outcome + '</td>';
                html += '<td class="' + profitClass + '"> + bet.profit.toFixed(2) + '</td>';
                html += '</tr>';
            });
            
            html += '</tbody></table></div>';
            historyContent.innerHTML = html;
        }
        
        function createBankrollChart(data) {
            const ctx = document.getElementById('bankroll-chart').getContext('2d');
            
            if (bankrollChart) {
                bankrollChart.destroy();
            }
            
            bankrollChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Bankroll',
                        data: data.data,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return ' + value.toFixed(0);
                                }
                            }
                        }
                    }
                }
            });
        }
        
        function createWinrateChart(data) {
            const ctx = document.getElementById('winrate-chart').getContext('2d');
            
            if (winrateChart) {
                winrateChart.destroy();
            }
            
            winrateChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Win Rate %',
                        data: data.data,
                        borderColor: '#43a047',
                        backgroundColor: 'rgba(67, 160, 71, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
        
        function createProfitChart(data) {
            const ctx = document.getElementById('profit-chart').getContext('2d');
            
            if (profitChart) {
                profitChart.destroy();
            }
            
            profitChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Number of Bets',
                        data: data.data,
                        backgroundColor: [
                            '#e53935',
                            '#ef5350',
                            '#ff7043',
                            '#66bb6a',
                            '#43a047',
                            '#2e7d32'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        }
    </script>
</body>
</html>''')
    html_template.close()
    
    # Now move it to templates folder
    if os.path.exists('backtesting_template.html'):
        with open('backtesting_template.html', 'r', encoding='utf-8') as src:
            content = src.read()
        with open('templates/backtesting.html', 'w', encoding='utf-8') as dst:
            dst.write(content)
        os.remove('backtesting_template.html')
        print("Created: templates/backtesting.html")
    
    print("\n✨ Setup complete! Your backtesting system is ready.")
    print("\nTo use it:")
    print("1. Make sure your Flask app includes the backtesting routes")
    print("2. Run your app: python app.py")
    print("3. Navigate to: http://localhost:5001/backtesting")
    print("\nNote: Sample data will be created automatically when you run your first backtest.")

if __name__ == "__main__":
    setup_backtesting()