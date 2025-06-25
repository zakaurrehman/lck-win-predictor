# hyperparameter_tuning.py
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
import numpy as np

class HyperparameterOptimizer:
    def __init__(self):
        self.best_params = {}
        
    def optimize_xgboost(self, X_train, y_train):
        """Optimize XGBoost hyperparameters"""
        print("Optimizing XGBoost hyperparameters...")
        
        param_distributions = {
            'max_depth': [4, 6, 8, 10, 12],
            'learning_rate': [0.01, 0.03, 0.05, 0.1],
            'n_estimators': [300, 500, 700, 1000],
            'subsample': [0.7, 0.8, 0.9],
            'colsample_bytree': [0.7, 0.8, 0.9],
            'gamma': [0, 0.1, 0.2, 0.3],
            'reg_alpha': [0, 0.1, 0.5, 1],
            'reg_lambda': [0.5, 1, 1.5, 2]
        }
        
        xgb_model = xgb.XGBClassifier(
            objective='binary:logistic',
            random_state=42,
            n_jobs=-1
        )
        
        random_search = RandomizedSearchCV(
            xgb_model,
            param_distributions,
            n_iter=50,
            scoring='roc_auc',
            cv=5,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        random_search.fit(X_train, y_train)
        
        self.best_params['xgboost'] = random_search.best_params_
        print(f"Best XGBoost params: {random_search.best_params_}")
        print(f"Best CV AUC: {random_search.best_score_:.4f}")
        
        return random_search.best_estimator_
    
    def optimize_lightgbm(self, X_train, y_train):
        """Optimize LightGBM hyperparameters"""
        print("\nOptimizing LightGBM hyperparameters...")
        
        param_distributions = {
            'num_leaves': [20, 31, 40, 50],
            'learning_rate': [0.01, 0.03, 0.05, 0.1],
            'n_estimators': [300, 500, 700, 1000],
            'feature_fraction': [0.7, 0.8, 0.9],
            'bagging_fraction': [0.7, 0.8, 0.9],
            'bagging_freq': [3, 5, 7],
            'min_child_samples': [10, 20, 30]
        }
        
        lgb_model = lgb.LGBMClassifier(
            objective='binary',
            random_state=42,
            n_jobs=-1,
            verbosity=-1
        )
        
        random_search = RandomizedSearchCV(
            lgb_model,
            param_distributions,
            n_iter=50,
            scoring='roc_auc',
            cv=5,
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        random_search.fit(X_train, y_train)
        
        self.best_params['lightgbm'] = random_search.best_params_
        print(f"Best LightGBM params: {random_search.best_params_}")
        print(f"Best CV AUC: {random_search.best_score_:.4f}")
        
        return random_search.best_estimator_