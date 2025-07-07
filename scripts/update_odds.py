# scripts/update_odds.py
"""
Script to regularly update odds data
"""

import schedule
import time
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collection.odds_scraper import LCKOddsScraper
from data_collection.match_scraper import LCKMatchScraper
from data_collection.data_validator import DataValidator

def update_daily_odds():
    """Update odds data for recent matches"""
    print(f"🕐 Starting daily odds update at {datetime.now()}")
    
    scraper = LCKOddsScraper()
    
    # Get odds for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    try:
        # Scrape odds (you'll need API keys for paid services)
        odds_data = scraper.scrape_esports_betting_sites(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if odds_data:
            scraper.save_odds_data(odds_data)
            print(f"✅ Updated {len(odds_data)} odds records")
        else:
            print("⚠️ No new odds data found")
            
    except Exception as e:
        print(f"❌ Error updating odds: {e}")

def update_match_results():
    """Update match results"""
    print(f"🕐 Starting match results update at {datetime.now()}")
    
    scraper = LCKMatchScraper()
    
    # Get matches for last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    try:
        matches = scraper.scrape_leaguepedia(
            start_year=start_date.year,
            end_year=end_date.year
        )
        
        if matches:
            scraper.save_match_data(matches)
            print(f"✅ Updated {len(matches)} match records")
        else:
            print("⚠️ No new match data found")
            
    except Exception as e:
        print(f"❌ Error updating matches: {e}")

def validate_and_merge_data():
    """Validate and merge all data"""
    print("🔍 Validating and merging data...")
    
    validator = DataValidator()
    
    try:
        # Load and validate odds data
        odds_file = 'data/odds/historical_odds.csv'
        matches_file = 'data/matches/match_results.csv'
        
        if os.path.exists(odds_file) and os.path.exists(matches_file):
            import pandas as pd
            
            odds_df = pd.read_csv(odds_file)
            matches_df = pd.read_csv(matches_file)
            
            # Validate
            odds_df, odds_issues = validator.validate_odds_data(odds_df)
            matches_df, match_issues = validator.validate_match_data(matches_df)
            
            # Merge
            merged_df = validator.merge_odds_and_matches(odds_df, matches_df)
            
            # Save merged data
            merged_df.to_csv('data/merged_betting_data.csv', index=False)
            
            print(f"✅ Merged data: {len(merged_df)} records")
            print(f"📊 Odds issues: {len(odds_issues)}")
            print(f"📊 Match issues: {len(match_issues)}")
            
        else:
            print("❌ Required data files not found")
            
    except Exception as e:
        print(f"❌ Error validating data: {e}")

def main():
    """Main update function"""
    print("🚀 LCK DATA UPDATE SERVICE")
    print("=" * 40)
    
    # Update odds data
    update_daily_odds()
    
    # Update match results
    update_match_results()
    
    # Validate and merge
    validate_and_merge_data()
    
    print("✅ Data update complete!")

def schedule_updates():
    """Schedule regular updates"""
    # Schedule daily updates at 6 AM
    schedule.every().day.at("06:00").do(main)
    
    # Schedule immediate run for testing
    schedule.every(10).seconds.do(main).tag('immediate')
    
    print("📅 Scheduled daily updates at 6:00 AM")
    print("⏰ Running immediate update in 10 seconds...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Update LCK betting data')
    parser.add_argument('--schedule', action='store_true', 
                       help='Run scheduled updates')
    parser.add_argument('--once', action='store_true', 
                       help='Run update once and exit')
    
    args = parser.parse_args()
    
    if args.schedule:
        schedule_updates()
    elif args.once:
        main()
    else:
        print("Use --once for single update or --schedule for continuous updates")
