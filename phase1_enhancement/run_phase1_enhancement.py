# run_phase1_enhancement.py
from enhanced_data_collector import EnhancedDataCollector
from player_stats_collector import PlayerStatsCalculator
from patch_analyzer import PatchAnalyzer
import pandas as pd

def run_phase1():
    """Execute all Phase 1 enhancements"""
    print("="*60)
    print("PHASE 1: DATA ENHANCEMENT")
    print("="*60)
    
    # Step 1: Collect enhanced data
    print("\n1. Collecting enhanced dataset...")
    collector = EnhancedDataCollector()
    df = collector.collect_all_sources()
    
    if df is None or len(df) < 1000:
        print("Warning: Insufficient data collected. Using existing data...")
        df = pd.read_csv("data/raw/lck_combined.csv")
    
    # Step 2: Calculate player statistics
    print("\n2. Calculating player statistics...")
    player_calc = PlayerStatsCalculator(df)
    player_calc.calculate_all_stats()
    
    # Step 3: Analyze patches
    print("\n3. Analyzing patch data...")
    patch_analyzer = PatchAnalyzer(df)
    patch_analyzer.analyze_patches()
    
    # Summary
    print("\n" + "="*60)
    print("PHASE 1 COMPLETE!")
    print("="*60)
    print(f"✓ Total matches: {len(df)}")
    print(f"✓ Player stats calculated")
    print(f"✓ Patch analysis complete")
    print("\nNext: Run Phase 2 - Feature Engineering")

if __name__ == "__main__":
    run_phase1()