# performance_monitor.py
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, jsonify
import json

class PerformanceMonitor:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
        self.db_engine = create_engine('sqlite:///data/predictions.db')
        
    def setup_routes(self):
        """Setup Flask routes for monitoring dashboard"""
        
        @self.app.route('/')
        def dashboard():
            return render_template('dashboard.html')
        
        @self.app.route('/api/metrics')
        def get_metrics():
            metrics = self.calculate_current_metrics()
            return jsonify(metrics)
        
        @self.app.route('/api/accuracy_trend')
        def accuracy_trend():
            trend_data = self.get_accuracy_trend()
            return jsonify(trend_data)
        
        @self.app.route('/api/model_performance')
        def model_performance():
            perf_data = self.get_model_performance()
            return jsonify(perf_data)
        
        @self.app.route('/api/feature_importance')
        def feature_importance():
            importance_data = self.get_feature_importance()
            return jsonify(importance_data)
    
    def calculate_current_metrics(self):
        """Calculate current performance metrics"""
        # Get predictions from last 7 days
        query = """
        SELECT 
            p.prediction_id,
            p.blue_win_probability,
            p.predicted_winner,
            p.actual_winner,
            p.confidence,
            p.timestamp,
            p.model_version
        FROM predictions p
        WHERE p.timestamp >= datetime('now', '-7 days')
        """
        
        df = pd.read_sql(query, self.db_engine)
        
        if len(df) == 0:
            return {
                'total_predictions': 0,
                'accuracy': 0,
                'avg_confidence': 0,
                'high_confidence_accuracy': 0
            }
        
        # Calculate metrics
        df['correct'] = df['predicted_winner'] == df['actual_winner']
        
        metrics = {
            'total_predictions': len(df),
            'accuracy': df['correct'].mean(),
            'avg_confidence': df['confidence'].mean(),
            'high_confidence_accuracy': df[df['confidence'] > 0.7]['correct'].mean(),
            'predictions_by_model': df['model_version'].value_counts().to_dict(),
            'recent_predictions': self.get_recent_predictions(df)
        }
        
        return metrics
    
    def get_accuracy_trend(self, days=30):
        """Get accuracy trend over time"""
        query = f"""
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as predictions,
            SUM(CASE WHEN predicted_winner = actual_winner THEN 1 ELSE 0 END) as correct,
            AVG(confidence) as avg_confidence
        FROM predictions
        WHERE timestamp >= datetime('now', '-{days} days')
        GROUP BY DATE(timestamp)
        ORDER BY date
        """
        
        df = pd.read_sql(query, self.db_engine)
        df['accuracy'] = df['correct'] / df['predictions']
        
        return {
            'dates': df['date'].tolist(),
            'accuracy': df['accuracy'].tolist(),
            'volume': df['predictions'].tolist(),
            'confidence': df['avg_confidence'].tolist()
        }
    
    def get_model_performance(self):
        """Compare performance across model versions"""
        query = """
        SELECT 
            model_version,
            COUNT(*) as predictions,
            AVG(CASE WHEN predicted_winner = actual_winner THEN 1.0 ELSE 0.0 END) as accuracy,
            AVG(confidence) as avg_confidence,
            AVG(ABS(blue_win_probability - 0.5)) as avg_certainty
        FROM predictions
        WHERE timestamp >= datetime('now', '-30 days')
        GROUP BY model_version
        """
        
        df = pd.read_sql(query, self.db_engine)
        
        return df.to_dict('records')
    
    def get_feature_importance(self):
        """Get current model feature importance"""
        # Load current model
        import joblib
        model_data = joblib.load('models/final_phase3_models.pkl')
        
        if 'ensemble' in model_data:
            # Get feature importance from best individual model
            best_model = model_data['ensemble'].fitted_models.get('xgboost_optimized')
            if hasattr(best_model, 'feature_importances_'):
                feature_cols = model_data['feature_columns']
                importance = best_model.feature_importances_
                
                # Top 20 features
                importance_df = pd.DataFrame({
                    'feature': feature_cols,
                    'importance': importance
                }).sort_values('importance', ascending=False).head(20)
                
                return importance_df.to_dict('records')
        
        return []
    
    def get_recent_predictions(self, df, limit=10):
        """Get recent prediction details"""
        recent = df.nlargest(limit, 'timestamp')[
            ['blue_win_probability', 'predicted_winner', 'actual_winner', 
             'correct', 'confidence', 'timestamp']
        ]
        
        return recent.to_dict('records')
    
    def log_prediction(self, prediction_data):
        """Log a prediction to database"""
        # Store prediction for monitoring
        pd.DataFrame([prediction_data]).to_sql(
            'predictions', 
            self.db_engine, 
            if_exists='append', 
            index=False
        )
    
    def run_dashboard(self, port=5000):
        """Run the monitoring dashboard"""
        self.app.run(host='0.0.0.0', port=port, debug=False)
