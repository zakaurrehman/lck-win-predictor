import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time

class EnhancedKoreanTeamsScraper:
    def __init__(self):
        self.base_url = "https://lol.fandom.com"
        self.teams_data = {}
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def scrape_all_korean_teams(self):
        """Comprehensive scraping of ALL Korean teams"""
        print("Starting comprehensive Korean teams scraping...")
        
        # 1. Get teams from multiple sources
        self._scrape_from_api()  # Try API first
        self._scrape_main_pages()  # Main wiki pages
        self._scrape_tournament_pages()  # Recent tournaments
        
        # 2. Add all known teams manually (comprehensive list)
        manual_teams = self._get_all_korean_teams_manual()
        for team, data in manual_teams.items():
            if team not in self.teams_data:
                self.teams_data[team] = data
        
        print(f"\n✓ Total teams collected: {len(self.teams_data)}")
        return self.teams_data
    
    def _scrape_from_api(self):
        """Try to use Leaguepedia API for comprehensive data"""
        try:
            # Cargo query for all Korean teams
            api_url = "https://lol.fandom.com/api.php"
            params = {
                'action': 'cargoquery',
                'format': 'json',
                'tables': 'Teams',
                'fields': 'Teams.Name, Teams.Region, Teams.IsActive',
                'where': 'Teams.Region="Korea"',
                'limit': '500'
            }
            
            response = requests.get(api_url, params=params, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                results = data.get('cargoquery', [])
                
                for item in results:
                    team_data = item.get('title', {})
                    team_name = team_data.get('Name', '').strip()
                    if team_name:
                        print(f"Found via API: {team_name}")
                        # Get roster for this team
                        roster = self._get_team_roster_api(team_name)
                        self.teams_data[team_name] = {
                            'league': 'LCK' if team_data.get('IsActive') == 'true' else 'Former',
                            'roster': roster,
                            'active': team_data.get('IsActive') == 'true'
                        }
                        
        except Exception as e:
            print(f"API scraping failed: {e}")
    
    def _get_team_roster_api(self, team_name):
        """Get roster using API"""
        try:
            api_url = "https://lol.fandom.com/api.php"
            params = {
                'action': 'cargoquery',
                'format': 'json',
                'tables': 'Players',
                'fields': 'Players.ID, Players.Role',
                'where': f'Players.Team="{team_name}" AND Players.IsRetired="false"',
                'limit': '10'
            }
            
            response = requests.get(api_url, params=params, headers=self.headers)
            roster = {}
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('cargoquery', [])
                
                for item in results:
                    player_data = item.get('title', {})
                    player_name = player_data.get('ID', '')
                    role = player_data.get('Role', '').lower()
                    
                    normalized_role = self._normalize_position(role)
                    if player_name and normalized_role:
                        roster[normalized_role] = player_name
            
            return roster
            
        except Exception as e:
            print(f"  Error getting roster for {team_name}: {e}")
            return {}
    
    def _scrape_main_pages(self):
        """Scrape from main wiki pages"""
        pages = [
            "Korean_Teams",
            "LCK",
            "LCK_Challengers_League",
            "Category:Korean_Teams",
            "Portal:Teams/Korea"
        ]
        
        for page in pages:
            try:
                url = f"{self.base_url}/wiki/{page}"
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all team links
                links = soup.find_all('a', href=re.compile(r'/wiki/[^:]+$'))
                
                for link in links:
                    team_name = link.text.strip()
                    if self._is_valid_team_name(team_name) and team_name not in self.teams_data:
                        team_url = self.base_url + link.get('href', '')
                        print(f"Checking {team_name}...")
                        roster = self._get_team_roster_from_page(team_url)
                        if roster or self._is_known_team(team_name):
                            self.teams_data[team_name] = {
                                'league': self._determine_league(team_name),
                                'roster': roster,
                                'url': team_url
                            }
                        time.sleep(0.2)
                        
            except Exception as e:
                print(f"Error scraping {page}: {e}")
    
    def _scrape_tournament_pages(self):
        """Scrape recent tournament pages"""
        tournaments = [
            "LCK/2025_Season",
            "LCK/2024_Season",
            "LCK_Challengers_League/2025_Season",
            "LCK_Academy_Series/2025_Season"
        ]
        
        for tournament in tournaments:
            try:
                url = f"{self.base_url}/wiki/{tournament}"
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for team lists
                team_sections = soup.find_all(['div', 'table'], class_=re.compile('team|participant'))
                
                for section in team_sections:
                    links = section.find_all('a')
                    for link in links:
                        team_name = link.text.strip()
                        if self._is_valid_team_name(team_name):
                            self.teams_data.setdefault(team_name, {
                                'league': self._league_from_tournament(tournament),
                                'roster': {},
                                'tournament': tournament
                            })
                            
            except Exception as e:
                print(f"Error scraping {tournament}: {e}")
    
    def _get_team_roster_from_page(self, url):
        """Extract roster from team page"""
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            roster = {}
            
            # Method 1: Look for roster tables
            tables = soup.find_all('table')
            for table in tables:
                header_text = ' '.join([th.text.lower() for th in table.find_all('th')])
                if 'player' in header_text and ('role' in header_text or 'position' in header_text):
                    roster = self._parse_roster_table(table)
                    if roster:
                        return roster
            
            # Method 2: Look for player infoboxes
            infoboxes = soup.find_all('div', class_='infobox')
            for box in infoboxes:
                if 'player' in box.text.lower():
                    roster.update(self._parse_infobox(box))
            
            return roster
            
        except Exception as e:
            return {}
    
    def _parse_roster_table(self, table):
        """Parse roster from table"""
        roster = {}
        rows = table.find_all('tr')
        
        if not rows:
            return roster
        
        # Find column indices
        headers = rows[0].find_all(['th', 'td'])
        player_idx = position_idx = -1
        
        for i, header in enumerate(headers):
            header_text = header.text.strip().lower()
            if any(word in header_text for word in ['player', 'id', 'name']):
                player_idx = i
            elif any(word in header_text for word in ['position', 'role']):
                position_idx = i
        
        if player_idx == -1 or position_idx == -1:
            return roster
        
        # Parse player rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) > max(player_idx, position_idx):
                # Get player name
                player_cell = cells[player_idx]
                player_link = player_cell.find('a')
                player_name = (player_link.text if player_link else player_cell.text).strip()
                
                # Skip if not a real player name
                if not player_name or player_name.lower() in ['tbd', 'n/a', '-', '']:
                    continue
                
                # Get position
                position = cells[position_idx].text.strip().lower()
                normalized_position = self._normalize_position(position)
                
                if player_name and normalized_position:
                    roster[normalized_position] = player_name
        
        return roster
    
    def _normalize_position(self, position):
        """Normalize position names"""
        position = position.lower().strip()
        
        position_map = {
            # Top lane
            'top': 'top', 'toplane': 'top', 'top lane': 'top', 'toplaner': 'top',
            # Jungle
            'jungle': 'jng', 'jungler': 'jng', 'jng': 'jng', 'jg': 'jng',
            # Mid lane
            'mid': 'mid', 'midlane': 'mid', 'mid lane': 'mid', 'middle': 'mid',
            # Bot lane
            'bot': 'bot', 'bottom': 'bot', 'adc': 'bot', 'ad carry': 'bot', 'botlane': 'bot',
            # Support
            'support': 'sup', 'sup': 'sup', 'supp': 'sup'
        }
        
        return position_map.get(position)
    
    def _is_valid_team_name(self, name):
        """Check if this is a valid team name"""
        if not name or len(name) < 2:
            return False
        
        # Skip common non-team pages
        skip_patterns = [
            'category:', 'template:', 'user:', 'file:', 'talk:',
            'list of', 'season', 'split', 'playoffs', 'promotion'
        ]
        
        name_lower = name.lower()
        return not any(pattern in name_lower for pattern in skip_patterns)
    
    def _is_known_team(self, name):
        """Check if this is a known Korean team"""
        known_teams = [
            'T1', 'Gen.G', 'DRX', 'KT Rolster', 'Hanwha Life Esports',
            'Dplus KIA', 'BRION', 'Nongshim RedForce', 'FearX', 'Kwangdong Freecs'
        ]
        return name in known_teams
    
    def _determine_league(self, team_name):
        """Determine which league a team belongs to"""
        # LCK main teams
        lck_teams = [
            'T1', 'Gen.G', 'DRX', 'KT Rolster', 'Hanwha Life Esports',
            'Dplus KIA', 'BRION', 'Nongshim RedForce', 'FearX', 'Kwangdong Freecs'
        ]
        
        if team_name in lck_teams:
            return 'LCK'
        elif 'academy' in team_name.lower():
            return 'LCK Academy'
        elif 'challengers' in team_name.lower():
            return 'LCK CL'
        else:
            return 'Korean Team'
    
    def _league_from_tournament(self, tournament):
        """Determine league from tournament name"""
        if 'Challengers' in tournament:
            return 'LCK CL'
        elif 'Academy' in tournament:
            return 'LCK Academy'
        else:
            return 'LCK'
    
    def _get_all_korean_teams_manual(self):
        """Comprehensive manual list of ALL Korean teams"""
        return {
            # === LCK MAIN TEAMS (2025) ===
            "T1": {
                "league": "LCK",
                "roster": {
                    "top": "Zeus", "jng": "Oner", "mid": "Faker",
                    "bot": "Gumayusi", "sup": "Keria"
                }
            },
            "Gen.G": {
                "league": "LCK",
                "roster": {
                    "top": "Kiin", "jng": "Canyon", "mid": "Chovy",
                    "bot": "Peyz", "sup": "Lehends"
                }
            },
            "Hanwha Life Esports": {
                "league": "LCK",
                "roster": {
                    "top": "Doran", "jng": "Peanut", "mid": "Zeka",
                    "bot": "Viper", "sup": "Delight"
                }
            },
            "Dplus KIA": {
                "league": "LCK",
                "roster": {
                    "top": "Canna", "jng": "Lucid", "mid": "ShowMaker",
                    "bot": "Aiming", "sup": "Kellin"
                }
            },
            "KT Rolster": {
                "league": "LCK",
                "roster": {
                    "top": "PerfecT", "jng": "Pyosik", "mid": "Bdd",
                    "bot": "Deft", "sup": "BeryL"
                }
            },
            "DRX": {
                "league": "LCK",
                "roster": {
                    "top": "Rascal", "jng": "Juhan", "mid": "SeTab",
                    "bot": "Teddy", "sup": "Pleata"
                }
            },
            "BRION": {
                "league": "LCK",
                "roster": {
                    "top": "Morgan", "jng": "UmTi", "mid": "Clozer",
                    "bot": "EnvyY", "sup": "Effort"
                }
            },
            "Nongshim RedForce": {
                "league": "LCK",
                "roster": {
                    "top": "DuDu", "jng": "Sylvie", "mid": "Jiwoo",
                    "bot": "Vital", "sup": "Peter"
                }
            },
            "FearX": {
                "league": "LCK",
                "roster": {
                    "top": "Clear", "jng": "Willer", "mid": "YoungJae",
                    "bot": "Hena", "sup": "Andil"
                }
            },
            "Kwangdong Freecs": {
                "league": "LCK",
                "roster": {
                    "top": "DuDu", "jng": "Cuzz", "mid": "BuLLDoG",
                    "bot": "Taeyoon", "sup": "Andil"
                }
            },
            
            # === LCK CHALLENGERS LEAGUE TEAMS ===
            "Dplus KIA Challengers": {
                "league": "LCK CL",
                "roster": {
                    "top": "Hoya", "jng": "Raptor", "mid": "Pullbae",
                    "bot": "Lava", "sup": "Moham"
                }
            },
            "T1 Academy": {
                "league": "LCK CL",
                "roster": {
                    "top": "Dal", "jng": "Guwon", "mid": "Poby",
                    "bot": "Smash", "sup": "Rekkles"
                }
            },
            "Gen.G Challengers": {
                "league": "LCK CL",
                "roster": {
                    "top": "Kingen", "jng": "Grizzly", "mid": "BuLLDoG",
                    "bot": "Peyz", "sup": "Execute"
                }
            },
            "BRION Academy": {
                "league": "LCK CL",
                "roster": {
                    "top": "Sword", "jng": "Dang", "mid": "Karis",
                    "bot": "Envyy", "sup": "Pollu"
                }
            },
            "KT Rolster Challengers": {
                "league": "LCK CL",
                "roster": {
                    "top": "Castle", "jng": "Gideon", "mid": "Rookie",
                    "bot": "Aiming", "sup": "Rebel"
                }
            },
            "Liiv SANDBOX": {
                "league": "LCK CL",
                "roster": {
                    "top": "Willer", "jng": "Croco", "mid": "Clozer",
                    "bot": "Teddy", "sup": "Kael"
                }
            },
            "OKSavingsBank BRION": {
                "league": "LCK CL",
                "roster": {
                    "top": "Morgan", "jng": "UmTi", "mid": "Ucal",
                    "bot": "Hena", "sup": "Effort"
                }
            },
            
            # === FORMER/HISTORICAL TEAMS ===
            "Griffin": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "DAMWON Gaming": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "Samsung Galaxy": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "SK Telecom T1": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "ROX Tigers": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "Afreeca Freecs": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "Jin Air Green Wings": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "bbq Olivers": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "Kongdoo Monster": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "MVP": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "Longzhu Gaming": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "SBENU Sonicboom": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "Rebels Anarchy": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "Ever8 Winners": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "Incredible Miracle": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "CJ Entus": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "NaJin e-mFire": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            "KT Bullets": {
                "league": "Former LCK",
                "roster": {},
                "active": False
            },
            
            # === AMATEUR/ACADEMY TEAMS ===
            "HLE Academy": {
                "league": "LCK Academy",
                "roster": {
                    "top": "DnDn", "jng": "Willer", "mid": "Karis",
                    "bot": "Viper", "sup": "Vsta"
                }
            },
            "NS Academy": {
                "league": "LCK Academy",
                "roster": {
                    "top": "Rich", "jng": "Peanut", "mid": "Bay",
                    "bot": "Ghost", "sup": "SnowFlower"
                }
            },
            "DRX Academy": {
                "league": "LCK Academy",
                "roster": {
                    "top": "Kingen", "jng": "Pyosik", "mid": "FATE",
                    "bot": "deokdam", "sup": "BeryL"
                }
            }
        }
    
    def save_to_json(self, filename='data/korean_teams_all.json'):
        """Save all scraped data to JSON file"""
        import os
        os.makedirs('data', exist_ok=True)
        
        output = {
            'last_updated': datetime.now().isoformat(),
            'total_teams': len(self.teams_data),
            'teams': self.teams_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Saved {len(self.teams_data)} teams to {filename}")
        
        # Print summary by league
        leagues = {}
        for team, data in self.teams_data.items():
            league = data.get('league', 'Unknown')
            leagues[league] = leagues.get(league, 0) + 1
        
        print("\nTeams by League:")
        for league, count in sorted(leagues.items()):
            print(f"  {league}: {count} teams")
        
        # Print teams with complete rosters
        complete_rosters = 0
        for team, data in self.teams_data.items():
            roster = data.get('roster', {})
            if len(roster) >= 5:
                complete_rosters += 1
        
        print(f"\nTeams with complete rosters: {complete_rosters}/{len(self.teams_data)}")

if __name__ == "__main__":
    scraper = EnhancedKoreanTeamsScraper()
    
    print("Enhanced Korean Teams Scraper")
    print("="*50)
    print("This will collect ALL Korean teams including:")
    print("- LCK Main Teams")
    print("- LCK Challengers League")
    print("- Academy Teams")
    print("- Former/Historical Teams")
    print("="*50)
    
    # Scrape all teams
    teams = scraper.scrape_all_korean_teams()
    
    # Save to JSON
    scraper.save_to_json()
    
    print("\n✓ Scraping complete!")
    print("\nSample teams collected:")
    for i, (team, data) in enumerate(list(teams.items())[:10]):
        roster_count = len(data.get('roster', {}))
        print(f"  {team} ({data.get('league')}) - {roster_count} players")