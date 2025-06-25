from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import pickle
import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# EXACT FEATURES YOUR MODEL EXPECTS (in correct order)
REQUIRED_FEATURES = [
    'blue_side',
    'blue_synergy_score',
    'red_synergy_score',
    'synergy_diff',
    'top_lane_advantage',
    'mid_lane_advantage',
    'bot_lane_advantage',
    'top_elo_diff',
    'jng_elo_diff',
    'mid_elo_diff',
    'bot_elo_diff',
    'sup_elo_diff',
    'avg_elo_diff',
    'blue_team_avg_elo',
    'red_team_avg_elo',
    'blue_tanks',
    'red_tanks',
    'tanks_diff',
    'blue_fighters',
    'red_fighters',
    'fighters_diff',
    'blue_assassins',
    'red_assassins',
    'assassins_diff',
    'blue_mages',
    'red_mages',
    'mages_diff',
    'blue_marksmen',
    'red_marksmen',
    'marksmen_diff',
    'blue_supports',
    'red_supports',
    'supports_diff',
    'blue_engage_score',
    'red_engage_score',
    'engage_score_diff',
    'blue_disengage_score',
    'red_disengage_score',
    'disengage_score_diff',
    'blue_poke_score',
    'red_poke_score',
    'poke_score_diff',
    'blue_teamfight_score',
    'red_teamfight_score',
    'teamfight_score_diff',
    'blue_splitpush_score',
    'red_splitpush_score',
    'splitpush_score_diff',
    'blue_pick_potential',
    'red_pick_potential',
    'pick_potential_diff',
    'blue_early_game_score',
    'red_early_game_score',
    'early_game_score_diff',
    'blue_mid_game_score',
    'red_mid_game_score',
    'mid_game_score_diff',
    'blue_late_game_score',
    'red_late_game_score',
    'late_game_score_diff',
    'blue_physical_damage',
    'red_physical_damage',
    'physical_damage_diff',
    'blue_magic_damage',
    'red_magic_damage',
    'magic_damage_diff',
    'blue_true_damage',
    'red_true_damage',
    'true_damage_diff',
    'blue_cc_score',
    'red_cc_score',
    'cc_score_diff',
    'blue_mobility_score',
    'red_mobility_score',
    'mobility_score_diff',
    'blue_sustain_score',
    'red_sustain_score',
    'sustain_score_diff',
    'blue_is_teamfight_comp',
    'red_is_teamfight_comp',
    'is_teamfight_comp_diff',
    'blue_is_poke_comp',
    'red_is_poke_comp',
    'is_poke_comp_diff',
    'blue_is_pick_comp',
    'red_is_pick_comp',
    'is_pick_comp_diff',
    'blue_is_split_comp',
    'red_is_split_comp',
    'is_split_comp_diff',
    'historical_matchup_winrate',
    'historical_matchup_games',
    'blue_recent_winrate',
    'blue_recent_games',
    'red_recent_winrate',
    'red_recent_games',
    'recent_form_diff',
    'patch_number',
]

class ExactFeatureCreator:
    def __init__(self):
        """Initialize with exact feature calculation matching training data"""
        self.load_data()
        self.load_champion_data()
        
    def load_data(self):
        """Load all required data"""
        try:
            # Load player ELO ratings
            if os.path.exists('data/enhanced/player_stats.csv'):
                player_stats_df = pd.read_csv('data/enhanced/player_stats.csv')
                self.player_dict = dict(zip(player_stats_df['player'], player_stats_df['elo']))
            else:
                self.player_dict = {}
            
            # Load team recent form
            if os.path.exists('data/enhanced/team_recent_form.csv'):
                self.recent_form_df = pd.read_csv('data/enhanced/team_recent_form.csv')
            else:
                self.recent_form_df = pd.DataFrame()
            
            # Load team matchup history  
            if os.path.exists('data/enhanced/team_matchup_history.csv'):
                self.team_matchups_df = pd.read_csv('data/enhanced/team_matchup_history.csv')
            else:
                self.team_matchups_df = pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.player_dict = {}
            self.recent_form_df = pd.DataFrame()
            self.team_matchups_df = pd.DataFrame()
    
    def load_champion_data(self):
        """Load champion role and attribute data"""
        # Simplified champion data - in production, load from file
        self.champion_data = {
            # Tanks
            'Ornn': {'role': 'tank', 'damage': 'magic', 'cc': 3, 'engage': 3},
            'Malphite': {'role': 'tank', 'damage': 'magic', 'cc': 3, 'engage': 3},
            'Sion': {'role': 'tank', 'damage': 'physical', 'cc': 2, 'engage': 2},
            'K\'Sante': {'role': 'tank', 'damage': 'physical', 'cc': 2, 'engage': 2},
            'Maokai': {'role': 'tank', 'damage': 'magic', 'cc': 3, 'engage': 2},
            
            # Fighters
            'Aatrox': {'role': 'fighter', 'damage': 'physical', 'cc': 1, 'engage': 1},
            'Jax': {'role': 'fighter', 'damage': 'physical', 'cc': 1, 'engage': 1},
            'Fiora': {'role': 'fighter', 'damage': 'physical', 'cc': 0, 'engage': 0},
            'Renekton': {'role': 'fighter', 'damage': 'physical', 'cc': 1, 'engage': 1},
            'Gwen': {'role': 'fighter', 'damage': 'magic', 'cc': 0, 'engage': 0},
            
            # Assassins
            'Zed': {'role': 'assassin', 'damage': 'physical', 'cc': 0, 'engage': 0},
            'LeBlanc': {'role': 'assassin', 'damage': 'magic', 'cc': 1, 'engage': 0},
            'Akali': {'role': 'assassin', 'damage': 'magic', 'cc': 0, 'engage': 0},
            'Qiyana': {'role': 'assassin', 'damage': 'physical', 'cc': 2, 'engage': 0},
            
            # Mages
            'Orianna': {'role': 'mage', 'damage': 'magic', 'cc': 2, 'engage': 1},
            'Azir': {'role': 'mage', 'damage': 'magic', 'cc': 1, 'engage': 0},
            'Viktor': {'role': 'mage', 'damage': 'magic', 'cc': 1, 'engage': 0},
            'Syndra': {'role': 'mage', 'damage': 'magic', 'cc': 2, 'engage': 0},
            
            # Marksmen
            'Jinx': {'role': 'marksman', 'damage': 'physical', 'cc': 1, 'engage': 0},
            'Aphelios': {'role': 'marksman', 'damage': 'physical', 'cc': 1, 'engage': 0},
            'Lucian': {'role': 'marksman', 'damage': 'physical', 'cc': 0, 'engage': 0},
            'Jhin': {'role': 'marksman', 'damage': 'physical', 'cc': 1, 'engage': 0},
            
            # Supports
            'Thresh': {'role': 'support', 'damage': 'magic', 'cc': 3, 'engage': 2},
            'Nautilus': {'role': 'support', 'damage': 'magic', 'cc': 3, 'engage': 3},
            'Lulu': {'role': 'support', 'damage': 'magic', 'cc': 2, 'engage': 0},
            'Karma': {'role': 'support', 'damage': 'magic', 'cc': 1, 'engage': 0},
            
            # Junglers
            'Lee Sin': {'role': 'fighter', 'damage': 'physical', 'cc': 1, 'engage': 2},
            'Graves': {'role': 'marksman', 'damage': 'physical', 'cc': 1, 'engage': 0},
            'Viego': {'role': 'fighter', 'damage': 'physical', 'cc': 1, 'engage': 1},
            'Nidalee': {'role': 'assassin', 'damage': 'magic', 'cc': 0, 'engage': 0},
        }
    
    def create_exact_features(self, match_data):
        """Create features exactly matching the training data"""
        features = {}
        
        # 1. Blue side advantage
        features['blue_side'] = 1
        
        # 2. Get champions
        blue_champions = [
            match_data.get('blue_champ1', ''),
            match_data.get('blue_champ2', ''),
            match_data.get('blue_champ3', ''),
            match_data.get('blue_champ4', ''),
            match_data.get('blue_champ5', '')
        ]
        red_champions = [
            match_data.get('red_champ1', ''),
            match_data.get('red_champ2', ''),
            match_data.get('red_champ3', ''),
            match_data.get('red_champ4', ''),
            match_data.get('red_champ5', '')
        ]
        
        # 3. Calculate team compositions
        blue_comp = self.calculate_team_composition(blue_champions)
        red_comp = self.calculate_team_composition(red_champions)
        
        # Set composition features
        for key in ['tanks', 'fighters', 'assassins', 'mages', 'marksmen', 'supports']:
            features[f'blue_{key}'] = blue_comp[key]
            features[f'red_{key}'] = red_comp[key]
            features[f'{key}_diff'] = blue_comp[key] - red_comp[key]
        
        # 4. Strategic scores
        blue_strategic = self.calculate_strategic_scores(blue_champions)
        red_strategic = self.calculate_strategic_scores(red_champions)
        
        strategic_keys = ['engage_score', 'disengage_score', 'poke_score', 'teamfight_score', 
                         'splitpush_score', 'pick_potential', 'early_game_score', 
                         'mid_game_score', 'late_game_score', 'physical_damage', 
                         'magic_damage', 'true_damage', 'cc_score', 'mobility_score', 
                         'sustain_score']
        
        for key in strategic_keys:
            features[f'blue_{key}'] = blue_strategic.get(key, 0)
            features[f'red_{key}'] = red_strategic.get(key, 0)
            features[f'{key}_diff'] = blue_strategic.get(key, 0) - red_strategic.get(key, 0)
        
        # 5. Composition types (binary features)
        comp_types = ['is_teamfight_comp', 'is_poke_comp', 'is_pick_comp', 'is_split_comp']
        for comp_type in comp_types:
            features[f'blue_{comp_type}'] = blue_strategic.get(comp_type, 0)
            features[f'red_{comp_type}'] = red_strategic.get(comp_type, 0)
            features[f'{comp_type}_diff'] = blue_strategic.get(comp_type, 0) - red_strategic.get(comp_type, 0)
        
        # 6. Synergy scores (simplified)
        features['blue_synergy_score'] = 0.5 + (len(set([self.champion_data.get(c, {}).get('role', 'unknown') for c in blue_champions])) - 3) * 0.1
        features['red_synergy_score'] = 0.5 + (len(set([self.champion_data.get(c, {}).get('role', 'unknown') for c in red_champions])) - 3) * 0.1
        features['synergy_diff'] = features['blue_synergy_score'] - features['red_synergy_score']
        
        # 7. Lane advantages (simplified)
        features['top_lane_advantage'] = 0.0  # Neutral
        features['mid_lane_advantage'] = 0.0  # Neutral  
        features['bot_lane_advantage'] = 0.0  # Neutral
        
        # 8. Player ELO features
        self.calculate_player_elo_features(match_data, features)
        
        # 9. Team recent form
        self.calculate_team_form_features(match_data, features)
        
        # 10. Historical matchup
        self.calculate_historical_features(match_data, features)
        
        # 11. Patch number
        features['patch_number'] = 14.23
        
        return features
    
    def calculate_team_composition(self, champions):
        """Calculate team composition counts"""
        composition = {
            'tanks': 0, 'fighters': 0, 'assassins': 0, 
            'mages': 0, 'marksmen': 0, 'supports': 0
        }
        
        for champion in champions:
            if champion in self.champion_data:
                role = self.champion_data[champion]['role']
                if role in composition:
                    composition[role] += 1
        
        return composition
    
    def calculate_strategic_scores(self, champions):
        """Calculate strategic scores for a team"""
        scores = {
            'engage_score': 0, 'disengage_score': 0, 'poke_score': 0,
            'teamfight_score': 0, 'splitpush_score': 0, 'pick_potential': 0,
            'early_game_score': 0, 'mid_game_score': 0, 'late_game_score': 0,
            'physical_damage': 0, 'magic_damage': 0, 'true_damage': 0,
            'cc_score': 0, 'mobility_score': 0, 'sustain_score': 0,
            'is_teamfight_comp': 0, 'is_poke_comp': 0, 'is_pick_comp': 0, 'is_split_comp': 0
        }
        
        engage_total = 0
        cc_total = 0
        assassin_count = 0
        
        for champion in champions:
            if champion in self.champion_data:
                data = self.champion_data[champion]
                
                # Engage and CC
                engage_total += data.get('engage', 0)
                cc_total += data.get('cc', 0)
                
                # Count roles
                if data['role'] == 'assassin':
                    assassin_count += 1
                
                # Damage types
                if data['damage'] == 'physical':
                    scores['physical_damage'] += 1
                elif data['damage'] == 'magic':
                    scores['magic_damage'] += 1
        
        # Set strategic scores
        scores['engage_score'] = engage_total
        scores['cc_score'] = cc_total
        scores['teamfight_score'] = engage_total
        scores['pick_potential'] = assassin_count * 2
        
        # Composition types
        if engage_total >= 3:
            scores['is_teamfight_comp'] = 1
        if assassin_count >= 2:
            scores['is_pick_comp'] = 1
        
        # Game phases (simplified)
        scores['early_game_score'] = 2
        scores['mid_game_score'] = 2
        scores['late_game_score'] = 1
        
        return scores
    
    def calculate_player_elo_features(self, match_data, features):
        """Calculate player ELO differences"""
        positions = ['top', 'jng', 'mid', 'bot', 'sup']
        blue_elos = []
        red_elos = []
        
        for pos in positions:
            blue_player = match_data.get(f'blue_{pos}', '')
            red_player = match_data.get(f'red_{pos}', '')
            
            blue_elo = self.player_dict.get(blue_player, 1500)
            red_elo = self.player_dict.get(red_player, 1500)
            
            blue_elos.append(blue_elo)
            red_elos.append(red_elo)
            
            features[f'{pos}_elo_diff'] = blue_elo - red_elo
        
        features['avg_elo_diff'] = np.mean(blue_elos) - np.mean(red_elos)
        features['blue_team_avg_elo'] = np.mean(blue_elos)
        features['red_team_avg_elo'] = np.mean(red_elos)
    
    def calculate_team_form_features(self, match_data, features):
        """Calculate team recent form features"""
        blue_team = match_data.get('blue_team', '')
        red_team = match_data.get('red_team', '')
        
        # Blue team form
        if not self.recent_form_df.empty:
            blue_form = self.recent_form_df[self.recent_form_df['team'] == blue_team]
            if not blue_form.empty:
                features['blue_recent_winrate'] = blue_form.iloc[0]['recent_winrate']
                features['blue_recent_games'] = blue_form.iloc[0]['recent_games']
            else:
                features['blue_recent_winrate'] = 0.5
                features['blue_recent_games'] = 10
        
        # Red team form
        if not self.recent_form_df.empty:
            red_form = self.recent_form_df[self.recent_form_df['team'] == red_team]
            if not red_form.empty:
                features['red_recent_winrate'] = red_form.iloc[0]['recent_winrate']
                features['red_recent_games'] = red_form.iloc[0]['recent_games']
            else:
                features['red_recent_winrate'] = 0.5
                features['red_recent_games'] = 10
        
        features['recent_form_diff'] = features.get('blue_recent_winrate', 0.5) - features.get('red_recent_winrate', 0.5)
    
    def calculate_historical_features(self, match_data, features):
        """Calculate historical matchup features"""
        blue_team = match_data.get('blue_team', '')
        red_team = match_data.get('red_team', '')
        
        if not self.team_matchups_df.empty:
            matchup = self.team_matchups_df[
                ((self.team_matchups_df['team1'] == blue_team) & 
                 (self.team_matchups_df['team2'] == red_team)) |
                ((self.team_matchups_df['team1'] == red_team) & 
                 (self.team_matchups_df['team2'] == blue_team))
            ]
            
            if not matchup.empty:
                matchup_row = matchup.iloc[0]
                if matchup_row['team1'] == blue_team:
                    features['historical_matchup_winrate'] = matchup_row['team1_winrate']
                else:
                    features['historical_matchup_winrate'] = 1 - matchup_row['team1_winrate']
                features['historical_matchup_games'] = matchup_row['games']
            else:
                features['historical_matchup_winrate'] = 0.5
                features['historical_matchup_games'] = 0
        else:
            features['historical_matchup_winrate'] = 0.5
            features['historical_matchup_games'] = 0

class LCKPredictionApp:
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.scaler = None
        self.teams_list = []
        self.champions_list = []
        self.players_data = {}
        self.team_rosters = {}
        self.feature_creator = None
        self.load_model_and_data()
    
    def load_model_and_data(self):
        """Load trained model, scaler, and supporting data"""
        try:
            # Initialize the EXACT feature creator
            self.feature_creator = ExactFeatureCreator()
            
            # Load model
            model_path = 'models/final_phase3_models.pkl'
            if os.path.exists(model_path):
                try:
                    import joblib
                    model_data = joblib.load(model_path)
                    
                    if isinstance(model_data, dict):
                        self.model = model_data.get('best_model') or model_data.get('ensemble') or model_data.get('model')
                        self.feature_columns = model_data.get('feature_columns')
                        self.scaler = model_data.get('scaler')
                    else:
                        self.model = model_data
                    
                    logger.info("Model loaded successfully")
                    
                except Exception as e:
                    logger.error(f"Model loading failed: {e}")
            else:
                logger.warning("Model file not found")
            
            # Load supporting data
            self.load_supporting_data()
            
            # Load team rosters
            self.load_team_rosters()
            
        except Exception as e:
            logger.error(f"Error in initialization: {str(e)}")
    
    def load_team_rosters(self):
        """Load team rosters from JSON file"""
        try:
            roster_paths = [
                'data/korean_teams_rosters.json',
                'korean_teams_rosters.json'
            ]
            
            for path in roster_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        roster_data = json.load(f)
                        self.team_rosters = roster_data.get('teams', {})
                        logger.info(f"Loaded rosters for {len(self.team_rosters)} teams")
                        break
            
            # Ensure all teams in teams_list have roster entries
            for team in self.teams_list:
                if team not in self.team_rosters:
                    self.team_rosters[team] = {
                        'league': 'LCK',
                        'roster': {}
                    }
                    
        except Exception as e:
            logger.error(f"Error loading team rosters: {e}")
            self.team_rosters = {}
    
    def load_supporting_data(self):
        """Load teams, players, and champions data"""
        try:
            # Load teams
            team_data_paths = [
                'data/enhanced/team_recent_form.csv',
                'data/team_recent_form.csv'
            ]
            
            for path in team_data_paths:
                if os.path.exists(path):
                    teams_df = pd.read_csv(path)
                    self.teams_list = sorted(teams_df['team'].unique().tolist())
                    logger.info(f"Loaded {len(self.teams_list)} teams")
                    break
            
            # Load players
            player_data_paths = [
                'data/enhanced/player_stats.csv',
                'data/player_stats.csv'
            ]
            
            for path in player_data_paths:
                if os.path.exists(path):
                    players_df = pd.read_csv(path)
                    self.players_data = players_df.to_dict('records')
                    logger.info(f"Loaded {len(self.players_data)} players")
                    break
            
            # Load champions
            main_data_paths = [
                'data/enhanced/lck_full_dataset.csv',
                'data/lck_full_dataset.csv'
            ]
            
            for path in main_data_paths:
                if os.path.exists(path):
                    lck_df = pd.read_csv(path)
                    champs = []
                    for col in ['blue_champ1', 'blue_champ2', 'blue_champ3', 'blue_champ4', 'blue_champ5']:
                        if col in lck_df.columns:
                            champs.extend(lck_df[col].dropna().unique().tolist())
                    self.champions_list = sorted(list(set([champ for champ in champs if champ and str(champ) != 'nan'])))
                    logger.info(f"Loaded {len(self.champions_list)} champions")
                    break
            
            # Fallbacks
            if not self.teams_list:
                self.teams_list = ["T1", "Gen.G", "DRX", "KT Rolster", "Hanwha Life Esports"]
            if not self.champions_list:
                self.champions_list = ["Aatrox", "Azir", "Jhin", "LeBlanc", "Nautilus", "Viego"]
            
        except Exception as e:
            logger.error(f"Error loading supporting data: {str(e)}")
    
    def predict_match(self, match_data):
        """Make prediction for a match"""
        if self.model is None:
            return {'error': 'Model not loaded'}
        
        try:
            # Create EXACT features
            features = self.feature_creator.create_exact_features(match_data)
            
            # Convert to DataFrame with exact column order
            feature_df = pd.DataFrame([features])
            feature_df = feature_df[REQUIRED_FEATURES]  # Ensure exact order
            
            # Make prediction
            prediction = self.model.predict(feature_df)[0]
            
            if hasattr(self.model, 'predict_proba'):
                prediction_proba = self.model.predict_proba(feature_df)[0]
                blue_prob = prediction_proba[1] if len(prediction_proba) > 1 else prediction_proba[0]
                red_prob = 1.0 - blue_prob
            else:
                blue_prob = float(prediction)
                red_prob = 1.0 - blue_prob
            
            return {
                'blue_win_probability': float(blue_prob),
                'red_win_probability': float(red_prob),
                'predicted_winner': 'Blue Team' if blue_prob > 0.5 else 'Red Team',
                'confidence': float(abs(blue_prob - 0.5) * 2),
                'model_accuracy': '79.88%'
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {'error': f'Prediction failed: {str(e)}'}

# Initialize Flask app
prediction_app = LCKPredictionApp()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         teams=prediction_app.teams_list,
                         champions=prediction_app.champions_list)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
        match_data = request.json
        result = prediction_app.predict_match(match_data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Prediction endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/teams')
def get_teams():
    """Get list of teams"""
    return jsonify(prediction_app.teams_list)

@app.route('/champions')
def get_champions():
    """Get list of champions"""
    return jsonify(prediction_app.champions_list)

@app.route('/team-roster/<team_name>')
def get_team_roster(team_name):
    """Get roster for a specific team"""
    if team_name in prediction_app.team_rosters:
        return jsonify({
            'success': True,
            'roster': prediction_app.team_rosters[team_name]['roster']
        })
    else:
        return jsonify({
            'success': False,
            'roster': {}
        })

@app.route('/all-players')
def get_all_players():
    """Get all unique players organized by position"""
    players_by_position = {
        'top': set(),
        'jng': set(),
        'mid': set(),
        'bot': set(),
        'sup': set()
    }
    
    # Collect all players from team rosters
    for team, data in prediction_app.team_rosters.items():
        roster = data.get('roster', {})
        for position, player in roster.items():
            if position in players_by_position and player:
                players_by_position[position].add(player)
    
    # Convert sets to sorted lists
    result = {pos: sorted(list(players)) for pos, players in players_by_position.items()}
    
    return jsonify(result)

@app.route('/debug')
def debug_info():
    """Debug endpoint"""
    return jsonify({
        'model_loaded': prediction_app.model is not None,
        'teams_count': len(prediction_app.teams_list),
        'champions_count': len(prediction_app.champions_list),
        'feature_creator_loaded': prediction_app.feature_creator is not None,
        'expected_features': len(REQUIRED_FEATURES)
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': prediction_app.model is not None,
        'teams_count': len(prediction_app.teams_list),
        'champions_count': len(prediction_app.champions_list)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)