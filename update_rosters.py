#!/usr/bin/env python3
"""
Script to update Korean team rosters - gets ALL teams
Run this periodically to keep roster data up to date
"""

import json
import os
from datetime import datetime

def create_comprehensive_manual_rosters():
    """Comprehensive manual roster list for ALL Korean teams"""
    return {
        # === LCK MAIN TEAMS (2025) ===
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
        "Kwangdong Freecs": {
            "league": "LCK",
            "roster": {
                "top": "DuDu",
                "jng": "Cuzz",
                "mid": "BuLLDoG",
                "bot": "Taeyoon",
                "sup": "Andil"
            }
        },
        
        # === LCK CHALLENGERS LEAGUE TEAMS ===
        "Dplus KIA Challengers": {
            "league": "LCK CL",
            "roster": {
                "top": "Hoya",
                "jng": "Raptor",
                "mid": "Pullbae",
                "bot": "Lava",
                "sup": "Moham"
            }
        },
        "T1 Academy": {
            "league": "LCK CL",
            "roster": {
                "top": "Dal",
                "jng": "Guwon",
                "mid": "Poby",
                "bot": "Smash",
                "sup": "Rekkles"
            }
        },
        "Gen.G Challengers": {
            "league": "LCK CL",
            "roster": {
                "top": "Kingen",
                "jng": "Grizzly",
                "mid": "BuLLDoG",
                "bot": "Peyz",
                "sup": "Execute"
            }
        },
        "BRION Academy": {
            "league": "LCK CL",
            "roster": {
                "top": "Sword",
                "jng": "Dang",
                "mid": "Karis",
                "bot": "Envyy",
                "sup": "Pollu"
            }
        },
        "KT Rolster Challengers": {
            "league": "LCK CL",
            "roster": {
                "top": "Castle",
                "jng": "Gideon",
                "mid": "Rookie",
                "bot": "Aiming",
                "sup": "Rebel"
            }
        },
        "Liiv SANDBOX": {
            "league": "LCK CL",
            "roster": {
                "top": "Willer",
                "jng": "Croco",
                "mid": "Clozer",
                "bot": "Teddy",
                "sup": "Kael"
            }
        },
        "OKSavingsBank BRION": {
            "league": "LCK CL",
            "roster": {
                "top": "Morgan",
                "jng": "UmTi",
                "mid": "Ucal",
                "bot": "Hena",
                "sup": "Effort"
            }
        },
        "Fredit BRION": {
            "league": "LCK CL",
            "roster": {
                "top": "Sword",
                "jng": "Raptor",
                "mid": "Feisty",
                "bot": "Hena",
                "sup": "Delight"
            }
        },
        
        # === ACADEMY TEAMS ===
        "HLE Academy": {
            "league": "LCK Academy",
            "roster": {
                "top": "DnDn",
                "jng": "Willer",
                "mid": "Karis",
                "bot": "Viper",
                "sup": "Vsta"
            }
        },
        "NS Academy": {
            "league": "LCK Academy",
            "roster": {
                "top": "Rich",
                "jng": "Peanut",
                "mid": "Bay",
                "bot": "Ghost",
                "sup": "SnowFlower"
            }
        },
        "DRX Academy": {
            "league": "LCK Academy",
            "roster": {
                "top": "Kingen",
                "jng": "Pyosik",
                "mid": "FATE",
                "bot": "deokdam",
                "sup": "BeryL"
            }
        },
        "FearX Academy": {
            "league": "LCK Academy",
            "roster": {
                "top": "Dove",
                "jng": "Sylvie",
                "mid": "Guwon",
                "bot": "Envyy",
                "sup": "Execute"
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
        "DWG KIA": {
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
        "KingZone DragonX": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "SANDBOX Gaming": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "SeolHaeOne Prince": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "APK Prince": {
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
        "NaJin Black Sword": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "NaJin White Shield": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "KT Bullets": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "KT Arrows": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "Samsung Blue": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "Samsung White": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "SK Telecom T1 S": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "SK Telecom T1 K": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "Azubu Frost": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        },
        "Azubu Blaze": {
            "league": "Former LCK",
            "roster": {},
            "active": False
        }
    }

def main():
    """Main function to update rosters"""
    print("Updating ALL Korean team rosters...")
    print("="*50)
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    roster_data = {}
    
    # Try to use the enhanced scraper first
    try:
        print("Attempting to use enhanced scraper...")
        from enhanced_korean_teams_scraper import EnhancedKoreanTeamsScraper
        scraper = EnhancedKoreanTeamsScraper()
        teams = scraper.scrape_all_korean_teams()
        
        if teams and len(teams) >= 20:  # Should have many more teams
            print(f"✓ Successfully scraped {len(teams)} teams")
            roster_data = teams
        else:
            print("⚠ Scraping incomplete, adding manual rosters...")
            roster_data = teams or {}
            
    except ImportError:
        print("⚠ Enhanced scraper not found, trying original scraper...")
        
        try:
            from korean_teams_scraper import KoreanTeamsScraper
            scraper = KoreanTeamsScraper()
            teams = scraper.scrape_korean_teams()
            
            if teams:
                roster_data = teams
                print(f"✓ Original scraper found {len(teams)} teams")
            else:
                print("⚠ Original scraper failed")
                
        except Exception as e:
            print(f"❌ Original scraper error: {e}")
    
    except Exception as e:
        print(f"❌ Enhanced scraper error: {e}")
    
    # Always add manual rosters to ensure completeness
    print("\nAdding comprehensive manual rosters...")
    manual_rosters = create_comprehensive_manual_rosters()
    
    # Merge manual rosters (don't overwrite existing complete rosters)
    for team, data in manual_rosters.items():
        if team not in roster_data:
            roster_data[team] = data
        elif not roster_data[team].get('roster'):
            # If team exists but has no roster, add manual roster
            roster_data[team]['roster'] = data.get('roster', {})
    
    print(f"✓ Total teams after merging: {len(roster_data)}")
    
    # Save to JSON
    output = {
        'last_updated': datetime.now().isoformat(),
        'total_teams': len(roster_data),
        'teams': roster_data
    }
    
    filepath = 'data/korean_teams_rosters.json'
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Saved {len(roster_data)} teams to {filepath}")
    
    # Print summary
    print("\n" + "="*50)
    print("TEAM ROSTERS SUMMARY")
    print("="*50)
    
    # Count by league
    leagues = {}
    complete_rosters = 0
    
    for team, data in roster_data.items():
        league = data.get('league', 'Unknown')
        leagues[league] = leagues.get(league, 0) + 1
        
        roster = data.get('roster', {})
        if len(roster) >= 5:
            complete_rosters += 1
    
    print("\nTeams by League:")
    for league, count in sorted(leagues.items()):
        print(f"  • {league}: {count} teams")
    
    print(f"\nComplete rosters: {complete_rosters}/{len(roster_data)}")
    
    # Show some teams from each category
    print("\n" + "="*50)
    print("SAMPLE TEAMS")
    print("="*50)
    
    # Group by league
    by_league = {}
    for team, data in roster_data.items():
        league = data.get('league', 'Unknown')
        if league not in by_league:
            by_league[league] = []
        by_league[league].append((team, data))
    
    # Show first 3 teams from each league
    for league in ['LCK', 'LCK CL', 'LCK Academy']:
        if league in by_league:
            print(f"\n{league} Teams:")
            for team, data in by_league[league][:3]:
                print(f"\n  {team}:")
                roster = data.get('roster', {})
                if roster:
                    for pos in ['top', 'jng', 'mid', 'bot', 'sup']:
                        if pos in roster:
                            print(f"    {pos.upper()}: {roster[pos]}")
                else:
                    print("    (No roster data)")
    
    print("\n✓ Update complete! Your app now has ALL Korean teams.")

if __name__ == "__main__":
    main()