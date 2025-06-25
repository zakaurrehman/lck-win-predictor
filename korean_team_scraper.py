import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

class KoreanTeamsScraper:
    def __init__(self):
        self.base_url = "https://lol.fandom.com"
        self.teams_data = {}
        
    def scrape_korean_teams(self):
        """Scrape all Korean teams and their current rosters"""
        url = "https://lol.fandom.com/wiki/Korean_Teams"
        
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all team sections
            # Look for LCK teams first
            lck_section = soup.find('span', {'id': 'LCK'})
            if lck_section:
                # Navigate to the table containing LCK teams
                current = lck_section.parent
                while current and current.name != 'table':
                    current = current.find_next_sibling()
                
                if current:
                    self._process_teams_table(current, 'LCK')
            
            # Also check for Challengers League teams if needed
            cl_section = soup.find('span', {'id': 'LCK_Challengers_League'})
            if cl_section:
                current = cl_section.parent
                while current and current.name != 'table':
                    current = current.find_next_sibling()
                
                if current:
                    self._process_teams_table(current, 'LCK CL')
            
            return self.teams_data
            
        except Exception as e:
            print(f"Error scraping teams: {e}")
            return None
    
    def _process_teams_table(self, table, league):
        """Process a table of teams"""
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) >= 2:
                # Team name is usually in the second cell
                team_cell = cells[1]
                team_link = team_cell.find('a')
                
                if team_link:
                    team_name = team_link.get('title', '').strip()
                    team_url = self.base_url + team_link.get('href', '')
                    
                    # Get roster for this team
                    roster = self._get_team_roster(team_url)
                    
                    if team_name and roster:
                        self.teams_data[team_name] = {
                            'league': league,
                            'roster': roster,
                            'url': team_url
                        }
                        print(f"Scraped {team_name}: {len(roster)} players")
    
    def _get_team_roster(self, team_url):
        """Get current roster for a specific team"""
        try:
            response = requests.get(team_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            roster = {}
            
            # Look for roster card or player tables
            # Try to find "Current Roster" section
            roster_section = soup.find('span', {'id': re.compile('Current.*Roster|Active.*Roster', re.I)})
            
            if not roster_section:
                # Alternative: look for roster tables
                tables = soup.find_all('table', {'class': re.compile('roster|wikitable')})
                for table in tables:
                    # Check if this table contains player info
                    headers = table.find_all('th')
                    if any('player' in th.text.lower() or 'position' in th.text.lower() for th in headers):
                        roster = self._parse_roster_table(table)
                        if roster:
                            break
            else:
                # Find the table after the roster section
                current = roster_section.parent
                while current and current.name != 'table':
                    current = current.find_next_sibling()
                
                if current:
                    roster = self._parse_roster_table(current)
            
            return roster
            
        except Exception as e:
            print(f"Error getting roster from {team_url}: {e}")
            return {}
    
    def _parse_roster_table(self, table):
        """Parse a roster table to extract players and positions"""
        roster = {}
        rows = table.find_all('tr')
        
        # Find column indices
        headers = rows[0].find_all(['th', 'td'])
        player_idx = -1
        position_idx = -1
        
        for i, header in enumerate(headers):
            header_text = header.text.strip().lower()
            if 'player' in header_text or 'id' in header_text:
                player_idx = i
            elif 'position' in header_text or 'role' in header_text:
                position_idx = i
        
        if player_idx == -1 or position_idx == -1:
            return roster
        
        # Parse player rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) > max(player_idx, position_idx):
                player_cell = cells[player_idx]
                position_cell = cells[position_idx]
                
                # Extract player name
                player_link = player_cell.find('a')
                if player_link:
                    player_name = player_link.text.strip()
                else:
                    player_name = player_cell.text.strip()
                
                # Extract position
                position = position_cell.text.strip().lower()
                
                # Normalize positions
                position_map = {
                    'top': 'top',
                    'toplane': 'top',
                    'top lane': 'top',
                    'jungle': 'jng',
                    'jungler': 'jng',
                    'jng': 'jng',
                    'mid': 'mid',
                    'midlane': 'mid',
                    'mid lane': 'mid',
                    'bottom': 'bot',
                    'bot': 'bot',
                    'adc': 'bot',
                    'ad carry': 'bot',
                    'support': 'sup',
                    'sup': 'sup'
                }
                
                normalized_position = position_map.get(position, position)
                
                if player_name and normalized_position in ['top', 'jng', 'mid', 'bot', 'sup']:
                    roster[normalized_position] = player_name
        
        return roster
    
    def save_to_json(self, filename='data/korean_teams_rosters.json'):
        """Save scraped data to JSON file"""
        output = {
            'last_updated': datetime.now().isoformat(),
            'teams': self.teams_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\nSaved {len(self.teams_data)} teams to {filename}")
        
        # Print summary
        print("\nTeams scraped:")
        for team, data in self.teams_data.items():
            roster = data['roster']
            print(f"\n{team} ({data['league']}):")
            for pos in ['top', 'jng', 'mid', 'bot', 'sup']:
                if pos in roster:
                    print(f"  {pos.upper()}: {roster[pos]}")

    def get_manual_rosters(self):
        """Fallback: Define rosters manually for major LCK teams"""
        # This is a fallback in case scraping fails
        manual_rosters = {
            "T1": {
                "league": "LCK",
                "roster": {
                    "top": "Zeus",
                    "jng": "Oner",
                    "mid": "Faker",
                    "bot": "Gumayusi",
                    "sup": "Keria"
                }
            },
            "Gen.G": {
                "league": "LCK",
                "roster": {
                    "top": "Kiin",
                    "jng": "Canyon",
                    "mid": "Chovy",
                    "bot": "Peyz",
                    "sup": "Lehends"
                }
            },
            "Hanwha Life Esports": {
                "league": "LCK",
                "roster": {
                    "top": "Doran",
                    "jng": "Peanut",
                    "mid": "Zeka",
                    "bot": "Viper",
                    "sup": "Delight"
                }
            },
            "Dplus KIA": {
                "league": "LCK",
                "roster": {
                    "top": "Canna",
                    "jng": "Lucid",
                    "mid": "ShowMaker",
                    "bot": "Aiming",
                    "sup": "Kellin"
                }
            },
            "KT Rolster": {
                "league": "LCK",
                "roster": {
                    "top": "PerfecT",
                    "jng": "Pyosik",
                    "mid": "Bdd",
                    "bot": "Deft",
                    "sup": "BeryL"
                }
            },
            "DRX": {
                "league": "LCK",
                "roster": {
                    "top": "Rascal",
                    "jng": "Juhan",
                    "mid": "SeTab",
                    "bot": "Teddy",
                    "sup": "Pleata"
                }
            },
            "BRION": {
                "league": "LCK",
                "roster": {
                    "top": "Morgan",
                    "jng": "UmTi",
                    "mid": "Clozer",
                    "bot": "EnvyY",
                    "sup": "Effort"
                }
            },
            "Nongshim RedForce": {
                "league": "LCK",
                "roster": {
                    "top": "DuDu",
                    "jng": "Sylvie",
                    "mid": "Jiwoo",
                    "bot": "Vital",
                    "sup": "Peter"
                }
            },
            "FearX": {
                "league": "LCK",
                "roster": {
                    "top": "Clear",
                    "jng": "Willer",
                    "mid": "YoungJae",
                    "bot": "Hena",
                    "sup": "Andil"
                }
            },
            "OK BRION": {
                "league": "LCK",
                "roster": {
                    "top": "Kingen",
                    "jng": "Gideon",
                    "mid": "Ucal",
                    "bot": "Envyy",
                    "sup": "Execute"
                }
            }
        }
        
        return manual_rosters

if __name__ == "__main__":
    scraper = KoreanTeamsScraper()
    
    print("Attempting to scrape Korean teams from LoL Fandom...")
    teams = scraper.scrape_korean_teams()
    
    if not teams or len(teams) < 5:
        print("\nScraping incomplete, using manual rosters...")
        scraper.teams_data = scraper.get_manual_rosters()
    
    # Save the data
    import os
    os.makedirs('data', exist_ok=True)
    scraper.save_to_json()
    
    print("\nDone! Team rosters saved to data/korean_teams_rosters.json")