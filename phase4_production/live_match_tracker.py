# live_match_tracker.py
import websocket
import json
import threading
from datetime import datetime
import redis

class LiveMatchTracker:
    def __init__(self):
        # Redis for real-time data
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # WebSocket connection (example - actual URL depends on data provider)
        self.ws_url = "wss://live.leagueoflegends.com/lck"
        
        self.active_matches = {}
        
    def start_tracking(self):
        """Start tracking live matches"""
        def on_message(ws, message):
            self.process_live_update(json.loads(message))
        
        def on_error(ws, error):
            logging.error(f"WebSocket error: {error}")
        
        def on_close(ws):
            logging.info("WebSocket connection closed")
            # Implement reconnection logic
        
        def on_open(ws):
            logging.info("Connected to live match feed")
            # Subscribe to LCK matches
            ws.send(json.dumps({
                "type": "subscribe",
                "league": "LCK"
            }))
        
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        # Run in separate thread
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
    
    def process_live_update(self, data):
        """Process live match updates"""
        match_id = data.get('match_id')
        event_type = data.get('type')
        
        if event_type == 'draft_start':
            self.handle_draft_start(match_id, data)
        elif event_type == 'champion_pick':
            self.handle_champion_pick(match_id, data)
        elif event_type == 'champion_ban':
            self.handle_champion_ban(match_id, data)
        elif event_type == 'draft_complete':
            self.handle_draft_complete(match_id, data)
        elif event_type == 'match_end':
            self.handle_match_end(match_id, data)
    
    def handle_draft_start(self, match_id, data):
        """Handle draft phase start"""
        self.active_matches[match_id] = {
            'start_time': datetime.now(),
            'blue_team': data.get('blue_team'),
            'red_team': data.get('red_team'),
            'blue_picks': [],
            'red_picks': [],
            'blue_bans': [],
            'red_bans': [],
            'status': 'drafting'
        }
        
        # Store in Redis for API access
        self.redis_client.hset(
            f"live_match:{match_id}",
            mapping=self.active_matches[match_id]
        )
        self.redis_client.expire(f"live_match:{match_id}", 7200)  # 2 hour expiry
    
    def handle_champion_pick(self, match_id, data):
        """Handle champion pick event"""
        if match_id in self.active_matches:
            team = data.get('team')
            champion = data.get('champion')
            position = data.get('position')
            
            if team == 'blue':
                self.active_matches[match_id]['blue_picks'].append({
                    'champion': champion,
                    'position': position
                })
            else:
                self.active_matches[match_id]['red_picks'].append({
                    'champion': champion,
                    'position': position
                })
            
            # Update Redis
            self.update_redis_match(match_id)
            
            # Trigger prediction if enough picks
            self.check_prediction_ready(match_id)
    
    def check_prediction_ready(self, match_id):
        """Check if we have enough picks to make prediction"""
        match = self.active_matches[match_id]
        
        # If both teams have at least 3 picks, we can start predicting
        if len(match['blue_picks']) >= 3 and len(match['red_picks']) >= 3:
            self.generate_live_prediction(match_id)
    
    def generate_live_prediction(self, match_id):
        """Generate prediction for ongoing draft"""
        match = self.active_matches[match_id]
        
        # Prepare data for prediction
        draft_data = {
            'blue_champions': [p['champion'] for p in match['blue_picks']],
            'red_champions': [p['champion'] for p in match['red_picks']],
            'partial_draft': True
        }
        
        # Call prediction API
        response = requests.post(
            'http://localhost:8000/predict_live',
            json=draft_data
        )
        
        if response.status_code == 200:
            prediction = response.json()
            
            # Store prediction in Redis
            self.redis_client.hset(
                f"live_prediction:{match_id}",
                mapping={
                    'blue_win_probability': prediction['blue_win_probability'],
                    'red_win_probability': prediction['red_win_probability'],
                    'timestamp': datetime.now().isoformat()
                }
            )
    
    def handle_draft_complete(self, match_id, data):
        """Handle completed draft"""
        if match_id in self.active_matches:
            self.active_matches[match_id]['status'] = 'in_game'
            self.generate_live_prediction(match_id)
            
            # Log final draft
            self.log_draft_completion(match_id)
    
    def handle_match_end(self, match_id, data):
        """Handle match end"""
        if match_id in self.active_matches:
            winner = data.get('winner')
            
            # Store result
            self.active_matches[match_id]['result'] = winner
            self.active_matches[match_id]['status'] = 'completed'
            
            # Compare prediction with actual result
            self.evaluate_prediction_accuracy(match_id, winner)
            
            # Clean up
            del self.active_matches[match_id]
    
    def update_redis_match(self, match_id):
        """Update match data in Redis"""
        if match_id in self.active_matches:
            # Convert lists to JSON strings for Redis
            match_data = self.active_matches[match_id].copy()
            match_data['blue_picks'] = json.dumps(match_data['blue_picks'])
            match_data['red_picks'] = json.dumps(match_data['red_picks'])
            
            self.redis_client.hset(
                f"live_match:{match_id}",
                mapping=match_data
            )