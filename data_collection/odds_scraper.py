# data_collection/odds_scraper.py
"""
Scrape betting odds for LCK matches from multiple sources
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path

class LCKOddsScraper:
    """Scrape betting odds for LCK matches"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for scraper"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data/odds/scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def scrape_odds_api(self, api_key: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Scrape odds from The Odds API (paid service but has historical data)
        """
        base_url = "https://api.the-odds-api.com/v4/sports/lol_lck/odds/history"
        
        all_odds = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current_date <= end_date_obj:
            params = {
                'apiKey': api_key,
                'regions': 'us,uk,eu',
                'markets': 'h2h',  # Head to head
                'dateFormat': 'iso',
                'date': current_date.strftime('%Y-%m-%dT00:00:00Z')
            }
            
            try:
                response = requests.get(base_url, params=params, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()
                for match in data:
                    processed_match = self.process_odds_data(match)
                    if processed_match:
                        all_odds.append(processed_match)
                
                self.logger.info(f"Scraped {len(data)} matches for {current_date.date()}")
                time.sleep(1)  # Rate limiting
                
            except requests.RequestException as e:
                self.logger.error(f"Error scraping {current_date.date()}: {e}")
            
            current_date += timedelta(days=1)
        
        return all_odds
    
    def scrape_esports_betting_sites(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Scrape from free esports betting sites (implement specific sites)
        Note: This is a template - actual implementation depends on available sites
        """
        # Example sites to scrape (you'll need to implement each):
        # - Bet365 (if they have historical data)
        # - Pinnacle esports
        # - Betway esports
        # - Community betting tracking sites
        
        all_odds = []
        
        # Template for scraping a betting site
        sites = [
            {
                'name': 'pinnacle',
                'url': 'https://www.pinnacle.com/en/esports/league-of-legends/lck',
                'scraper': self.scrape_pinnacle
            },
            # Add more sites here
        ]
        
        for site in sites:
            try:
                site_odds = site['scraper'](start_date, end_date)
                all_odds.extend(site_odds)
                self.logger.info(f"Scraped {len(site_odds)} matches from {site['name']}")
            except Exception as e:
                self.logger.error(f"Error scraping {site['name']}: {e}")
        
        return all_odds
    
    def scrape_pinnacle(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Scrape Pinnacle esports (template - needs actual implementation)
        """
        # This is a template - actual implementation needed
        # Pinnacle has good odds but anti-scraping measures
        return []
    
    def process_odds_data(self, raw_match: Dict) -> Optional[Dict]:
        """Process raw odds data into standardized format"""
        try:
            # Extract team names and clean them
            teams = []
            bookmaker_odds = []
            
            for bookmaker in raw_match.get('bookmakers', []):
                for market in bookmaker.get('markets', []):
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            teams.append(outcome['name'])
                            bookmaker_odds.append({
                                'bookmaker': bookmaker['key'],
                                'team': outcome['name'],
                                'odds': outcome['price'],
                                'last_update': bookmaker['last_update']
                            })
            
            if len(teams) < 2:
                return None
            
            # Clean team names to match your existing data
            team1, team2 = self.clean_team_names(teams[0], teams[1])
            
            return {
                'match_id': raw_match.get('id'),
                'commence_time': raw_match.get('commence_time'),
                'team1': team1,
                'team2': team2,
                'odds_data': bookmaker_odds,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing match data: {e}")
            return None
    
    def clean_team_names(self, team1: str, team2: str) -> tuple:
        """Clean and standardize team names to match your existing data"""
        # Map betting site team names to your standardized names
        team_mapping = {
            'T1': 'T1',
            'SK Telecom T1': 'T1',
            'Gen.G': 'Gen.G',
            'DRX': 'DRX',
            'KT Rolster': 'KT Rolster',
            'Hanwha Life Esports': 'Hanwha Life Esports',
            'Kwangdong Freecs': 'Kwangdong Freecs',
            'Nongshim RedForce': 'Nongshim RedForce',
            'DWG KIA': 'DWG KIA',
            'Liiv SANDBOX': 'Liiv SANDBOX'
            # Add more mappings as needed
        }
        
        cleaned_team1 = team_mapping.get(team1, team1)
        cleaned_team2 = team_mapping.get(team2, team2)
        
        return cleaned_team1, cleaned_team2
    
    def save_odds_data(self, odds_data: List[Dict], filename: str = None):
        """Save scraped odds data"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/odds/historical_odds_{timestamp}.csv"
        
        df = pd.DataFrame(odds_data)
        df.to_csv(filename, index=False)
        self.logger.info(f"Saved {len(odds_data)} records to {filename}")

