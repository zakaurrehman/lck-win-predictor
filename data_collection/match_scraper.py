# data_collection/match_scraper.py
"""
Scrape LCK match results from official sources
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import logging
from typing import List, Dict


class LCKMatchScraper:
    """Scrape LCK match results and game data"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def scrape_leaguepedia(self, start_year: int = 2019, end_year: int = 2024) -> List[Dict]:
        """
        Scrape match data from Leaguepedia (free and comprehensive)
        """
        all_matches = []
        
        for year in range(start_year, end_year + 1):
            # Leaguepedia API endpoints
            tournaments = [
                f"LCK/{year}/Spring",
                f"LCK/{year}/Summer"
            ]
            
            for tournament in tournaments:
                try:
                    matches = self.get_leaguepedia_matches(tournament)
                    all_matches.extend(matches)
                    self.logger.info(f"Scraped {len(matches)} matches from {tournament}")
                    time.sleep(1)
                except Exception as e:
                    self.logger.error(f"Error scraping {tournament}: {e}")
        
        return all_matches
    
    def get_leaguepedia_matches(self, tournament: str) -> List[Dict]:
        """Get matches from Leaguepedia API"""
        # Using Leaguepedia's Cargo API
        base_url = "https://lol.fandom.com/api.php"
        
        params = {
            'action': 'cargoquery',
            'tables': 'MatchSchedule=MS,ScoreboardGames=SG,ScoreboardPlayers=SP',
            'join_on': 'MS.UniqueGame=SG.UniqueGame,SG.UniqueGame=SP.UniqueGame',
            'fields': 'MS.DateTime_UTC,MS.Team1,MS.Team2,MS.Winner,MS.OverviewPage,SG.GameId,SG.Gamelength,SP.Link,SP.Champion,SP.Team',
            'where': f'MS.OverviewPage="{tournament}"',
            'format': 'json',
            'limit': 'max'
        }
        
        response = requests.get(base_url, params=params, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        return self.process_leaguepedia_data(data)
    
    def process_leaguepedia_data(self, raw_data: Dict) -> List[Dict]:
        """Process Leaguepedia data into standardized format"""
        matches = []
        
        # Group by match
        match_groups = {}
        for item in raw_data.get('cargoquery', []):
            title = item['title']
            overview_page = title.get('OverviewPage', '')
            team1 = title.get('Team1', '')
            team2 = title.get('Team2', '')
            date_time = title.get('DateTime UTC', '')
            winner = title.get('Winner', '')
            
            match_key = f"{overview_page}_{team1}_{team2}_{date_time}"
            
            if match_key not in match_groups:
                match_groups[match_key] = {
                    'date': date_time,
                    'team1': team1,
                    'team2': team2,
                    'winner': winner,
                    'games': []
                }
            
            # Add game-specific data
            game_data = {
                'game_id': title.get('GameId', ''),
                'duration': title.get('Gamelength', ''),
                'player': title.get('Link', ''),
                'champion': title.get('Champion', ''),
                'team': title.get('Team', '')
            }
            
            match_groups[match_key]['games'].append(game_data)
        
        # Convert to list format
        for match_data in match_groups.values():
            matches.append(match_data)
        
        return matches
    
    def scrape_riot_api(self, api_key: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Scrape from Riot Games API (if available for historical data)
        Note: Riot API has limitations for historical data
        """
        # This is a template - Riot API access for historical LCK data is limited
        return []
    
    def save_match_data(self, matches: List[Dict], filename: str = None):
        """Save match data"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/matches/match_results_{timestamp}.csv"
        
        # Flatten match data for CSV
        flattened_matches = []
        for match in matches:
            base_match = {
                'date': match['date'],
                'team1': match['team1'],
                'team2': match['team2'],
                'winner': match['winner'],
                'team1_win': 1 if match['winner'] == match['team1'] else 0
            }
            
            # Add champion data
            team1_champions = []
            team2_champions = []
            
            for game in match['games']:
                if game['team'] == match['team1']:
                    team1_champions.append(game['champion'])
                elif game['team'] == match['team2']:
                    team2_champions.append(game['champion'])
            
            # Add champions to match (assuming standard 5v5)
            for i in range(5):
                if i < len(team1_champions):
                    base_match[f'team1_champ{i+1}'] = team1_champions[i]
                if i < len(team2_champions):
                    base_match[f'team2_champ{i+1}'] = team2_champions[i]
            
            flattened_matches.append(base_match)
        
        df = pd.DataFrame(flattened_matches)
        df.to_csv(filename, index=False)
        self.logger.info(f"Saved {len(flattened_matches)} matches to {filename}")
