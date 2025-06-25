# run_phase3_models_simple.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
import xgboost as xgb
import lightgbm as lgb
import joblib

def run_phase3_simple():
    print("="*60)
    print("PHASE 3: MODEL IMPROVEMENT (No TensorFlow)")
    print("="*60)
    
    # Load data
    print("\n1. Loading data...")
    features_df = pd.read_csv("data/enhanced/advanced_features.csv")
    
    # Prepare data
    feature_cols = [col for col in features_df.columns 
                   if col not in ['gameid', 'blue_win']]
    X = features_df[feature_cols].fillna(0)
    y = features_df['blue_win']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train multiple models
    print("\n2. Training models...")
    
    models = {
        'xgboost': xgb.XGBClassifier(n_estimators=200, max_depth=6, random_state=42),
        'lightgbm': lgb.LGBMClassifier(n_estimators=200, num_leaves=31, random_state=42),
        'random_forest': RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),
        'gradient_boost': GradientBoostingClassifier(n_estimators=100, max_depth=6, random_state=42),
        'logistic': LogisticRegression(max_iter=1000, random_state=42)
    }
    
    trained_models = {}
    results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
        
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        
        trained_models[name] = model
        results[name] = {'accuracy': accuracy, 'auc': auc}
        print(f"  {name} - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
    
    # Create ensemble
    print("\n3. Creating ensemble...")
    ensemble = VotingClassifier(
        estimators=[
            ('xgb', trained_models['xgboost']),
            ('lgb', trained_models['lightgbm']),
            ('rf', trained_models['random_forest'])
        ],
        voting='soft'
    )
    
    ensemble.fit(X_train, y_train)
    
    # Evaluate ensemble
    ensemble_pred = ensemble.predict(X_test)
    ensemble_proba = ensemble.predict_proba(X_test)[:, 1]
    ensemble_accuracy = accuracy_score(y_test, ensemble_pred)
    ensemble_auc = roc_auc_score(y_test, ensemble_proba)
    
    print(f"\nEnsemble Results:")
    print(f"  Accuracy: {ensemble_accuracy:.4f}")
    print(f"  AUC: {ensemble_auc:.4f}")
    
    # Save best model
    best_model_name = max(results.items(), key=lambda x: x[1]['auc'])[0]
    print(f"\nBest individual model: {best_model_name}")
    
    # Save models
    final_models = {
        'ensemble': ensemble,
        'best_model': trained_models[best_model_name],
        'all_models': trained_models,
        'feature_columns': feature_cols,
        'results': results
    }
    
    joblib.dump(final_models, 'models/final_phase3_models.pkl')
    
    print("\n" + "="*60)
    print("PHASE 3 COMPLETE!")
    print("="*60)
    print(f"✓ Trained {len(models)} models")
    print(f"✓ Created ensemble with {ensemble_accuracy:.2%} accuracy")
    print("✓ Models saved to: models/final_phase3_models.pkl")

if __name__ == "__main__":
    run_phase3_simple()