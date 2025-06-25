# player_stats_collector.py
import pandas as pd
import numpy as np
from collections import defaultdict

class PlayerStatsCalculator:
    def __init__(self, matches_df):
        self.matches_df = matches_df
        self.player_stats = defaultdict(lambda: {
            'games': 0,
            'wins': 0,
            'positions': defaultdict(int),
            'champions': defaultdict(int),
            'champion_wins': defaultdict(int),
            'recent_form': [],
            'elo': 1500  # Starting ELO
        })
        
    def calculate_all_stats(self):
        """Calculate comprehensive player statistics"""
        print("Calculating player statistics...")
        
        # Sort by date to process chronologically
        df = self.matches_df.sort_values('date')
        
        for idx, game in df.iterrows():
            self.process_game(game)
        
        # Calculate derived stats
        self.calculate_derived_stats()
        
        # Save player stats
        self.save_player_stats()
        
    def process_game(self, game):
        """Process a single game for player stats"""
        # Blue team
        blue_won = game['blue_win'] == 1
        positions = ['top', 'jng', 'mid', 'bot', 'sup']
        
        for i, pos in enumerate(positions):
            # Blue player
            player = game.get(f'blue_{pos}', '')
            if player:
                champ = game[f'blue_champ{i+1}']
                self.update_player_stats(player, pos, champ, blue_won, game['date'])
            
            # Red player
            player = game.get(f'red_{pos}', '')
            if player:
                champ = game[f'red_champ{i+1}']
                self.update_player_stats(player, pos, champ, not blue_won, game['date'])
    
    def update_player_stats(self, player, position, champion, won, date):
        """Update individual player statistics"""
        stats = self.player_stats[player]
        
        # Basic stats
        stats['games'] += 1
        if won:
            stats['wins'] += 1
        
        # Position stats
        stats['positions'][position] += 1
        
        # Champion stats
        stats['champions'][champion] += 1
        if won:
            stats['champion_wins'][champion] += 1
        
        # Recent form (last 10 games)
        stats['recent_form'].append((date, won))
        if len(stats['recent_form']) > 10:
            stats['recent_form'].pop(0)
        
        # Update ELO
        stats['elo'] = self.update_elo(stats['elo'], won)
    
    def update_elo(self, current_elo, won, k_factor=32):
        """Simple ELO calculation"""
        expected = 1 / (1 + 10 ** ((1500 - current_elo) / 400))
        actual = 1 if won else 0
        return current_elo + k_factor * (actual - expected)
    
    def calculate_derived_stats(self):
        """Calculate win rates and other derived statistics"""
        for player, stats in self.player_stats.items():
            # Overall win rate
            stats['winrate'] = stats['wins'] / stats['games'] if stats['games'] > 0 else 0
            
            # Main position
            if stats['positions']:
                stats['main_position'] = max(stats['positions'].items(), key=lambda x: x[1])[0]
            
            # Champion pool size
            stats['champion_pool'] = len(stats['champions'])
            
            # Best champions (by games played)
            champ_games = [(c, g) for c, g in stats['champions'].items()]
            stats['top_champions'] = sorted(champ_games, key=lambda x: x[1], reverse=True)[:5]
            
            # Recent form win rate
            recent_wins = sum(1 for _, won in stats['recent_form'] if won)
            stats['recent_winrate'] = recent_wins / len(stats['recent_form']) if stats['recent_form'] else 0
    
    def save_player_stats(self):
        """Save player statistics to file"""
        # Convert to DataFrame
        players_data = []
        for player, stats in self.player_stats.items():
            players_data.append({
                'player': player,
                'games': stats['games'],
                'wins': stats['wins'],
                'winrate': stats['winrate'],
                'elo': stats['elo'],
                'main_position': stats.get('main_position', ''),
                'champion_pool': stats['champion_pool'],
                'recent_winrate': stats['recent_winrate']
            })
        
        df = pd.DataFrame(players_data)
        df = df.sort_values('games', ascending=False)
        df.to_csv("data/enhanced/player_stats.csv", index=False)
        
        print(f"✓ Calculated stats for {len(df)} players")
        print(f"✓ Top 10 players by games:")
        print(df[['player', 'games', 'winrate', 'elo']].head(10))
        
        # Also save detailed stats as JSON for later use
        import json
        with open("data/enhanced/player_stats_detailed.json", 'w') as f:
            json.dump(dict(self.player_stats), f, indent=2, default=str)