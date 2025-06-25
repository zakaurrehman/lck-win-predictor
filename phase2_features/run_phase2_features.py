import pandas as pd
from phase2_features.champion_synergy_calculator import ChampionSynergyCalculator
from phase2_features.matchup_history_analyzer import MatchupHistoryAnalyzer
from phase2_features.team_composition_analyzer import TeamCompositionAnalyzer
from phase2_features.advanced_feature_creator import AdvancedFeatureCreator

def run_phase2():
    """Execute all Phase 2 feature engineering"""
    print("="*60)
    print("PHASE 2: FEATURE ENGINEERING")
    print("="*60)
    
    # Load enhanced dataset from Phase 1
    df = pd.read_csv("data/enhanced/lck_full_dataset.csv")
    df['date'] = pd.to_datetime(df['date'])
    
    # Step 1: Calculate champion synergies
    print("\n1. Calculating champion synergies...")
    synergy_calc = ChampionSynergyCalculator(df)
    synergy_calc.calculate_all_synergies()
    
    # Step 2: Analyze matchup history
    print("\n2. Analyzing historical matchups...")
    matchup_analyzer = MatchupHistoryAnalyzer(df)
    matchup_analyzer.analyze_all_matchups()
    
    # Step 3: Create advanced features for all games
    print("\n3. Creating advanced features for all games...")
    feature_creator = AdvancedFeatureCreator()
    
    all_features = []
    for idx, game in df.iterrows():
        if idx % 500 == 0:
            print(f"  Processing game {idx}/{len(df)}...")
        
        features = feature_creator.create_game_features(game)
        features['gameid'] = game['gameid']
        features['blue_win'] = game['blue_win']
        all_features.append(features)
    
    # Save enhanced features
    features_df = pd.DataFrame(all_features)
    features_df.to_csv("data/enhanced/advanced_features.csv", index=False)
    
    print("\n" + "="*60)
    print("PHASE 2 COMPLETE!")
    print("="*60)
    print(f"✓ Created {len(features_df.columns)} advanced features")
    print(f"✓ Processed {len(features_df)} games")
    print("\nFeature categories:")
    print("  - Champion synergies")
    print("  - Lane matchups")
    print("  - Player skills (ELO)")
    print("  - Team compositions")
    print("  - Historical matchups")
    print("  - Recent form")
    print("\nNext: Run Phase 3 - Model Improvement")

if __name__ == "__main__":
    run_phase2()