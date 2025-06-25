# feedback_system.py
from flask import request
import uuid
from datetime import datetime

class FeedbackSystem:
    def __init__(self, db_engine):
        self.db_engine = db_engine
        self.create_feedback_tables()
        
    def create_feedback_tables(self):
        """Create feedback storage tables"""
        create_feedback_sql = """
        CREATE TABLE IF NOT EXISTS user_feedback (
            feedback_id TEXT PRIMARY KEY,
            prediction_id TEXT,
            user_id TEXT,
            rating INTEGER,
            accuracy_feedback TEXT,
            comments TEXT,
            timestamp DATETIME,
            processed BOOLEAN DEFAULT FALSE
        )
        """
        
        create_corrections_sql = """
        CREATE TABLE IF NOT EXISTS prediction_corrections (
            correction_id TEXT PRIMARY KEY,
            prediction_id TEXT,
            corrected_winner TEXT,
            correction_reason TEXT,
            user_id TEXT,
            timestamp DATETIME,
            verified BOOLEAN DEFAULT FALSE
        )
        """
        
        with self.db_engine.connect() as conn:
            conn.execute(create_feedback_sql)
            conn.execute(create_corrections_sql)
    
    def collect_feedback(self, prediction_id, user_id, rating, comments=None):
        """Collect user feedback on prediction"""
        feedback_data = {
            'feedback_id': str(uuid.uuid4()),
            'prediction_id': prediction_id,
            'user_id': user_id,
            'rating': rating,  # 1-5 stars
            'comments': comments,
            'timestamp': datetime.now()
        }
        
        pd.DataFrame([feedback_data]).to_sql(
            'user_feedback',
            self.db_engine,
            if_exists='append',
            index=False
        )
        
        # Check if feedback indicates issue
        if rating <= 2:
            self.flag_for_review(prediction_id, feedback_data)
        
        return feedback_data['feedback_id']
    
    def report_incorrect_prediction(self, prediction_id, user_id, actual_winner, reason):
        """Report an incorrect prediction"""
        correction_data = {
            'correction_id': str(uuid.uuid4()),
            'prediction_id': prediction_id,
            'corrected_winner': actual_winner,
            'correction_reason': reason,
            'user_id': user_id,
            'timestamp': datetime.now()
        }
        
        pd.DataFrame([correction_data]).to_sql(
            'prediction_corrections',
            self.db_engine,
            if_exists='append',
            index=False
        )
        
        return correction_data['correction_id']
    
    def analyze_feedback(self):
        """Analyze collected feedback for insights"""
        # Get recent feedback
        feedback_query = """
        SELECT 
            f.*,
            p.blue_team,
            p.red_team,
            p.predicted_winner,
            p.actual_winner
        FROM user_feedback f
        JOIN predictions p ON f.prediction_id = p.prediction_id
        WHERE f.processed = FALSE
        """
        
        feedback_df = pd.read_sql(feedback_query, self.db_engine)
        
        if len(feedback_df) == 0:
            return None
        
        # Analyze patterns
        insights = {
            'avg_rating': feedback_df['rating'].mean(),
            'low_rating_predictions': feedback_df[feedback_df['rating'] <= 2],
            'common_issues': self.extract_common_issues(feedback_df),
            'accuracy_by_rating': self.analyze_accuracy_by_rating(feedback_df)
        }
        
        # Mark as processed
        feedback_df['processed'] = True
        feedback_df[['feedback_id', 'processed']].to_sql(
            'user_feedback',
            self.db_engine,
            if_exists='replace',
            index=False
        )
        
        return insights
    
    def extract_common_issues(self, feedback_df):
        """Extract common issues from comments"""
        # Simple keyword analysis
        issues = {
            'champion_synergy': 0,
            'player_skill': 0,
            'recent_form': 0,
            'patch_changes': 0
        }
        
        if 'comments' in feedback_df.columns:
            comments = ' '.join(feedback_df['comments'].dropna().str.lower())
            
            for issue, keywords in {
                'champion_synergy': ['synergy', 'comp', 'composition', 'combo'],
                'player_skill': ['player', 'skill', 'performance', 'roster'],
                'recent_form': ['form', 'recent', 'streak', 'momentum'],
                'patch_changes': ['patch', 'nerf', 'buff', 'meta']
            }.items():
                issues[issue] = sum(comments.count(keyword) for keyword in keywords)
        
        return issues
    
    def trigger_model_improvement(self, insights):
        """Trigger model improvements based on feedback"""
        if insights['avg_rating'] < 3.5:
            logging.warning("Low average rating detected. Model review needed.")
            
            # Identify specific areas for improvement
            common_issues = insights['common_issues']
            top_issue = max(common_issues, key=common_issues.get)
            
            if top_issue == 'champion_synergy':
                # Retrain synergy calculations
                os.system("python update_champion_synergies.py")
            elif top_issue == 'player_skill':
                # Update player ratings
                os.system("python update_player_stats.py")
            elif top_issue == 'patch_changes':
                # Force patch data update
                os.system("python update_patch_data.py")