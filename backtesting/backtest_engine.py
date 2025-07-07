# backtesting/backtest_engine.py
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
