# matchup_history_analyzer.py
import pandas as pd
import numpy as np
from collections import defaultdict

class MatchupHistoryAnalyzer:
    def __init__(self, matches_df):
        self.matches_df = matches_df
        self.team_matchups = defaultdict(lambda: {'games': 0, 'wins': 0})
        self.player_matchups = defaultdict(lambda: {'games': 0, 'wins': 0})
        
    def analyze_all_matchups(self):
        """Analyze historical matchups"""
        print("Analyzing historical matchups...")
        
        # Team vs Team history
        self.analyze_team_matchups()
        
        # Player vs Player history
        self.analyze_player_matchups()
        
        # Recent form
        self.analyze_recent_form()
        
        # Save results
        self.save_matchup_data()
        
    def analyze_team_matchups(self):
        """Analyze team vs team historical performance"""
        for _, game in self.matches_df.iterrows():
            blue_team = game['blue_team']
            red_team = game['red_team']
            blue_won = game['blue_win'] == 1
            
            # Create matchup key (alphabetical order)
            matchup_key = tuple(sorted([blue_team, red_team]))
            
            self.team_matchups[matchup_key]['games'] += 1
            if (matchup_key[0] == blue_team and blue_won) or \
               (matchup_key[1] == blue_team and not blue_won):
                self.team_matchups[matchup_key]['wins'] += 1
        
        print(f"✓ Analyzed {len(self.team_matchups)} team matchups")
    
    def analyze_player_matchups(self):
        """Analyze player vs player matchups in same role"""
        positions = ['top', 'jng', 'mid', 'bot', 'sup']
        
        for _, game in self.matches_df.iterrows():
            for pos in positions:
                blue_player = game.get(f'blue_{pos}', '')
                red_player = game.get(f'red_{pos}', '')
                
                if blue_player and red_player:
                    matchup_key = (blue_player, red_player, pos)
                    self.player_matchups[matchup_key]['games'] += 1
                    
                    if game['blue_win']:
                        self.player_matchups[matchup_key]['wins'] += 1
    
    def analyze_recent_form(self):
        """Analyze recent team and player form"""
        # Sort by date
        df = self.matches_df.sort_values('date', ascending=False)
        
        # Get last 30 days of games for each team
        self.recent_team_form = {}
        self.recent_player_form = {}
        
        recent_date = df['date'].max() - pd.Timedelta(days=30)
        recent_games = df[df['date'] > recent_date]
        
        # Team form
        for team in set(recent_games['blue_team'].unique()) | set(recent_games['red_team'].unique()):
            team_games = recent_games[
                (recent_games['blue_team'] == team) | 
                (recent_games['red_team'] == team)
            ]
            
            wins = sum(
                (team_games['blue_team'] == team) & (team_games['blue_win'] == 1)
            ) + sum(
                (team_games['red_team'] == team) & (team_games['blue_win'] == 0)
            )
            
            self.recent_team_form[team] = {
                'games': len(team_games),
                'wins': wins,
                'winrate': wins / len(team_games) if len(team_games) > 0 else 0
            }
    
    def save_matchup_data(self):
        """Save matchup analysis"""
        # Team matchups
        team_matchup_data = []
        for (team1, team2), stats in self.team_matchups.items():
            if stats['games'] >= 3:  # Minimum games
                team_matchup_data.append({
                    'team1': team1,
                    'team2': team2,
                    'games': stats['games'],
                    'team1_winrate': stats['wins'] / stats['games']
                })
        
        df_team_matchups = pd.DataFrame(team_matchup_data)
        df_team_matchups.to_csv("data/enhanced/team_matchup_history.csv", index=False)
        
        # Recent form
        recent_form_data = []
        for team, stats in self.recent_team_form.items():
            recent_form_data.append({
                'team': team,
                'recent_games': stats['games'],
                'recent_wins': stats['wins'],
                'recent_winrate': stats['winrate']
            })
        
        df_recent = pd.DataFrame(recent_form_data)
        df_recent.to_csv("data/enhanced/team_recent_form.csv", index=False)
        
        print(f"✓ Saved matchup history and recent form data")