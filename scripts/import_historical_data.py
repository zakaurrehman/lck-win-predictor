#!/usr/bin/env python3
"""
Scripts to import and format historical data for backtesting
Save as: scripts/import_historical_data.py
"""

import pandas as pd
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_sample_real_data():
    """
    Create sample real data files to show the expected format
    You should replace these with your actual historical data
    """
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # 1. Sample real odds data (from bookmakers)
    odds_data = [
        # Format: bookmaker, match datetime, team1, team2, team1 odds, team2 odds
        {'bookmaker': 'Bet365', 'commence_time': '2024-01-15T10:00:00', 'team1': 'T1', 'team2': 'Gen.G', 'team1_odds': 1.85, 'team2_odds': 2.10},
        {'bookmaker': 'DraftKings', 'commence_time': '2024-01-15T10:00:00', 'team1': 'T1', 'team2': 'Gen.G', 'team1_odds': 1.83, 'team2_odds': 2.15},
        {'bookmaker': 'Bet365', 'commence_time': '2024-01-17T14:00:00', 'team1': 'DWG KIA', 'team2': 'DRX', 'team1_odds': 2.20, 'team2_odds': 1.75},
        {'bookmaker': 'DraftKings', 'commence_time': '2024-01-17T14:00:00', 'team1': 'DWG KIA', 'team2': 'DRX', 'team1_odds': 2.25, 'team2_odds': 1.72},
        {'bookmaker': 'Bet365', 'commence_time': '2024-01-20T10:00:00', 'team1': 'T1', 'team2': 'KT Rolster', 'team1_odds': 1.65, 'team2_odds': 2.35},
        {'bookmaker': 'Bet365', 'commence_time': '2024-01-22T14:00:00', 'team1': 'Gen.G', 'team2': 'DWG KIA', 'team1_odds': 1.72, 'team2_odds': 2.25},
        {'bookmaker': 'Bet365', 'commence_time': '2024-01-25T10:00:00', 'team1': 'Fredit BRION', 'team2': 'T1', 'team1_odds': 3.50, 'team2_odds': 1.35},
        {'bookmaker': 'Bet365', 'commence_time': '2024-01-27T14:00:00', 'team1': 'DRX', 'team2': 'Nongshim RedForce', 'team1_odds': 1.90, 'team2_odds': 2.00},
    ]
    
    odds_df = pd.DataFrame(odds_data)
    odds_df.to_csv('data/real_odds.csv', index=False)
    print(f"✅ Created data/real_odds.csv with {len(odds_df)} records")
    
    # 2. Sample real match results
    match_results = [
        # Format: date, team1, team2, winner (1 or 2), match duration in seconds
        {'date': '2024-01-15', 'team1': 'T1', 'team2': 'Gen.G', 'winner': 1, 'duration': 2156},
        {'date': '2024-01-17', 'team1': 'DWG KIA', 'team2': 'DRX', 'winner': 2, 'duration': 2847},
        {'date': '2024-01-20', 'team1': 'T1', 'team2': 'KT Rolster', 'winner': 1, 'duration': 1923},
        {'date': '2024-01-22', 'team1': 'Gen.G', 'team2': 'DWG KIA', 'winner': 1, 'duration': 2534},
        {'date': '2024-01-25', 'team1': 'Fredit BRION', 'team2': 'T1', 'winner': 2, 'duration': 1876},
        {'date': '2024-01-27', 'team1': 'DRX', 'team2': 'Nongshim RedForce', 'winner': 1, 'duration': 2234},
    ]
    
    matches_df = pd.DataFrame(match_results)
    matches_df.to_csv('data/real_matches.csv', index=False)
    print(f"✅ Created data/real_matches.csv with {len(matches_df)} records")
    
    # 3. Sample champion picks (optional but recommended for better predictions)
    champion_picks = [
        {
            'date': '2024-01-15', 'team1': 'T1', 'team2': 'Gen.G',
            'team1_champ1': 'Aatrox', 'team1_champ2': 'Viego', 'team1_champ3': 'Azir', 'team1_champ4': 'Jinx', 'team1_champ5': 'Nautilus',
            'team2_champ1': "K'Sante", 'team2_champ2': 'Graves', 'team2_champ3': 'LeBlanc', 'team2_champ4': 'Aphelios', 'team2_champ5': 'Thresh',
            'team1_top': 'Zeus', 'team1_jng': 'Oner', 'team1_mid': 'Faker', 'team1_bot': 'Gumayusi', 'team1_sup': 'Keria',
            'team2_top': 'Kiin', 'team2_jng': 'Canyon', 'team2_mid': 'Chovy', 'team2_bot': 'Peyz', 'team2_sup': 'Lehends'
        },
        {
            'date': '2024-01-17', 'team1': 'DWG KIA', 'team2': 'DRX',
            'team1_champ1': 'Jax', 'team1_champ2': 'Lee Sin', 'team1_champ3': 'Syndra', 'team1_champ4': "Kai'Sa", 'team1_champ5': 'Leona',
            'team2_champ1': 'Renekton', 'team2_champ2': 'Xin Zhao', 'team2_champ3': 'Orianna', 'team2_champ4': 'Caitlyn', 'team2_champ5': 'Morgana',
            'team1_top': 'Canna', 'team1_jng': 'Lucid', 'team1_mid': 'Showmaker', 'team1_bot': 'Aiming', 'team1_sup': 'Kellin',
            'team2_top': 'Rascal', 'team2_jng': 'Croco', 'team2_mid': 'Fate', 'team2_bot': 'Teddy', 'team2_sup': 'Jun'
        },
    ]
    
    champions_df = pd.DataFrame(champion_picks)
    champions_df.to_csv('data/real_champion_picks.csv', index=False)
    print(f"✅ Created data/real_champion_picks.csv with {len(champions_df)} records")
    
    print("\n📌 These are sample files. Replace them with your actual historical data!")
    print("📌 Make sure the dates and teams match across all files")

def import_from_your_existing_data():
    """
    Helper function to import from your existing data structure
    Modify this based on where your historical data is stored
    """
    
    # Example: If you have match data in phase2_features/lck_matches_phase2.csv
    if os.path.exists('phase2_features/lck_matches_phase2.csv'):
        print("📊 Found existing match data...")
        
        # Load your match data
        matches = pd.read_csv('phase2_features/lck_matches_phase2.csv')
        
        # Transform to required format
        real_matches = []
        for _, match in matches.iterrows():
            real_matches.append({
                'date': match['date'],
                'team1': match['blue_team'],
                'team2': match['red_team'],
                'winner': 1 if match['blue_win'] == 1 else 2,
                'duration': match.get('gamelength', 1800)
            })
        
        # Save as real_matches.csv
        real_matches_df = pd.DataFrame(real_matches)
        real_matches_df.to_csv('data/real_matches.csv', index=False)
        print(f"✅ Imported {len(real_matches_df)} match results")
        
        # For champion picks
        real_champions = []
        for _, match in matches.iterrows():
            champ_data = {
                'date': match['date'],
                'team1': match['blue_team'],
                'team2': match['red_team']
            }
            
            # Add champions
            for i in range(1, 6):
                champ_data[f'team1_champ{i}'] = match.get(f'blue_champ{i}', 'Unknown')
                champ_data[f'team2_champ{i}'] = match.get(f'red_champ{i}', 'Unknown')
            
            # Add players if available
            for pos in ['top', 'jng', 'mid', 'bot', 'sup']:
                champ_data[f'team1_{pos}'] = match.get(f'blue_{pos}', 'Unknown')
                champ_data[f'team2_{pos}'] = match.get(f'red_{pos}', 'Unknown')
            
            real_champions.append(champ_data)
        
        champions_df = pd.DataFrame(real_champions)
        champions_df.to_csv('data/real_champion_picks.csv', index=False)
        print(f"✅ Imported {len(champions_df)} champion pick records")
        
        # Note: You'll need to get odds data from betting sites
        print("\n⚠️  You still need to add betting odds data!")
        print("   Odds should include: bookmaker, commence_time, team1, team2, team1_odds, team2_odds")

def scrape_odds_from_api():
    """
    Example of how to get odds from an API
    You'll need to sign up for an odds API service
    """
    print("\n📊 To get real odds data, you can:")
    print("1. Use The Odds API (https://the-odds-api.com/)")
    print("2. Scrape from betting sites (check their ToS)")
    print("3. Use historical odds databases")
    
    print("\nExample API code:")
    print("""
import requests

API_KEY = 'your_api_key_here'
SPORT = 'league-of-legends'
REGION = 'us'
MARKET = 'h2h'

url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds'
params = {
    'api_key': API_KEY,
    'regions': REGION,
    'markets': MARKET
}

response = requests.get(url, params=params)
odds_data = response.json()

# Transform to our format
for game in odds_data:
    for bookmaker in game['bookmakers']:
        odds_record = {
            'bookmaker': bookmaker['key'],
            'commence_time': game['commence_time'],
            'team1': game['home_team'],
            'team2': game['away_team'],
            'team1_odds': bookmaker['markets'][0]['outcomes'][0]['price'],
            'team2_odds': bookmaker['markets'][0]['outcomes'][1]['price']
        }
""")

def validate_data_compatibility():
    """Validate that your data files are compatible"""
    print("\n🔍 Validating data compatibility...")
    
    issues = []
    
    # Check odds file
    if os.path.exists('data/real_odds.csv'):
        odds_df = pd.read_csv('data/real_odds.csv')
        required_cols = ['bookmaker', 'commence_time', 'team1', 'team2', 'team1_odds', 'team2_odds']
        missing_cols = [col for col in required_cols if col not in odds_df.columns]
        
        if missing_cols:
            issues.append(f"Odds file missing columns: {missing_cols}")
        else:
            print("✅ Odds file structure is correct")
            
        # Check data types
        if 'team1_odds' in odds_df.columns:
            if odds_df['team1_odds'].dtype not in ['float64', 'int64']:
                issues.append("team1_odds should be numeric")
            if odds_df['team2_odds'].dtype not in ['float64', 'int64']:
                issues.append("team2_odds should be numeric")
    else:
        issues.append("data/real_odds.csv not found")
    
    # Check matches file
    if os.path.exists('data/real_matches.csv'):
        matches_df = pd.read_csv('data/real_matches.csv')
        required_cols = ['date', 'team1', 'team2', 'winner']
        missing_cols = [col for col in required_cols if col not in matches_df.columns]
        
        if missing_cols:
            issues.append(f"Matches file missing columns: {missing_cols}")
        else:
            print("✅ Matches file structure is correct")
            
        # Check winner values
        if 'winner' in matches_df.columns:
            invalid_winners = matches_df[~matches_df['winner'].isin([1, 2])]
            if len(invalid_winners) > 0:
                issues.append(f"{len(invalid_winners)} matches have invalid winner values (must be 1 or 2)")
    else:
        issues.append("data/real_matches.csv not found")
    
    # Check team name consistency
    if os.path.exists('data/real_odds.csv') and os.path.exists('data/real_matches.csv'):
        odds_df = pd.read_csv('data/real_odds.csv')
        matches_df = pd.read_csv('data/real_matches.csv')
        
        odds_teams = set(odds_df['team1'].unique()) | set(odds_df['team2'].unique())
        match_teams = set(matches_df['team1'].unique()) | set(matches_df['team2'].unique())
        
        teams_only_in_odds = odds_teams - match_teams
        teams_only_in_matches = match_teams - odds_teams
        
        if teams_only_in_odds:
            issues.append(f"Teams in odds but not matches: {teams_only_in_odds}")
        if teams_only_in_matches:
            issues.append(f"Teams in matches but not odds: {teams_only_in_matches}")
        
        if not teams_only_in_odds and not teams_only_in_matches:
            print("✅ Team names are consistent across files")
    
    # Report issues
    if issues:
        print("\n❌ Found issues:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ All data files are valid and compatible!")
    
    return len(issues) == 0

def merge_with_predictions():
    """Test merging historical data with model predictions"""
    print("\n🧪 Testing data with prediction model...")
    
    try:
        from app import prediction_app
        
        # Load a sample match
        if os.path.exists('data/real_matches.csv') and os.path.exists('data/real_champion_picks.csv'):
            matches_df = pd.read_csv('data/real_matches.csv')
            champions_df = pd.read_csv('data/real_champion_picks.csv')
            
            # Get first match
            match = matches_df.iloc[0]
            champ_match = champions_df[
                (champions_df['team1'] == match['team1']) & 
                (champions_df['team2'] == match['team2'])
            ]
            
            if not champ_match.empty:
                champ_data = champ_match.iloc[0]
                
                # Create match data for prediction
                match_data = {
                    'blue_team': match['team1'],
                    'red_team': match['team2']
                }
                
                # Add champions
                for i in range(1, 6):
                    match_data[f'blue_champ{i}'] = champ_data[f'team1_champ{i}']
                    match_data[f'red_champ{i}'] = champ_data[f'team2_champ{i}']
                
                # Add players
                for pos in ['top', 'jng', 'mid', 'bot', 'sup']:
                    match_data[f'blue_{pos}'] = champ_data.get(f'team1_{pos}', 'Unknown')
                    match_data[f'red_{pos}'] = champ_data.get(f'team2_{pos}', 'Unknown')
                
                # Test prediction
                print(f"\nTesting prediction for: {match['team1']} vs {match['team2']}")
                result = prediction_app.predict_match(match_data)
                
                print(f"Model prediction: {result['blue_win_probability']:.2%} for {match['team1']}")
                print(f"Actual winner: {'Blue' if match['winner'] == 1 else 'Red'} Team")
                print("✅ Model integration successful!")
            else:
                print("⚠️  No champion data found for test match")
        else:
            print("⚠️  Need both match and champion data files to test")
            
    except Exception as e:
        print(f"❌ Error testing prediction: {e}")

def create_data_summary():
    """Create a summary of available data"""
    print("\n📊 DATA SUMMARY")
    print("=" * 50)
    
    # Check each data file
    files = {
        'data/real_odds.csv': 'Betting Odds',
        'data/real_matches.csv': 'Match Results',
        'data/real_champion_picks.csv': 'Champion Picks'
    }
    
    for filepath, description in files.items():
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            print(f"\n{description}:")
            print(f"  - Records: {len(df)}")
            
            if 'date' in df.columns or 'commence_time' in df.columns:
                date_col = 'date' if 'date' in df.columns else 'commence_time'
                dates = pd.to_datetime(df[date_col])
                print(f"  - Date range: {dates.min().date()} to {dates.max().date()}")
            
            if 'team1' in df.columns:
                teams = set(df['team1'].unique()) | set(df['team2'].unique())
                print(f"  - Teams: {len(teams)} unique ({', '.join(sorted(teams)[:5])}...)")
            
            print(f"  - Columns: {', '.join(df.columns)}")
        else:
            print(f"\n{description}: NOT FOUND")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Import historical data for backtesting')
    parser.add_argument('--create-sample', action='store_true', help='Create sample data files')
    parser.add_argument('--import-existing', action='store_true', help='Import from existing project data')
    parser.add_argument('--validate', action='store_true', help='Validate data compatibility')
    parser.add_argument('--test', action='store_true', help='Test with prediction model')
    parser.add_argument('--summary', action='store_true', help='Show data summary')
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_real_data()
    elif args.import_existing:
        import_from_your_existing_data()
    elif args.validate:
        validate_data_compatibility()
    elif args.test:
        merge_with_predictions()
    elif args.summary:
        create_data_summary()
    else:
        # Run all
        print("🚀 LCK Historical Data Import Tool\n")
        create_sample_real_data()
        print("\n" + "="*50)
        validate_data_compatibility()
        print("\n" + "="*50)
        create_data_summary()