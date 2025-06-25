# real_time_data_updater.py
import schedule
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
from sqlalchemy import create_engine

class RealTimeDataUpdater:
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/data_updates.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Database connection
        self.db_engine = create_engine('sqlite:///data/lck_matches.db')
        
    def check_for_new_matches(self):
        """Check for new LCK matches every hour"""
        self.logger.info("Checking for new matches...")
        
        try:
            # Get latest match date from database
            latest_date = self.get_latest_match_date()
            
            # Query Leaguepedia for new matches
            new_matches = self.fetch_recent_matches(latest_date)
            
            if new_matches:
                self.logger.info(f"Found {len(new_matches)} new matches")
                self.process_new_matches(new_matches)
                self.trigger_model_update()
            else:
                self.logger.info("No new matches found")
                
        except Exception as e:
            self.logger.error(f"Error checking for matches: {e}")
    
    def get_latest_match_date(self):
        """Get the date of the most recent match in database"""
        query = "SELECT MAX(date) as latest_date FROM matches"
        result = pd.read_sql(query, self.db_engine)
        
        if result['latest_date'].iloc[0]:
            return pd.to_datetime(result['latest_date'].iloc[0])
        else:
            return datetime.now() - timedelta(days=30)
    
    def fetch_recent_matches(self, since_date):
        """Fetch matches from Leaguepedia since given date"""
        url = "https://lol.fandom.com/api.php"
        
        params = {
            'action': 'cargoquery',
            'format': 'json',
            'tables': 'ScoreboardGames=SG',
            'fields': 'SG.GameId, SG.DateTime_UTC, SG.Team1, SG.Team2, '
                     'SG.Winner, SG.Team1Picks, SG.Team2Picks, '
                     'SG.Team1Bans, SG.Team2Bans, SG.Patch',
            'where': f'SG.Tournament LIKE "%LCK%" AND SG.DateTime_UTC > "{since_date}"',
            'order_by': 'SG.DateTime_UTC DESC',
            'limit': '100'
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            matches = []
            
            for item in data.get('cargoquery', []):
                match_data = item.get('title', {})
                if self.validate_match_data(match_data):
                    matches.append(self.parse_match_data(match_data))
            
            return matches
        
        return []
    
    def validate_match_data(self, match_data):
        """Validate that match has complete data"""
        required_fields = ['Team1Picks', 'Team2Picks', 'Winner']
        return all(match_data.get(field) for field in required_fields)
    
    def parse_match_data(self, match_data):
        """Parse match data into standard format"""
        # Similar to Phase 1 parsing logic
        return {
            'gameid': match_data.get('GameId'),
            'date': match_data.get('DateTime UTC'),
            'blue_team': match_data.get('Team1'),
            'red_team': match_data.get('Team2'),
            'blue_win': 1 if match_data.get('Winner') == '1' else 0,
            # ... parse champions, bans, etc.
        }
    
    def process_new_matches(self, matches):
        """Process and store new matches"""
        df = pd.DataFrame(matches)
        
        # Store in database
        df.to_sql('matches', self.db_engine, if_exists='append', index=False)
        
        # Update feature calculations
        self.update_features(df)
        
        self.logger.info(f"Processed {len(df)} new matches")
    
    def update_features(self, new_matches_df):
        """Update feature calculations with new data"""
        # Update player stats
        self.update_player_stats(new_matches_df)
        
        # Update champion synergies
        self.update_champion_synergies(new_matches_df)
        
        # Update team matchup history
        self.update_team_matchups(new_matches_df)
    
    def trigger_model_update(self):
        """Trigger model retraining if needed"""
        # Check if enough new matches
        query = "SELECT COUNT(*) as new_matches FROM matches WHERE processed = 0"
        result = pd.read_sql(query, self.db_engine)
        
        if result['new_matches'].iloc[0] >= 50:
            self.logger.info("Triggering model retraining...")
            os.system("python retrain_model.py")
    
    def run_scheduler(self):
        """Run the update scheduler"""
        # Schedule updates
        schedule.every(1).hours.do(self.check_for_new_matches)
        schedule.every(24).hours.do(self.full_data_refresh)
        schedule.every(7).days.do(self.cleanup_old_logs)
        
        self.logger.info("Real-time updater started")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def full_data_refresh(self):
        """Perform full data refresh weekly"""
        self.logger.info("Performing full data refresh...")
        # Implementation for complete data validation and refresh
    
    def cleanup_old_logs(self):
        """Clean up logs older than 30 days"""