#!/usr/bin/env python3
"""
Debug script to check what features your model actually expects
"""

import pandas as pd
import numpy as np
import joblib
import os

def analyze_training_features():
    """Analyze the actual features your model was trained on"""
    print("=== ANALYZING TRAINING FEATURES ===\n")
    
    # 1. Load the actual advanced features that were used for training
    if os.path.exists('data/enhanced/advanced_features.csv'):
        print("✅ Found advanced_features.csv")
        df = pd.read_csv('data/enhanced/advanced_features.csv')
        
        print(f"Training data shape: {df.shape}")
        print(f"Number of features: {df.shape[1] - 2}")  # Minus gameid and blue_win
        
        # Get feature columns (excluding gameid and blue_win)
        feature_cols = [col for col in df.columns if col not in ['gameid', 'blue_win']]
        
        print(f"\n=== ACTUAL FEATURE COLUMNS ({len(feature_cols)}) ===")
        for i, col in enumerate(feature_cols, 1):
            print(f"{i:3d}. {col}")
        
        print("\n=== FEATURE CATEGORIES ===")
        categories = {}
        for col in feature_cols:
            if 'blue_' in col and '_diff' not in col:
                category = col.replace('blue_', '')
                categories.setdefault('Blue Team Features', []).append(col)
            elif 'red_' in col and '_diff' not in col:
                category = col.replace('red_', '')
                categories.setdefault('Red Team Features', []).append(col)
            elif '_diff' in col:
                categories.setdefault('Difference Features', []).append(col)
            elif 'synergy' in col:
                categories.setdefault('Synergy Features', []).append(col)
            elif 'elo' in col:
                categories.setdefault('Player ELO Features', []).append(col)
            elif 'advantage' in col:
                categories.setdefault('Lane Advantage Features', []).append(col)
            elif 'recent' in col or 'historical' in col:
                categories.setdefault('Team History Features', []).append(col)
            elif 'patch' in col:
                categories.setdefault('Patch Features', []).append(col)
            else:
                categories.setdefault('Other Features', []).append(col)
        
        for category, features in categories.items():
            print(f"\n{category} ({len(features)}):")
            for feature in features[:10]:  # Show first 10
                print(f"  - {feature}")
            if len(features) > 10:
                print(f"  ... and {len(features) - 10} more")
        
        return feature_cols
    else:
        print("❌ advanced_features.csv not found!")
        return None

def check_model_expectations():
    """Check what the actual model expects"""
    print("\n=== ANALYZING MODEL EXPECTATIONS ===\n")
    
    model_path = 'models/final_phase3_models.pkl'
    if os.path.exists(model_path):
        try:
            model_data = joblib.load(model_path)
            print("✅ Model loaded successfully")
            
            if isinstance(model_data, dict):
                print("Model is stored as dictionary with keys:")
                for key in model_data.keys():
                    print(f"  - {key}: {type(model_data[key])}")
                
                # Check for feature columns
                if 'feature_columns' in model_data:
                    features = model_data['feature_columns']
                    print(f"\n✅ Model expects {len(features)} features:")
                    for i, feature in enumerate(features, 1):
                        print(f"{i:3d}. {feature}")
                    return features
                elif 'features' in model_data:
                    features = model_data['features']
                    print(f"\n✅ Model expects {len(features)} features:")
                    for i, feature in enumerate(features, 1):
                        print(f"{i:3d}. {feature}")
                    return features
                else:
                    print("⚠️ No feature column information found in model")
                    
                # Check the actual model
                actual_model = model_data.get('model') or model_data.get('best_model') or model_data.get('ensemble')
                if actual_model and hasattr(actual_model, 'feature_names_in_'):
                    features = actual_model.feature_names_in_
                    print(f"\n✅ Model feature_names_in_ has {len(features)} features:")
                    for i, feature in enumerate(features, 1):
                        print(f"{i:3d}. {feature}")
                    return features
                    
            else:
                print("Model is stored as raw model object")
                if hasattr(model_data, 'feature_names_in_'):
                    features = model_data.feature_names_in_
                    print(f"\n✅ Model expects {len(features)} features:")
                    for i, feature in enumerate(features, 1):
                        print(f"{i:3d}. {feature}")
                    return features
                    
        except Exception as e:
            print(f"❌ Error loading model: {e}")
    else:
        print("❌ Model file not found!")
    
    return None

def create_sample_features():
    """Create a sample feature vector to test"""
    print("\n=== CREATING SAMPLE FEATURE VECTOR ===\n")
    
    # Sample match data
    sample_data = {
        'blue_team': 'T1',
        'red_team': 'Gen.G',
        'blue_champ1': 'Aatrox',
        'blue_champ2': 'Viego', 
        'blue_champ3': 'Azir',
        'blue_champ4': 'Jinx',
        'blue_champ5': 'Nautilus',
        'red_champ1': "K'Sante",
        'red_champ2': 'Graves',
        'red_champ3': 'LeBlanc',
        'red_champ4': 'Aphelios',
        'red_champ5': 'Thresh',
        'blue_top': 'Zeus',
        'blue_jng': 'Oner',
        'blue_mid': 'Faker',
        'blue_bot': 'Gumayusi',
        'blue_sup': 'Keria',
        'red_top': 'Kiin',
        'red_jng': 'Canyon',
        'red_mid': 'Chovy',
        'red_bot': 'Peyz',
        'red_sup': 'Lehends'
    }
    
    print("Sample match:")
    print(f"Blue Team: {sample_data['blue_team']} ({', '.join([sample_data[f'blue_champ{i}'] for i in range(1, 6)])})")
    print(f"Red Team: {sample_data['red_team']} ({', '.join([sample_data[f'red_champ{i}'] for i in range(1, 6)])})")
    
    return sample_data

def main():
    """Main function"""
    print("🔍 LCK MODEL FEATURE DEBUGGER")
    print("=" * 50)
    
    # 1. Analyze training features
    training_features = analyze_training_features()
    
    # 2. Check model expectations  
    model_features = check_model_expectations()
    
    # 3. Compare them
    if training_features and model_features:
        print(f"\n=== FEATURE COMPARISON ===")
        print(f"Training features: {len(training_features)}")
        print(f"Model features: {len(model_features)}")
        
        if set(training_features) == set(model_features):
            print("✅ Features match perfectly!")
        else:
            print("❌ Feature mismatch detected!")
            
            missing_in_model = set(training_features) - set(model_features)
            missing_in_training = set(model_features) - set(training_features)
            
            if missing_in_model:
                print(f"\nFeatures in training but not in model ({len(missing_in_model)}):")
                for feature in missing_in_model:
                    print(f"  - {feature}")
                    
            if missing_in_training:
                print(f"\nFeatures in model but not in training ({len(missing_in_training)}):")
                for feature in missing_in_training:
                    print(f"  - {feature}")
    
    # 4. Create sample features
    sample_data = create_sample_features()
    
    print(f"\n=== SUMMARY ===")
    print("To fix the Flask app, we need to create features that exactly match")
    print("the training feature names and order.")
    
    if training_features:
        print(f"\nSave this feature list for the Flask app:")
        print("REQUIRED_FEATURES = [")
        for feature in training_features:
            print(f"    '{feature}',")
        print("]")

if __name__ == "__main__":
    main()