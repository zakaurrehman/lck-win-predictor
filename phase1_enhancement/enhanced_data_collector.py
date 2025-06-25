# enhanced_data_collector.py
import requests
import pandas as pd
import os
import time
from datetime import datetime, timedelta
import json

class EnhancedDataCollector:
    def __init__(self):
        self.all_matches = []
        self.player_stats = {}
        self.patch_data = {}
        
    def collect_all_sources(self):
        """Collect from multiple sources to get 5000+ matches"""
        
        # 1. Leaguepedia - Main source
        print("1. Collecting from Leaguepedia...")
        self.collect_leaguepedia_extended()
        
        # 2. Try Riot API (if you have key)
        print("\n2. Attempting Riot API...")
        self.collect_riot_api()
        
        # 3. Historical Oracle's Elixir
        print("\n3. Downloading historical data...")
        self.download_historical_data()
        
        # 4. Combine and save
        self.combine_and_save()
        
    def collect_leaguepedia_extended(self):
        """Get ALL available LCK matches from Leaguepedia"""
        base_url = "https://lol.fandom.com/api.php"
        
        # Extended tournament list - get everything
        tournaments = [
            # 2024
            "%LCK 2024 Spring%", "%LCK 2024 Summer%", "%LCK 2024 Spring Playoffs%",
            # 2023  
            "%LCK 2023 Spring%", "%LCK 2023 Summer%", "%LCK 2023 Spring Playoffs%",
            "%LCK 2023 Summer Playoffs%", "%LCK 2023 Regional Finals%",
            # 2022
            "%LCK 2022 Spring%", "%LCK 2022 Summer%", "%LCK 2022 Spring Playoffs%",
            # 2021
            "%LCK 2021 Spring%", "%LCK 2021 Summer%",
            # 2020
            "%LCK 2020 Spring%", "%LCK 2020 Summer%",
            # Include Challengers League
            "%LCK CL 2024%", "%LCK CL 2023%", "%LCK CL 2022%",
            # Special events
            "%Kespa Cup%", "%LCK Academy%"
        ]
        
        for tournament in tournaments:
            print(f"  Fetching {tournament}...")
            offset = 0
            
            while True:
                params = {
                    'action': 'cargoquery',
                    'format': 'json',
                    'tables': 'ScoreboardGames=SG,ScoreboardPlayers=SP',
                    'fields': '''SG.GameId, SG.DateTime_UTC, SG.Team1, SG.Team2,
                               SG.Winner, SG.Team1Picks, SG.Team2Picks,
                               SG.Team1Bans, SG.Team2Bans, SG.Patch,
                               SG.Team1Players, SG.Team2Players,
                               SG.Team1Dragons, SG.Team2Dragons,
                               SG.Team1Barons, SG.Team2Barons,
                               SG.Team1Towers, SG.Team2Towers,
                               SG.Team1Gold, SG.Team2Gold,
                               SG.Team1Kills, SG.Team2Kills,
                               SG.Gamelength_Number''',
                    'where': f'SG.Tournament LIKE "{tournament}"',
                    'join_on': 'SG.GameId=SP.GameId',
                    'order_by': 'SG.DateTime_UTC DESC',
                    'limit': '500',
                    'offset': str(offset)
                }
                
                try:
                    response = requests.get(base_url, params=params, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('cargoquery', [])
                        
                        if not results:
                            break
                            
                        self.process_leaguepedia_data(results)
                        print(f"    Got {len(results)} matches (total: {len(self.all_matches)})")
                        
                        if len(results) < 500:
                            break
                            
                        offset += 500
                        time.sleep(0.5)  # Be nice to API
                except Exception as e:
                    print(f"    Error: {e}")
                    break
    
    def process_leaguepedia_data(self, results):
        """Process and extract all useful data from Leaguepedia"""
        for item in results:
            match = item.get('title', {})
            
            # Skip incomplete data
            if not match.get('Team1Picks') or not match.get('Team2Picks'):
                continue
                
            # Parse all data
            team1_picks = [p.strip() for p in match.get('Team1Picks', '').split(',')]
            team2_picks = [p.strip() for p in match.get('Team2Picks', '').split(',')]
            
            if len(team1_picks) != 5 or len(team2_picks) != 5:
                continue
                
            # Parse additional game stats
            game_data = {
                'gameid': match.get('GameId', ''),
                'date': match.get('DateTime UTC', ''),
                'patch': match.get('Patch', ''),
                'gamelength': float(match.get('Gamelength Number', 1800)) if match.get('Gamelength Number') else 1800,
                'blue_team': match.get('Team1', ''),
                'red_team': match.get('Team2', ''),
                'blue_win': 1 if match.get('Winner') == '1' else 0,
                
                # Champions
                'blue_champ1': team1_picks[0],
                'blue_champ2': team1_picks[1],
                'blue_champ3': team1_picks[2],
                'blue_champ4': team1_picks[3],
                'blue_champ5': team1_picks[4],
                'red_champ1': team2_picks[0],
                'red_champ2': team2_picks[1],
                'red_champ3': team2_picks[2],
                'red_champ4': team2_picks[3],
                'red_champ5': team2_picks[4],
                
                # Game stats
                'blue_kills': int(match.get('Team1Kills', 0)) if match.get('Team1Kills') else 0,
                'red_kills': int(match.get('Team2Kills', 0)) if match.get('Team2Kills') else 0,
                'blue_gold': int(match.get('Team1Gold', 0)) if match.get('Team1Gold') else 0,
                'red_gold': int(match.get('Team2Gold', 0)) if match.get('Team2Gold') else 0,
                'blue_dragons': int(match.get('Team1Dragons', 0)) if match.get('Team1Dragons') else 0,
                'red_dragons': int(match.get('Team2Dragons', 0)) if match.get('Team2Dragons') else 0,
                'blue_barons': int(match.get('Team1Barons', 0)) if match.get('Team1Barons') else 0,
                'red_barons': int(match.get('Team2Barons', 0)) if match.get('Team2Barons') else 0,
                'blue_towers': int(match.get('Team1Towers', 0)) if match.get('Team1Towers') else 0,
                'red_towers': int(match.get('Team2Towers', 0)) if match.get('Team2Towers') else 0,
            }
            
            # Parse bans
            team1_bans = [b.strip() for b in match.get('Team1Bans', '').split(',')] if match.get('Team1Bans') else []
            team2_bans = [b.strip() for b in match.get('Team2Bans', '').split(',')] if match.get('Team2Bans') else []
            
            for i in range(5):
                game_data[f'blue_ban{i+1}'] = team1_bans[i] if i < len(team1_bans) else ''
                game_data[f'red_ban{i+1}'] = team2_bans[i] if i < len(team2_bans) else ''
            
            # Parse players
            team1_players = match.get('Team1Players', '').split(',') if match.get('Team1Players') else []
            team2_players = match.get('Team2Players', '').split(',') if match.get('Team2Players') else []
            
            positions = ['top', 'jng', 'mid', 'bot', 'sup']
            for i, pos in enumerate(positions):
                game_data[f'blue_{pos}'] = team1_players[i].strip() if i < len(team1_players) else ''
                game_data[f'red_{pos}'] = team2_players[i].strip() if i < len(team2_players) else ''
            
            self.all_matches.append(game_data)
    
    def download_historical_data(self):
        """Download historical datasets"""
        historical_urls = [
            # Oracle's Elixir historical data
            ("2023", "https://drive.google.com/uc?export=download&id=1YourGoogleDriveID2023"),
            ("2022", "https://drive.google.com/uc?export=download&id=1YourGoogleDriveID2022"),
            # Add more sources as you find them
        ]
        
        for year, url in historical_urls:
            try:
                print(f"  Downloading {year} historical data...")
                # Implementation depends on actual URLs
            except Exception as e:
                print(f"  Skipping {year}: {e}")
    
    def collect_riot_api(self):
        """Collect from Riot API if available"""
        # This requires Riot API key
        # Implementation placeholder
        print("  Riot API requires authentication - skipping for now")
    
    def combine_and_save(self):
        """Combine all data and save"""
        if self.all_matches:
            df = pd.DataFrame(self.all_matches)
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['gameid'], keep='first')
            
            # Sort by date
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date', ascending=False)
            
            # Save full dataset
            os.makedirs("data/enhanced", exist_ok=True)
            df.to_csv("data/enhanced/lck_full_dataset.csv", index=False)
            
            print(f"\n✓ Total matches collected: {len(df)}")
            print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"✓ Unique patches: {df['patch'].nunique()}")
            print(f"✓ Saved to: data/enhanced/lck_full_dataset.csv")
            
            return df
        return None

# Run the enhanced collector
if __name__ == "__main__":
    collector = EnhancedDataCollector()
    df = collector.collect_all_sources()