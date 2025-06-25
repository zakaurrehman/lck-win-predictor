# team_composition_analyzer.py
import pandas as pd
import numpy as np




class TeamCompositionAnalyzer:
    def __init__(self):
        # Define champion roles and characteristics
        self.champion_roles = self.load_champion_roles()
        
    def load_champion_roles(self):
        """Load champion role classifications"""
        # In practice, load from a data file
        # This is a simplified example
        return {
            # Tanks
            'Ornn': {'primary_role': 'tank', 'secondary_role': 'engage', 'scaling': 'late'},
            'Malphite': {'primary_role': 'tank', 'secondary_role': 'engage', 'scaling': 'mid'},
            'Sion': {'primary_role': 'tank', 'secondary_role': 'waveclear', 'scaling': 'mid'},
            
            # Fighters
            'Aatrox': {'primary_role': 'fighter', 'secondary_role': 'sustain', 'scaling': 'mid'},
            'Fiora': {'primary_role': 'fighter', 'secondary_role': 'splitpush', 'scaling': 'late'},
            'Jax': {'primary_role': 'fighter', 'secondary_role': 'splitpush', 'scaling': 'late'},
            
            # Assassins
            'Zed': {'primary_role': 'assassin', 'secondary_role': 'burst', 'scaling': 'mid'},
            'LeBlanc': {'primary_role': 'assassin', 'secondary_role': 'burst', 'scaling': 'early'},
            'Khazix': {'primary_role': 'assassin', 'secondary_role': 'pick', 'scaling': 'mid'},
            
            # Mages
            'Orianna': {'primary_role': 'mage', 'secondary_role': 'control', 'scaling': 'late'},
            'Azir': {'primary_role': 'mage', 'secondary_role': 'dps', 'scaling': 'late'},
            'Viktor': {'primary_role': 'mage', 'secondary_role': 'waveclear', 'scaling': 'late'},
            
            # Marksmen
            'Jinx': {'primary_role': 'marksman', 'secondary_role': 'hypercarry', 'scaling': 'late'},
            'Lucian': {'primary_role': 'marksman', 'secondary_role': 'lane_bully', 'scaling': 'early'},
            'Aphelios': {'primary_role': 'marksman', 'secondary_role': 'utility', 'scaling': 'late'},
            
            # Supports
            'Thresh': {'primary_role': 'support', 'secondary_role': 'engage', 'scaling': 'all'},
            'Lulu': {'primary_role': 'support', 'secondary_role': 'enchanter', 'scaling': 'mid'},
            'Nautilus': {'primary_role': 'support', 'secondary_role': 'engage', 'scaling': 'early'},
            
            # Add more champions...
        }
    
    def analyze_team_composition(self, champions):
        """Analyze a team's composition and return features"""
        composition_features = {
            # Role distribution
            'tanks': 0,
            'fighters': 0,
            'assassins': 0,
            'mages': 0,
            'marksmen': 0,
            'supports': 0,
            
            # Team characteristics
            'engage_score': 0,
            'disengage_score': 0,
            'poke_score': 0,
            'teamfight_score': 0,
            'splitpush_score': 0,
            'pick_potential': 0,
            
            # Scaling
            'early_game_score': 0,
            'mid_game_score': 0,
            'late_game_score': 0,
            
            # Damage distribution
            'physical_damage': 0,
            'magic_damage': 0,
            'true_damage': 0,
            
            # Utility
            'cc_score': 0,
            'mobility_score': 0,
            'sustain_score': 0
        }
        
        for champ in champions:
            if champ in self.champion_roles:
                role_data = self.champion_roles[champ]
                
                # Count primary roles
                primary = role_data['primary_role']
                if primary in composition_features:
                    composition_features[primary] += 1
                
                # Add secondary role scores
                secondary = role_data['secondary_role']
                if secondary == 'engage':
                    composition_features['engage_score'] += 1
                    composition_features['cc_score'] += 1
                elif secondary == 'enchanter':
                    composition_features['disengage_score'] += 1
                    composition_features['sustain_score'] += 1
                elif secondary == 'burst':
                    composition_features['pick_potential'] += 1
                elif secondary == 'splitpush':
                    composition_features['splitpush_score'] += 1
                elif secondary == 'control':
                    composition_features['teamfight_score'] += 1
                    composition_features['cc_score'] += 1
                
                # Scaling scores
                scaling = role_data['scaling']
                if scaling == 'early':
                    composition_features['early_game_score'] += 1
                elif scaling == 'mid':
                    composition_features['mid_game_score'] += 1
                elif scaling == 'late':
                    composition_features['late_game_score'] += 1
                elif scaling == 'all':
                    composition_features['early_game_score'] += 0.5
                    composition_features['mid_game_score'] += 0.5
                    composition_features['late_game_score'] += 0.5
        
        # Calculate team composition type
        composition_features['is_teamfight_comp'] = int(
            composition_features['teamfight_score'] >= 3 and 
            composition_features['engage_score'] >= 2
        )
        composition_features['is_poke_comp'] = int(
            composition_features['poke_score'] >= 2 and
            composition_features['disengage_score'] >= 1
        )
        composition_features['is_pick_comp'] = int(
            composition_features['pick_potential'] >= 2 and
            composition_features['mobility_score'] >= 2
        )
        composition_features['is_split_comp'] = int(
            composition_features['splitpush_score'] >= 1 and
            composition_features['disengage_score'] >= 2
        )
        
        return composition_features
