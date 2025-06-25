# advanced_model_trainer.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import xgboost as xgb
import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
import joblib
import warnings
warnings.filterwarnings('ignore')

class AdvancedModelTrainer:
    def __init__(self, features_path="data/enhanced/advanced_features.csv"):
        self.features_df = pd.read_csv(features_path)
        self.models = {}
        self.results = {}
        self.scaler = StandardScaler()
        
    def prepare_data(self):
        """Prepare data for training"""
        # Remove non-feature columns
        feature_cols = [col for col in self.features_df.columns 
                       if col not in ['gameid', 'blue_win']]
        
        X = self.features_df[feature_cols]
        y = self.features_df['blue_win']
        
        # Handle any missing values
        X = X.fillna(0)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features for some models
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled, feature_cols
    
    def train_all_models(self):
        """Train multiple model types"""
        print("Training multiple models...")
        
        X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled, feature_cols = self.prepare_data()
        
        # 1. XGBoost
        print("\n1. Training XGBoost...")
        self.models['xgboost'] = self.train_xgboost(X_train, y_train, X_test, y_test)
        
        # 2. LightGBM
        print("\n2. Training LightGBM...")
        self.models['lightgbm'] = self.train_lightgbm(X_train, y_train, X_test, y_test)
        
        # 3. Random Forest (improved)
        print("\n3. Training Random Forest...")
        self.models['random_forest'] = self.train_random_forest(X_train, y_train, X_test, y_test)
        
        # 4. Gradient Boosting
        print("\n4. Training Gradient Boosting...")
        self.models['gradient_boosting'] = self.train_gradient_boosting(X_train, y_train, X_test, y_test)
        
        # 5. Logistic Regression (baseline)
        print("\n5. Training Logistic Regression...")
        self.models['logistic_regression'] = self.train_logistic_regression(
            X_train_scaled, y_train, X_test_scaled, y_test
        )
        
        # Compare results
        self.compare_models(X_test, X_test_scaled, y_test)
        
        # Save best model
        self.save_best_model(feature_cols)
    
    def train_xgboost(self, X_train, y_train, X_test, y_test):
        """Train XGBoost model with optimized parameters"""
        params = {
            'objective': 'binary:logistic',
            'max_depth': 8,
            'learning_rate': 0.03,
            'n_estimators': 500,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'gamma': 0.1,
            'reg_alpha': 0.1,
            'reg_lambda': 1,
            'random_state': 42,
            'n_jobs': -1,
            'eval_metric': 'logloss'
        }
        
        model = xgb.XGBClassifier(**params)
        
        # Train with early stopping
        eval_set = [(X_test, y_test)]
        model.fit(X_train, y_train, eval_set=eval_set, verbose=False)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        
        self.results['xgboost'] = {'accuracy': accuracy, 'auc': auc}
        print(f"  XGBoost - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
        
        return model
    
    def train_lightgbm(self, X_train, y_train, X_test, y_test):
        """Train LightGBM model"""
        params = {
            'objective': 'binary',
            'metric': 'binary_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': 42
        }
        
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        model = lgb.train(
            params,
            train_data,
            valid_sets=[valid_data],
            num_boost_round=500,
            callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)]
        )
        
        # Evaluate
        y_pred = (model.predict(X_test) > 0.5).astype(int)
        y_proba = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        
        self.results['lightgbm'] = {'accuracy': accuracy, 'auc': auc}
        print(f"  LightGBM - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
        
        return model
    
    def train_random_forest(self, X_train, y_train, X_test, y_test):
        """Train improved Random Forest"""
        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=15,
            min_samples_split=20,
            min_samples_leaf=10,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        
        self.results['random_forest'] = {'accuracy': accuracy, 'auc': auc}
        print(f"  Random Forest - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
        
        return model
    
    def train_gradient_boosting(self, X_train, y_train, X_test, y_test):
        """Train Gradient Boosting model"""
        model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=6,
            min_samples_split=20,
            min_samples_leaf=10,
            subsample=0.8,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        
        self.results['gradient_boosting'] = {'accuracy': accuracy, 'auc': auc}
        print(f"  Gradient Boosting - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
        
        return model
    
    def train_logistic_regression(self, X_train, y_train, X_test, y_test):
        """Train Logistic Regression as baseline"""
        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='lbfgs'
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        
        self.results['logistic_regression'] = {'accuracy': accuracy, 'auc': auc}
        print(f"  Logistic Regression - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")
        
        return model
    
    def compare_models(self, X_test, X_test_scaled, y_test):
        """Compare all models"""
        print("\n" + "="*50)
        print("MODEL COMPARISON")
        print("="*50)
        
        comparison_df = pd.DataFrame(self.results).T
        comparison_df = comparison_df.sort_values('auc', ascending=False)
        
        print(comparison_df.round(4))
        
        print(f"\nBest model: {comparison_df.index[0]}")
        print(f"Best AUC: {comparison_df.iloc[0]['auc']:.4f}")
        print(f"Best Accuracy: {comparison_df.iloc[0]['accuracy']:.4f}")
    
    def save_best_model(self, feature_cols):
        """Save the best performing model"""
        # Find best model by AUC
        best_model_name = max(self.results.items(), key=lambda x: x[1]['auc'])[0]
        best_model = self.models[best_model_name]
        
        # Save model and metadata
        model_data = {
            'model': best_model,
            'model_type': best_model_name,
            'feature_columns': feature_cols,
            'scaler': self.scaler if best_model_name == 'logistic_regression' else None,
            'results': self.results
        }
        
        joblib.dump(model_data, 'models/best_model_phase3.pkl')
        print(f"\n✓ Saved best model ({best_model_name}) to models/best_model_phase3.pkl")
