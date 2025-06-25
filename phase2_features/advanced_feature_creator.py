# advanced_feature_creator.py
import pandas as pd
import numpy as np
import json
from phase2_features.team_composition_analyzer import TeamCompositionAnalyzer
import os

class AdvancedFeatureCreator:
    def __init__(self):
        # Load all calculated data
        self.load_enhanced_data()
        
    def load_enhanced_data(self):
        """Load all pre-calculated data"""
        # Champion synergies
        with open("data/enhanced/champion_synergies.json", 'r') as f:
            self.synergies = json.load(f)
        
        # Champion counters
        with open("data/enhanced/champion_counters.json", 'r') as f:
            self.counters = json.load(f)
        
        # Player stats
        self.player_stats = pd.read_csv("data/enhanced/player_stats.csv")
        self.player_dict = dict(zip(self.player_stats['player'], 
                                   self.player_stats['elo']))
        
        # Team matchup history
        self.team_matchups = pd.read_csv("data/enhanced/team_matchup_history.csv")
        
        # Recent form
        self.recent_form = pd.read_csv("data/enhanced/team_recent_form.csv")
        
        # Team composition analyzer
        self.comp_analyzer = TeamCompositionAnalyzer()
        
    def create_game_features(self, game_row):
        """Create all advanced features for a game"""
        features = {}
        
        # 1. Basic features (keep original)
        features['blue_side'] = 1
        
        # 2. Champion synergy features
        blue_synergy = self.calculate_team_synergy([
            game_row[f'blue_champ{i}'] for i in range(1, 6)
        ])
        red_synergy = self.calculate_team_synergy([
            game_row[f'red_champ{i}'] for i in range(1, 6)
        ])
        
        features['blue_synergy_score'] = blue_synergy
        features['red_synergy_score'] = red_synergy
        features['synergy_diff'] = blue_synergy - red_synergy
        
        # 3. Lane matchup advantages
        matchup_advantages = self.calculate_matchup_advantages(game_row)
        features.update(matchup_advantages)
        
        # 4. Player skill features
        player_features = self.calculate_player_features(game_row)
        features.update(player_features)
        
        # 5. Team composition features
        blue_comp = self.comp_analyzer.analyze_team_composition([
            game_row[f'blue_champ{i}'] for i in range(1, 6)
        ])
        red_comp = self.comp_analyzer.analyze_team_composition([
            game_row[f'red_champ{i}'] for i in range(1, 6)
        ])
        
        # Add composition differences
        for key in blue_comp:
            features[f'blue_{key}'] = blue_comp[key]
            features[f'red_{key}'] = red_comp[key]
            features[f'{key}_diff'] = blue_comp[key] - red_comp[key]
        
        # 6. Historical matchup features
        if 'blue_team' in game_row and 'red_team' in game_row:
            matchup_features = self.get_matchup_history(
                game_row['blue_team'], 
                game_row['red_team']
            )
            features.update(matchup_features)
        
        # 7. Recent form features
        if 'blue_team' in game_row and 'red_team' in game_row:
            form_features = self.get_recent_form_features(
                game_row['blue_team'],
                game_row['red_team']
            )
            features.update(form_features)
        
        # 8. Patch meta features (if available)
        if 'patch' in game_row:
            features['patch_number'] = self.encode_patch(game_row['patch'])
        
        return features
    
    def calculate_team_synergy(self, champions):
        """Calculate total team synergy score"""
        total_synergy = 0
        pairs_checked = 0
        
        for i in range(len(champions)):
            for j in range(i+1, len(champions)):
                pair_key = f"{champions[i]}_{champions[j]}"
                pair_key_alt = f"{champions[j]}_{champions[i]}"
                
                if pair_key in self.synergies:
                    total_synergy += self.synergies[pair_key]['synergy_score']
                    pairs_checked += 1
                elif pair_key_alt in self.synergies:
                    total_synergy += self.synergies[pair_key_alt]['synergy_score']
                    pairs_checked += 1
        
        return total_synergy / pairs_checked if pairs_checked > 0 else 0
    
    def calculate_matchup_advantages(self, game_row):
        """Calculate lane matchup advantages"""
        features = {}
        
        # Top lane matchup
        top_matchup = f"{game_row['blue_champ1']}_vs_{game_row['red_champ1']}"
        if top_matchup in self.counters:
            features['top_lane_advantage'] = self.counters[top_matchup]['advantage']
        else:
            features['top_lane_advantage'] = 0
        
        # Mid lane matchup
        mid_matchup = f"{game_row['blue_champ3']}_vs_{game_row['red_champ3']}"
        if mid_matchup in self.counters:
            features['mid_lane_advantage'] = self.counters[mid_matchup]['advantage']
        else:
            features['mid_lane_advantage'] = 0
        
        # Bot lane 2v2 is more complex, simplified here
        features['bot_lane_advantage'] = 0
        
        return features
    
    def calculate_player_features(self, game_row):
        """Calculate player skill features"""
        features = {}
        positions = ['top', 'jng', 'mid', 'bot', 'sup']
        
        blue_elos = []
        red_elos = []
        
        for pos in positions:
            blue_player = game_row.get(f'blue_{pos}', '')
            red_player = game_row.get(f'red_{pos}', '')
            
            blue_elo = self.player_dict.get(blue_player, 1500)
            red_elo = self.player_dict.get(red_player, 1500)
            
            blue_elos.append(blue_elo)
            red_elos.append(red_elo)
            
            features[f'{pos}_elo_diff'] = blue_elo - red_elo
        
        features['avg_elo_diff'] = np.mean(blue_elos) - np.mean(red_elos)
        features['blue_team_avg_elo'] = np.mean(blue_elos)
        features['red_team_avg_elo'] = np.mean(red_elos)
        
        return features
    
    def get_matchup_history(self, blue_team, red_team):
        """Get historical matchup between teams"""
        features = {}
        
        # Find matchup
        matchup = self.team_matchups[
            ((self.team_matchups['team1'] == blue_team) & 
             (self.team_matchups['team2'] == red_team)) |
            ((self.team_matchups['team1'] == red_team) & 
             (self.team_matchups['team2'] == blue_team))
        ]
        
        if len(matchup) > 0:
            matchup = matchup.iloc[0]
            if matchup['team1'] == blue_team:
                features['historical_matchup_winrate'] = matchup['team1_winrate']
            else:
                features['historical_matchup_winrate'] = 1 - matchup['team1_winrate']
            features['historical_matchup_games'] = matchup['games']
        else:
            features['historical_matchup_winrate'] = 0.5
            features['historical_matchup_games'] = 0
        
        return features
    
    def get_recent_form_features(self, blue_team, red_team):
        """Get recent form for both teams"""
        features = {}
        
        blue_form = self.recent_form[self.recent_form['team'] == blue_team]
        red_form = self.recent_form[self.recent_form['team'] == red_team]
        
        if len(blue_form) > 0:
            features['blue_recent_winrate'] = blue_form.iloc[0]['recent_winrate']
            features['blue_recent_games'] = blue_form.iloc[0]['recent_games']
        else:
            features['blue_recent_winrate'] = 0.5
            features['blue_recent_games'] = 0
        
        if len(red_form) > 0:
            features['red_recent_winrate'] = red_form.iloc[0]['recent_winrate']
            features['red_recent_games'] = red_form.iloc[0]['recent_games']
        else:
            features['red_recent_winrate'] = 0.5
            features['red_recent_games'] = 0
        
        features['recent_form_diff'] = features['blue_recent_winrate'] - features['red_recent_winrate']
        
        return features
    
    def encode_patch(self, patch):
        """Convert patch string to numeric value"""
        try:
            # Convert "13.24" to 13.24
            return float(patch.replace('Patch ', ''))
        except:
            return 0