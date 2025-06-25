# model_diagnosis.py
"""
Diagnose issues with the current LCK model
"""

import pandas as pd
import numpy as np
import os
import joblib
import json

def diagnose_current_model():
    """Diagnose issues with current model"""
    print("🔍 LCK MODEL DIAGNOSIS")
    print("="*50)
    
    issues_found = []
    
    # Check 1: Model file exists
    model_path = 'models/final_phase3_models.pkl'
    if not os.path.exists(model_path):
        issues_found.append("❌ Model file not found")
        print("❌ Model file not found:", model_path)
    else:
        print("✅ Model file exists")
        
        # Check 2: Can load model
        try:
            model_data = joblib.load(model_path)
            print("✅ Model can be loaded")
            
            # Check 3: Model structure
            if isinstance(model_data, dict):
                print("✅ Model is stored as dictionary")
                print("   Keys:", list(model_data.keys()))
                
                # Check for required components
                if 'model' in model_data or 'best_model' in model_data:
                    actual_model = model_data.get('best_model') or model_data.get('model')
                    print("✅ Model object found")
                    
                    # Test model prediction
                    try:
                        if hasattr(actual_model, 'predict'):
                            # Create dummy input
                            if 'feature_columns' in model_data:
                                features = model_data['feature_columns']
                                dummy_input = pd.DataFrame([{col: 0.5 for col in features}])
                                pred = actual_model.predict(dummy_input)
                                prob = actual_model.predict_proba(dummy_input)
                                print(f"✅ Model can make predictions: {pred[0]}")
                                print(f"✅ Model probabilities: {prob[0]}")
                            else:
                                issues_found.append("❌ No feature_columns in model")
                                print("❌ No feature_columns found in model")
                        else:
                            issues_found.append("❌ Model has no predict method")
                            print("❌ Model has no predict method")
                    except Exception as e:
                        issues_found.append(f"❌ Model prediction failed: {e}")
                        print(f"❌ Model prediction failed: {e}")
                else:
                    issues_found.append("❌ No model object in saved data")
                    print("❌ No model object found in saved data")
            else:
                print("✅ Model is raw object")
                
        except Exception as e:
            issues_found.append(f"❌ Cannot load model: {e}")
            print(f"❌ Cannot load model: {e}")
    
    # Check 4: Training data exists
    features_path = "data/enhanced/advanced_features.csv"
    if not os.path.exists(features_path):
        issues_found.append("❌ Training data not found")
        print("❌ Training data not found:", features_path)
    else:
        print("✅ Training data exists")
        
        try:
            df = pd.read_csv(features_path)
            print(f"✅ Training data shape: {df.shape}")
            
            if 'blue_win' not in df.columns:
                issues_found.append("❌ No target variable in training data")
                print("❌ No 'blue_win' column in training data")
            else:
                print("✅ Target variable found")
                
        except Exception as e:
            issues_found.append(f"❌ Cannot read training data: {e}")
            print(f"❌ Cannot read training data: {e}")
    
    # Check 5: Flask app compatibility
    print("\n🌐 FLASK APP COMPATIBILITY")
    print("-"*30)
    
    try:
        from app import ExactFeatureCreator, REQUIRED_FEATURES
        print("✅ Can import app components")
        print(f"✅ Required features list has {len(REQUIRED_FEATURES)} items")
        
        # Test feature creator
        try:
            feature_creator = ExactFeatureCreator()
            print("✅ Feature creator can be initialized")
        except Exception as e:
            issues_found.append(f"❌ Feature creator fails: {e}")
            print(f"❌ Feature creator initialization failed: {e}")
            
    except Exception as e:
        issues_found.append(f"❌ Cannot import app: {e}")
        print(f"❌ Cannot import app components: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("DIAGNOSIS SUMMARY")
    print("="*50)
    
    if not issues_found:
        print("🎉 No issues found! Model should be working properly.")
        print("   If you're still having problems, try restarting Flask app.")
        return True
    else:
        print(f"❌ Found {len(issues_found)} issues:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print("\n💡 RECOMMENDED ACTIONS:")
        
        if any("Model file not found" in issue for issue in issues_found):
            print("   1. Run complete model retraining:")
            print("      python lck_model_retrainer.py")
        
        if any("Training data not found" in issue for issue in issues_found):
            print("   2. Generate features first:")
            print("      python run_phase2_features.py")
        
        if any("feature_columns" in issue for issue in issues_found):
            print("   3. Model missing feature information - retrain required")
        
        if any("Flask app" in issue or "app" in issue for issue in issues_found):
            print("   4. Fix Flask app compatibility issues")
        
        print("\n🔄 QUICK FIX: Run the complete retrainer:")
        print("   python lck_model_retrainer.py")
        
        return False

def check_feature_mismatch():
    """Check for feature mismatches between model and app"""
    print("\n🔍 FEATURE MISMATCH ANALYSIS")
    print("-"*40)
    
    try:
        # Load model features
        model_path = 'models/final_phase3_models.pkl'
        if os.path.exists(model_path):
            model_data = joblib.load(model_path)
            model_features = model_data.get('feature_columns', [])
            print(f"Model expects {len(model_features)} features")
        else:
            print("❌ No model file to check")
            return
        
        # Load training features
        features_path = "data/enhanced/advanced_features.csv"
        if os.path.exists(features_path):
            df = pd.read_csv(features_path)
            training_features = [col for col in df.columns if col not in ['gameid', 'blue_win']]
            print(f"Training data has {len(training_features)} features")
        else:
            print("❌ No training data to check")
            return
        
        # Check app features
        try:
            from app import REQUIRED_FEATURES
            app_features = REQUIRED_FEATURES
            print(f"App expects {len(app_features)} features")
        except:
            print("❌ Cannot load app features")
            return
        
        # Compare features
        model_set = set(model_features)
        training_set = set(training_features)
        app_set = set(app_features)
        
        if model_set == training_set == app_set:
            print("✅ All features match perfectly!")
        else:
            print("❌ Feature mismatch detected:")
            
            if model_set != training_set:
                missing_in_model = training_set - model_set
                extra_in_model = model_set - training_set
                
                if missing_in_model:
                    print(f"   Features in training but not model: {len(missing_in_model)}")
                    for feat in list(missing_in_model)[:5]:
                        print(f"     - {feat}")
                    if len(missing_in_model) > 5:
                        print(f"     ... and {len(missing_in_model)-5} more")
                
                if extra_in_model:
                    print(f"   Features in model but not training: {len(extra_in_model)}")
                    for feat in list(extra_in_model)[:5]:
                        print(f"     - {feat}")
            
            if app_set != model_set:
                print(f"   App vs Model feature count: {len(app_set)} vs {len(model_set)}")
                
    except Exception as e:
        print(f"❌ Feature comparison failed: {e}")

def test_prediction_pipeline():
    """Test the complete prediction pipeline"""
    print("\n🧪 PREDICTION PIPELINE TEST")
    print("-"*35)
    
    try:
        # Test data
        test_match = {
            'blue_team': 'T1',
            'red_team': 'Gen.G',
            'blue_champ1': 'Aatrox', 'blue_champ2': 'Viego', 'blue_champ3': 'Azir', 
            'blue_champ4': 'Jinx', 'blue_champ5': 'Nautilus',
            'red_champ1': "K'Sante", 'red_champ2': 'Graves', 'red_champ3': 'LeBlanc', 
            'red_champ4': 'Aphelios', 'red_champ5': 'Thresh',
            'blue_top': 'Zeus', 'blue_jng': 'Oner', 'blue_mid': 'Faker', 
            'blue_bot': 'Gumayusi', 'blue_sup': 'Keria',
            'red_top': 'Kiin', 'red_jng': 'Canyon', 'red_mid': 'Chovy', 
            'red_bot': 'Peyz', 'red_sup': 'Lehends'
        }
        
        print("Test match: T1 vs Gen.G")
        
        # Step 1: Feature creation
        try:
            from app import ExactFeatureCreator
            feature_creator = ExactFeatureCreator()
            features = feature_creator.create_exact_features(test_match)
            print(f"✅ Features created: {len(features)} features")
        except Exception as e:
            print(f"❌ Feature creation failed: {e}")
            return
        
        # Step 2: Load model
        try:
            model_data = joblib.load('models/final_phase3_models.pkl')
            model = model_data.get('best_model') or model_data.get('model')
            expected_features = model_data.get('feature_columns', [])
            print("✅ Model loaded")
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            return
        
        # Step 3: Prepare features for model
        try:
            feature_vector = []
            for feature_name in expected_features:
                feature_vector.append(features.get(feature_name, 0))
            
            X = pd.DataFrame([feature_vector], columns=expected_features)
            print(f"✅ Feature vector prepared: shape {X.shape}")
        except Exception as e:
            print(f"❌ Feature vector preparation failed: {e}")
            return
        
        # Step 4: Make prediction
        try:
            prediction = model.predict(X)[0]
            probabilities = model.predict_proba(X)[0]
            
            blue_prob = probabilities[1] * 100
            red_prob = probabilities[0] * 100
            
            print(f"✅ Prediction successful:")
            print(f"   Winner: {'Blue (T1)' if prediction == 1 else 'Red (Gen.G)'}")
            print(f"   Blue probability: {blue_prob:.1f}%")
            print(f"   Red probability: {red_prob:.1f}%")
            
            # Check if probabilities are reasonable
            if 20 <= blue_prob <= 80:
                print("✅ Probabilities look reasonable")
            else:
                print("⚠️  Probabilities seem extreme - model may need retraining")
                
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            return
        
        print("✅ Complete pipeline test passed!")
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")

def generate_fix_script():
    """Generate a script to fix common issues"""
    print("\n🔧 GENERATING FIX SCRIPT")
    print("-"*30)
    
    fix_script = '''#!/usr/bin/env python3
# auto_fix_model.py - Automatically fix LCK model issues

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🚀 AUTO-FIXING LCK MODEL ISSUES")
    print("="*40)
    
    # Check if training data exists
    if not os.path.exists("data/enhanced/advanced_features.csv"):
        print("📊 Generating features...")
        if not run_command("python run_phase2_features.py", "Feature generation"):
            print("❌ Cannot proceed without features")
            return
    
    # Retrain model
    print("🤖 Retraining model...")
    if not run_command("python lck_model_retrainer.py", "Model retraining"):
        print("❌ Model retraining failed")
        return
    
    # Test the fix
    print("🧪 Testing fixed model...")
    if run_command("python model_diagnosis.py", "Model testing"):
        print("🎉 Model fixed successfully!")
    else:
        print("❌ Issues still remain")

if __name__ == "__main__":
    main()
'''
    
    with open("auto_fix_model.py", "w") as f:
        f.write(fix_script)
    
    print("✅ Created auto_fix_model.py")
    print("   Run: python auto_fix_model.py")

def main():
    """Main diagnosis function"""
    print("🏥 LCK MODEL HEALTH CHECK")
    print("="*50)
    
    # Run main diagnosis
    model_healthy = diagnose_current_model()
    
    # Check feature mismatches
    check_feature_mismatch()
    
    # Test prediction pipeline
    test_prediction_pipeline()
    
    # Generate fix script
    generate_fix_script()
    
    print("\n" + "="*50)
    print("FINAL RECOMMENDATION")
    print("="*50)
    
    if model_healthy:
        print("✅ Your model appears to be working!")
        print("   If you're still having issues:")
        print("   1. Restart your Flask app: python app.py")
        print("   2. Clear browser cache")
        print("   3. Check Flask console for errors")
    else:
        print("❌ Your model needs fixing!")
        print("   QUICK FIX OPTIONS:")
        print("   1. Run auto-fix: python auto_fix_model.py")
        print("   2. Manual retrain: python lck_model_retrainer.py") 
        print("   3. Full rebuild: python run_phase2_features.py then python lck_model_retrainer.py")
    
    print("\n💡 After fixing, test with: python model_diagnosis.py")

if __name__ == "__main__":
    main()