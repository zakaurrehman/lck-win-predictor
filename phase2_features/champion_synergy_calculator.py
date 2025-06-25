# champion_synergy_calculator.py
import pandas as pd
import numpy as np
from itertools import combinations
import json

class ChampionSynergyCalculator:
    def __init__(self, matches_df):
        self.matches_df = matches_df
        self.synergy_matrix = {}
        self.counter_matrix = {}
        
    def calculate_all_synergies(self):
        """Calculate champion synergies and counters"""
        print("Calculating champion synergies...")
        
        # Calculate team synergies
        self.calculate_team_synergies()
        
        # Calculate lane counters
        self.calculate_lane_counters()
        
        # Calculate role synergies
        self.calculate_role_synergies()
        
        # Save results
        self.save_synergy_data()
        
    def calculate_team_synergies(self):
        """Calculate how well champion pairs work together"""
        pair_stats = {}
        
        for _, game in self.matches_df.iterrows():
            # Blue team combinations
            blue_champs = [game[f'blue_champ{i}'] for i in range(1, 6)]
            blue_won = game['blue_win'] == 1
            
            # Check all pairs
            for champ1, champ2 in combinations(blue_champs, 2):
                pair_key = tuple(sorted([champ1, champ2]))
                if pair_key not in pair_stats:
                    pair_stats[pair_key] = {'games': 0, 'wins': 0}
                
                pair_stats[pair_key]['games'] += 1
                if blue_won:
                    pair_stats[pair_key]['wins'] += 1
            
            # Red team combinations
            red_champs = [game[f'red_champ{i}'] for i in range(1, 6)]
            red_won = not blue_won
            
            for champ1, champ2 in combinations(red_champs, 2):
                pair_key = tuple(sorted([champ1, champ2]))
                if pair_key not in pair_stats:
                    pair_stats[pair_key] = {'games': 0, 'wins': 0}
                
                pair_stats[pair_key]['games'] += 1
                if red_won:
                    pair_stats[pair_key]['wins'] += 1
        
        # Calculate synergy scores
        for pair, stats in pair_stats.items():
            if stats['games'] >= 10:  # Minimum sample size
                winrate = stats['wins'] / stats['games']
                # Synergy score: how much better than average (0.5)
                synergy_score = (winrate - 0.5) * 2  # Scale to [-1, 1]
                self.synergy_matrix[pair] = {
                    'synergy_score': synergy_score,
                    'winrate': winrate,
                    'games': stats['games']
                }
        
        print(f"✓ Calculated {len(self.synergy_matrix)} champion pair synergies")
        
    def calculate_lane_counters(self):
        """Calculate champion matchup statistics"""
        # Focus on 1v1 lanes (top, mid)
        lane_matchups = {}
        
        for _, game in self.matches_df.iterrows():
            # Top lane matchup
            blue_top = game['blue_champ1']  # Assuming position order
            red_top = game['red_champ1']
            blue_won = game['blue_win'] == 1
            
            matchup_key = (blue_top, red_top)
            if matchup_key not in lane_matchups:
                lane_matchups[matchup_key] = {'games': 0, 'wins': 0}
            
            lane_matchups[matchup_key]['games'] += 1
            if blue_won:
                lane_matchups[matchup_key]['wins'] += 1
            
            # Mid lane matchup
            blue_mid = game['blue_champ3']
            red_mid = game['red_champ3']
            
            matchup_key = (blue_mid, red_mid)
            if matchup_key not in lane_matchups:
                lane_matchups[matchup_key] = {'games': 0, 'wins': 0}
            
            lane_matchups[matchup_key]['games'] += 1
            if blue_won:
                lane_matchups[matchup_key]['wins'] += 1
        
        # Calculate counter scores
        for matchup, stats in lane_matchups.items():
            if stats['games'] >= 5:  # Lower threshold for matchups
                winrate = stats['wins'] / stats['games']
                self.counter_matrix[matchup] = {
                    'winrate': winrate,
                    'advantage': winrate - 0.5,
                    'games': stats['games']
                }
        
        print(f"✓ Calculated {len(self.counter_matrix)} lane matchups")
        
    def calculate_role_synergies(self):
        """Calculate synergies between specific roles"""
        role_combos = {
            'jungle_mid': (2, 3),  # Jungle-Mid synergy
            'bot_support': (4, 5),  # Bot-Support synergy
            'top_jungle': (1, 2),  # Top-Jungle synergy
        }
        
        self.role_synergies = {}
        
        for role_name, (pos1, pos2) in role_combos.items():
            combo_stats = {}
            
            for _, game in self.matches_df.iterrows():
                # Blue side
                champ1 = game[f'blue_champ{pos1}']
                champ2 = game[f'blue_champ{pos2}']
                combo_key = tuple(sorted([champ1, champ2]))
                
                if combo_key not in combo_stats:
                    combo_stats[combo_key] = {'games': 0, 'wins': 0}
                
                combo_stats[combo_key]['games'] += 1
                if game['blue_win']:
                    combo_stats[combo_key]['wins'] += 1
                
                # Red side
                champ1 = game[f'red_champ{pos1}']
                champ2 = game[f'red_champ{pos2}']
                combo_key = tuple(sorted([champ1, champ2]))
                
                if combo_key not in combo_stats:
                    combo_stats[combo_key] = {'games': 0, 'wins': 0}
                
                combo_stats[combo_key]['games'] += 1
                if not game['blue_win']:
                    combo_stats[combo_key]['wins'] += 1
            
            # Calculate synergy scores
            role_synergy_data = {}
            for combo, stats in combo_stats.items():
                if stats['games'] >= 10:
                    winrate = stats['wins'] / stats['games']
                    role_synergy_data[combo] = {
                        'winrate': winrate,
                        'games': stats['games'],
                        'synergy': winrate - 0.5
                    }
            
            self.role_synergies[role_name] = role_synergy_data
        
        print(f"✓ Calculated role-specific synergies")
    
    def save_synergy_data(self):
        """Save all synergy calculations"""
        # Save synergy matrix
        with open("data/enhanced/champion_synergies.json", 'w') as f:
            # Convert tuple keys to strings for JSON
            synergy_dict = {f"{c1}_{c2}": data for (c1, c2), data in self.synergy_matrix.items()}
            json.dump(synergy_dict, f, indent=2)
        
        # Save counter matrix
        with open("data/enhanced/champion_counters.json", 'w') as f:
            counter_dict = {f"{c1}_vs_{c2}": data for (c1, c2), data in self.counter_matrix.items()}
            json.dump(counter_dict, f, indent=2)
        
        # Save role synergies
        with open("data/enhanced/role_synergies.json", 'w') as f:
            role_dict = {}
            for role, synergies in self.role_synergies.items():
                role_dict[role] = {f"{c1}_{c2}": data for (c1, c2), data in synergies.items()}
            json.dump(role_dict, f, indent=2)
        
        # Create top synergies report
        top_synergies = sorted(self.synergy_matrix.items(), 
                              key=lambda x: x[1]['synergy_score'], 
                              reverse=True)[:20]
        
        print("\nTop 10 Champion Synergies:")
        for (c1, c2), data in top_synergies[:10]:
            print(f"  {c1} + {c2}: {data['winrate']:.1%} winrate ({data['games']} games)")

