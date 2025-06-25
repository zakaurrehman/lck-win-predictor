# patch_analyzer.py
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict 

class PatchAnalyzer:
    def __init__(self, matches_df):
        self.matches_df = matches_df
        self.patch_stats = {}
        
    def analyze_patches(self):
        """Analyze champion performance by patch"""
        print("Analyzing patch data...")
        
        # Group by patch
        for patch, patch_games in self.matches_df.groupby('patch'):
            if pd.isna(patch) or patch == '':
                continue
                
            self.patch_stats[patch] = {
                'games': len(patch_games),
                'date_range': (patch_games['date'].min(), patch_games['date'].max()),
                'champion_stats': self.calculate_champion_stats(patch_games),
                'blue_winrate': patch_games['blue_win'].mean()
            }
        
        # Save patch analysis
        self.save_patch_analysis()
        
    def calculate_champion_stats(self, games):
        """Calculate champion statistics for a specific patch"""
        champion_stats = defaultdict(lambda: {'picks': 0, 'wins': 0, 'bans': 0})
        
        for _, game in games.iterrows():
            # Process picks
            for i in range(1, 6):
                # Blue champions
                champ = game[f'blue_champ{i}']
                if champ:
                    champion_stats[champ]['picks'] += 1
                    if game['blue_win']:
                        champion_stats[champ]['wins'] += 1
                
                # Red champions
                champ = game[f'red_champ{i}']
                if champ:
                    champion_stats[champ]['picks'] += 1
                    if not game['blue_win']:
                        champion_stats[champ]['wins'] += 1
                
                # Bans
                blue_ban = game.get(f'blue_ban{i}', '')
                red_ban = game.get(f'red_ban{i}', '')
                if blue_ban:
                    champion_stats[blue_ban]['bans'] += 1
                if red_ban:
                    champion_stats[red_ban]['bans'] += 1
        
        # Calculate rates
        for champ, stats in champion_stats.items():
            stats['winrate'] = stats['wins'] / stats['picks'] if stats['picks'] > 0 else 0
            stats['presence'] = (stats['picks'] + stats['bans']) / (len(games) * 2)  # *2 for both teams
        
        return dict(champion_stats)
    
    def save_patch_analysis(self):
        """Save patch analysis results"""
        # Create summary DataFrame
        patch_summary = []
        for patch, data in self.patch_stats.items():
            patch_summary.append({
                'patch': patch,
                'games': data['games'],
                'start_date': data['date_range'][0],
                'end_date': data['date_range'][1],
                'blue_winrate': data['blue_winrate']
            })
        
        df = pd.DataFrame(patch_summary)
        df = df.sort_values('start_date', ascending=False)
        df.to_csv("data/enhanced/patch_summary.csv", index=False)
        
        # Save detailed patch data
        import json
        with open("data/enhanced/patch_champion_stats.json", 'w') as f:
            json.dump(self.patch_stats, f, indent=2, default=str)
        
        print(f"✓ Analyzed {len(df)} patches")
        print(f"✓ Recent patches:")
        print(df[['patch', 'games', 'blue_winrate']].head())