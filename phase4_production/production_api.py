# production_api.py
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
import redis
import asyncio
from datetime import datetime

app = FastAPI(title="LCK Draft Predictor Pro", version="2.0.0")

# Security
api_key_header = APIKeyHeader(name="X-API-Key")
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Initialize systems
feedback_system = FeedbackSystem(db_engine)
performance_monitor = PerformanceMonitor()

class PredictionRequest(BaseModel):
    blue_champions: List[str]
    red_champions: List[str]
    blue_team: Optional[str] = None
    red_team: Optional[str] = None
    blue_players: Optional[List[str]] = None
    red_players: Optional[List[str]] = None
    match_id: Optional[str] = None

class PredictionResponse(BaseModel):
    prediction_id: str
    blue_win_probability: float
    red_win_probability: float
    confidence: float
    key_factors: List[str]
    model_version: str
    timestamp: datetime
    live_updates_available: bool

class FeedbackRequest(BaseModel):
    prediction_id: str
    rating: int  # 1-5
    comments: Optional[str] = None
    actual_winner: Optional[str] = None

def verify_api_key(api_key: str = Depends(api_key_header)):
    """Verify API key for production use"""
    valid_keys = load_valid_api_keys()  # Load from secure storage
    if api_key not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.post("/predict", response_model=PredictionResponse)
async def predict_match(
    draft: PredictionRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Enhanced prediction endpoint with monitoring"""
    
    # Generate prediction ID
    prediction_id = str(uuid.uuid4())
    
    # Load latest model
    model_data = load_latest_model()
    
    # Create features
    features = create_advanced_features(draft)
    
    # Make prediction
    prediction = model_data['ensemble'].predict_proba(features)
    blue_win_prob = prediction[0][1]
    
    # Calculate confidence and factors
    confidence = abs(blue_win_prob - 0.5) * 2
    key_factors = extract_key_factors(features, model_data)
    
    # Check if live updates available
    live_updates = False
    if draft.match_id:
        live_updates = redis_client.exists(f"live_match:{draft.match_id}")
    
    # Log prediction for monitoring
    background_tasks.add_task(
        log_prediction,
        {
            'prediction_id': prediction_id,
            'blue_team': draft.blue_team,
            'red_team': draft.red_team,
            'blue_win_probability': blue_win_prob,
            'predicted_winner': 'blue' if blue_win_prob > 0.5 else 'red',
            'confidence': confidence,
            'model_version': model_data['version'],
            'timestamp': datetime.now(),
            'api_key': api_key[:8] + '...'  # Log partial key
        }
    )
    
    return PredictionResponse(
        prediction_id=prediction_id,
        blue_win_probability=blue_win_prob,
        red_win_probability=1 - blue_win_prob,
        confidence=confidence,
        key_factors=key_factors[:5],
        model_version=model_data['version'],
        timestamp=datetime.now(),
        live_updates_available=live_updates
    )

@app.get("/live/{match_id}")
async def get_live_match(match_id: str):
    """Get live match data and predictions"""
    
    # Check Redis for live data
    match_data = redis_client.hgetall(f"live_match:{match_id}")
    if not match_data:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Get latest prediction
    prediction_data = redis_client.hgetall(f"live_prediction:{match_id}")
    
    # Parse data
    match_data['blue_picks'] = json.loads(match_data.get('blue_picks', '[]'))
    match_data['red_picks'] = json.loads(match_data.get('red_picks', '[]'))
    
    return {
        'match_id': match_id,
        'status': match_data.get('status'),
        'blue_team': match_data.get('blue_team'),
        'red_team': match_data.get('red_team'),
        'current_draft': {
            'blue_picks': match_data['blue_picks'],
            'red_picks': match_data['red_picks']
        },
        'current_prediction': {
            'blue_win_probability': float(prediction_data.get('blue_win_probability', 0.5)),
            'red_win_probability': float(prediction_data.get('red_win_probability', 0.5)),
            'last_updated': prediction_data.get('timestamp')
        }
    }

@app.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Submit feedback on predictions"""
    
    # Get user ID from API key
    user_id = get_user_id_from_api_key(api_key)
    
    # Collect feedback
    feedback_id = feedback_system.collect_feedback(
        feedback.prediction_id,
        user_id,
        feedback.rating,
        feedback.comments
    )
    
    # If actual winner provided, check accuracy
    if feedback.actual_winner:
        background_tasks.add_task(
            update_prediction_result,
            feedback.prediction_id,
            feedback.actual_winner
        )
    
    # Trigger analysis if needed
    background_tasks.add_task(analyze_feedback_patterns)
    
    return {
        'feedback_id': feedback_id,
        'status': 'received',
        'message': 'Thank you for your feedback'
    }

@app.get("/performance/dashboard")
async def performance_dashboard():
    """Get performance metrics for dashboard"""
    metrics = performance_monitor.calculate_current_metrics()
    return metrics

@app.get("/performance/accuracy-trend")
async def accuracy_trend(days: int = 30):
    """Get accuracy trend over time"""
    trend = performance_monitor.get_accuracy_trend(days)
    return trend

@app.get("/health")
async def health_check():
    """Enhanced health check"""
    
    # Check model status
    try:
        model_data = load_latest_model()
        model_status = "healthy"
        model_version = model_data['version']
    except:
        model_status = "error"
        model_version = "unknown"
    
    # Check Redis connection
    try:
        redis_client.ping()
        redis_status = "healthy"
    except:
        redis_status = "error"
    
    # Check database connection
    try:
        pd.read_sql("SELECT 1", db_engine)
        db_status = "healthy"
    except:
        db_status = "error"
    
    return {
        'status': 'healthy' if all([model_status == 'healthy', 
                                   redis_status == 'healthy',
                                   db_status == 'healthy']) else 'degraded',
        'components': {
            'model': {'status': model_status, 'version': model_version},
            'redis': {'status': redis_status},
            'database': {'status': db_status}
        },
        'timestamp': datetime.now()
    }

# Background task functions
async def log_prediction(prediction_data):
    """Log prediction to database"""
    performance_monitor.log_prediction(prediction_data)

async def update_prediction_result(prediction_id, actual_winner):
    """Update prediction with actual result"""
    query = f"""
    UPDATE predictions 
    SET actual_winner = '{actual_winner}'
    WHERE prediction_id = '{prediction_id}'
    """
    with db_engine.connect() as conn:
        conn.execute(query)

async def analyze_feedback_patterns():
    """Analyze feedback patterns periodically"""
    insights = feedback_system.analyze_feedback()
    if insights and insights['avg_rating'] < 3.5:
        feedback_system.trigger_model_improvement(insights)