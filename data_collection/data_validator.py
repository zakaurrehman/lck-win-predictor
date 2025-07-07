


# data_collection/data_validator.py
"""
Validate and clean collected data
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple

class DataValidator:
    """Validate and clean betting/match data"""
    
    def __init__(self):
        self.known_teams = [
            'T1', 'Gen.G', 'DRX', 'KT Rolster', 'Hanwha Life Esports',
            'Kwangdong Freecs', 'Nongshim RedForce', 'DWG KIA', 'Liiv SANDBOX',
            'Samsung Galaxy', 'SK Telecom T1', 'Longzhu Gaming', 'Afreeca Freecs'
        ]
    
    def validate_odds_data(self, odds_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Validate and clean odds data"""
        issues = []
        
        # Check for required columns
        required_columns = ['team1', 'team2', 'commence_time']
        missing_columns = [col for col in required_columns if col not in odds_df.columns]
        if missing_columns:
            issues.append(f"Missing columns: {missing_columns}")
            return odds_df, issues
        
        # Clean team names
        odds_df['team1'] = odds_df['team1'].apply(self.clean_team_name)
        odds_df['team2'] = odds_df['team2'].apply(self.clean_team_name)
        
        # Remove rows with unknown teams
        initial_rows = len(odds_df)
        odds_df = odds_df[
            (odds_df['team1'].isin(self.known_teams)) & 
            (odds_df['team2'].isin(self.known_teams))
        ]
        removed_rows = initial_rows - len(odds_df)
        if removed_rows > 0:
            issues.append(f"Removed {removed_rows} rows with unknown teams")
        
        # Validate odds values
        if 'odds_data' in odds_df.columns:
            # Check for realistic odds (between 1.01 and 50.0)
            # This depends on your odds format
            pass
        
        return odds_df, issues
    
    def validate_match_data(self, matches_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Validate and clean match data"""
        issues = []
        
        # Check for required columns
        required_columns = ['team1', 'team2', 'winner', 'date']
        missing_columns = [col for col in required_columns if col not in matches_df.columns]
        if missing_columns:
            issues.append(f"Missing columns: {missing_columns}")
            return matches_df, issues
        
        # Clean team names
        matches_df['team1'] = matches_df['team1'].apply(self.clean_team_name)
        matches_df['team2'] = matches_df['team2'].apply(self.clean_team_name)
        matches_df['winner'] = matches_df['winner'].apply(self.clean_team_name)
        
        # Validate winner is one of the teams
        valid_winners = (
            (matches_df['winner'] == matches_df['team1']) |
            (matches_df['winner'] == matches_df['team2'])
        )
        invalid_winners = len(matches_df) - valid_winners.sum()
        if invalid_winners > 0:
            issues.append(f"Found {invalid_winners} matches with invalid winners")
            matches_df = matches_df[valid_winners]
        
        return matches_df, issues
    
    def clean_team_name(self, team_name: str) -> str:
        """Clean and standardize team names"""
        if pd.isna(team_name):
            return team_name
        
        # Team name mappings
        mappings = {
            'SK Telecom T1': 'T1',
            'SKT': 'T1',
            'Samsung Galaxy': 'Gen.G',
            'KSV': 'Gen.G',
            'DragonX': 'DRX',
            'Griffin': 'DRX',  # Historical mapping
            'Longzhu Gaming': 'KT Rolster',  # Historical
            'DAMWON KIA': 'DWG KIA',
            'DAMWON': 'DWG KIA'
        }
        
        cleaned = team_name.strip()
        return mappings.get(cleaned, cleaned)
    
    def merge_odds_and_matches(self, odds_df: pd.DataFrame, matches_df: pd.DataFrame) -> pd.DataFrame:
        """Merge odds and match result data"""
        # Convert dates to datetime
        odds_df['date'] = pd.to_datetime(odds_df['commence_time'])
        matches_df['date'] = pd.to_datetime(matches_df['date'])
        
        # Create merge keys
        odds_df['merge_key'] = odds_df.apply(
            lambda x: f"{sorted([x['team1'], x['team2']])}{x['date'].date()}", axis=1
        )
        matches_df['merge_key'] = matches_df.apply(
            lambda x: f"{sorted([x['team1'], x['team2']])}{x['date'].date()}", axis=1
        )
        
        # Merge on the key
        merged = pd.merge(odds_df, matches_df, on='merge_key', how='inner', suffixes=('_odds', '_match'))
        
        return merged