# ensemble_model.py
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
import joblib

class EnsembleVotingSystem(BaseEstimator, ClassifierMixin):
    def __init__(self, models=None, weights=None):
        """
        models: dict of {'name': model}
        weights: dict of {'name': weight} or None for equal weights
        """
        self.models = models or {}
        self.weights = weights
        self.fitted_models = {}
        
    def fit(self, X, y):
        """Fit all models"""
        for name, model in self.models.items():
            print(f"Training {name}...")
            if hasattr(model, 'fit'):
                model.fit(X, y)
            self.fitted_models[name] = model
        return self
    
    def predict_proba(self, X):
        """Get weighted average predictions"""
        predictions = []
        weights = []
        
        for name, model in self.fitted_models.items():
            if hasattr(model, 'predict_proba'):
                pred = model.predict_proba(X)[:, 1]
            elif hasattr(model, 'predict'):
                # For models that only have predict (like LightGBM)
                pred = model.predict(X)
            else:
                continue
                
            predictions.append(pred)
            
            # Get weight
            if self.weights and name in self.weights:
                weights.append(self.weights[name])
            else:
                weights.append(1.0)
        
        # Weighted average
        predictions = np.array(predictions)
        weights = np.array(weights) / np.sum(weights)
        
        weighted_pred = np.average(predictions, axis=0, weights=weights)
        
        # Return as 2D array for sklearn compatibility
        return np.vstack([1 - weighted_pred, weighted_pred]).T
    
    def predict(self, X):
        """Get binary predictions"""
        proba = self.predict_proba(X)[:, 1]
        return (proba > 0.5).astype(int)
    
    def get_individual_predictions(self, X):
        """Get predictions from each model separately"""
        individual_preds = {}
        
        for name, model in self.fitted_models.items():
            if hasattr(model, 'predict_proba'):
                individual_preds[name] = model.predict_proba(X)[:, 1]
            elif hasattr(model, 'predict'):
                individual_preds[name] = model.predict(X)
                
        return individual_preds
