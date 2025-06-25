#!/usr/bin/env python3
"""
Test script to verify model predictions are working correctly
"""

import requests
import json
import time

def test_model_predictions():
    """Test various match scenarios to see prediction results"""
    
    print("🧪 TESTING LCK MODEL PREDICTIONS")
    print("=" * 50)
    
    # Test scenarios
    test_cases = [
        {
            "name": "T1 vs Gen.G (Balanced Match)",
            "data": {
                "blue_team": "T1",
                "red_team": "Gen.G",
                "blue_top": "Zeus",
                "blue_jng": "Oner", 
                "blue_mid": "Faker",
                "blue_bot": "Gumayusi",
                "blue_sup": "Keria",
                "red_top": "Kiin",
                "red_jng": "Canyon",
                "red_mid": "Chovy", 
                "red_bot": "Peyz",
                "red_sup": "Lehends",
                "blue_champ1": "Aatrox",
                "blue_champ2": "Viego",
                "blue_champ3": "Azir", 
                "blue_champ4": "Jinx",
                "blue_champ5": "Nautilus",
                "red_champ1": "K'Sante",
                "red_champ2": "Graves",
                "red_champ3": "LeBlanc",
                "red_champ4": "Aphelios", 
                "red_champ5": "Thresh"
            }
        },
        {
            "name": "Tank vs Assassin Comp",
            "data": {
                "blue_team": "T1",
                "red_team": "DRX",
                "blue_top": "Zeus",
                "blue_jng": "Oner",
                "blue_mid": "Faker", 
                "blue_bot": "Gumayusi",
                "blue_sup": "Keria",
                "red_top": "Rascal",
                "red_jng": "Pyosik",
                "red_mid": "Zeka",
                "red_bot": "Deft", 
                "red_sup": "BeryL",
                "blue_champ1": "Maokai",
                "blue_champ2": "Sejuani",
                "blue_champ3": "Orianna",
                "blue_champ4": "Jinx",
                "blue_champ5": "Braum",
                "red_champ1": "Camille", 
                "red_champ2": "Lee Sin",
                "red_champ3": "Zed",
                "red_champ4": "Varus",
                "red_champ5": "Thresh"
            }
        },
        {
            "name": "Strong Team vs Weak Team",
            "data": {
                "blue_team": "Gen.G",
                "red_team": "Kwangdong Freecs",
                "blue_top": "Kiin",
                "blue_jng": "Canyon", 
                "blue_mid": "Chovy",
                "blue_bot": "Peyz",
                "blue_sup": "Lehends",
                "red_top": "Canna",
                "red_jng": "Willer",
                "red_mid": "Fisher",
                "red_bot": "Ghost",
                "red_sup": "Effort",
                "blue_champ1": "Jax",
                "blue_champ2": "Graves",
                "blue_champ3": "Azir",
                "blue_champ4": "Aphelios",
                "blue_champ5": "Thresh",
                "red_champ1": "Renekton",
                "red_champ2": "Lee Sin", 
                "red_champ3": "Syndra",
                "red_champ4": "Jhin",
                "red_champ5": "Nautilus"
            }
        }
    ]
    
    base_url = "http://127.0.0.1:5000"
    
    # Check if Flask app is running
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Flask app is not running!")
            print("Please start the app with: python app.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to Flask app!")
        print("Please start the app with: python app.py")
        return
    
    print("✅ Flask app is running\n")
    
    # Test each scenario
    for i, test_case in enumerate(test_cases, 1):
        print(f"🎯 TEST {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Make prediction request
            response = requests.post(
                f"{base_url}/predict",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'error' in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    # Display results
                    blue_prob = result.get('blue_win_probability', 0) * 100
                    red_prob = result.get('red_win_probability', 0) * 100
                    winner = result.get('predicted_winner', 'Unknown')
                    confidence = result.get('confidence', 0) * 100
                    
                    print(f"📊 Results:")
                    print(f"   Blue Team ({test_case['data']['blue_team']}): {blue_prob:.1f}%")
                    print(f"   Red Team ({test_case['data']['red_team']}): {red_prob:.1f}%")
                    print(f"   Predicted Winner: {winner}")
                    print(f"   Confidence: {confidence:.1f}%")
                    
                    # Check if results are realistic
                    if blue_prob > 95 or red_prob > 95:
                        print("⚠️  WARNING: Extreme probabilities detected!")
                        print("   Model may still have feature issues")
                    elif 35 <= blue_prob <= 65 and 35 <= red_prob <= 65:
                        print("✅ Realistic probabilities - Model working correctly!")
                    else:
                        print("🔶 Moderate probabilities - Acceptable range")
                        
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        print()
        time.sleep(1)  # Small delay between tests
    
    # Test debug endpoint
    print("🔍 DEBUG INFO")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/debug", timeout=5)
        if response.status_code == 200:
            debug_info = response.json()
            print(f"Model Loaded: {debug_info.get('model_loaded', False)}")
            print(f"Teams Count: {debug_info.get('teams_count', 0)}")
            print(f"Champions Count: {debug_info.get('champions_count', 0)}")
            print(f"Expected Features: {debug_info.get('expected_features', 0)}")
            print(f"Feature Creator: {debug_info.get('feature_creator_loaded', False)}")
        else:
            print("❌ Could not get debug info")
    except:
        print("❌ Debug endpoint failed")

def manual_test():
    """Allow manual testing with custom input"""
    print("\n🎮 MANUAL TEST MODE")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    # Get available teams and champions
    try:
        teams_response = requests.get(f"{base_url}/teams")
        champions_response = requests.get(f"{base_url}/champions")
        
        if teams_response.status_code == 200 and champions_response.status_code == 200:
            teams = teams_response.json()
            champions = champions_response.json()
            
            print(f"Available Teams ({len(teams)}): {', '.join(teams[:8])}...")
            print(f"Available Champions ({len(champions)}): {', '.join(champions[:10])}...")
            print()
            
            # Simple manual test
            manual_data = {
                "blue_team": teams[0] if teams else "T1",
                "red_team": teams[1] if len(teams) > 1 else "Gen.G",
                "blue_champ1": champions[0] if champions else "Aatrox",
                "blue_champ2": champions[1] if len(champions) > 1 else "Viego", 
                "blue_champ3": champions[2] if len(champions) > 2 else "Azir",
                "blue_champ4": champions[3] if len(champions) > 3 else "Jinx",
                "blue_champ5": champions[4] if len(champions) > 4 else "Nautilus",
                "red_champ1": champions[5] if len(champions) > 5 else "Jax",
                "red_champ2": champions[6] if len(champions) > 6 else "Graves",
                "red_champ3": champions[7] if len(champions) > 7 else "LeBlanc", 
                "red_champ4": champions[8] if len(champions) > 8 else "Aphelios",
                "red_champ5": champions[9] if len(champions) > 9 else "Thresh"
            }
            
            print(f"🧪 Testing with available data:")
            print(f"Blue: {manual_data['blue_team']} - {', '.join([manual_data[f'blue_champ{i}'] for i in range(1, 6)])}")
            print(f"Red: {manual_data['red_team']} - {', '.join([manual_data[f'red_champ{i}'] for i in range(1, 6)])}")
            
            response = requests.post(f"{base_url}/predict", json=manual_data)
            if response.status_code == 200:
                result = response.json()
                if 'error' not in result:
                    blue_prob = result.get('blue_win_probability', 0) * 100
                    red_prob = result.get('red_win_probability', 0) * 100
                    print(f"\n📊 Result: Blue {blue_prob:.1f}% vs Red {red_prob:.1f}%")
                else:
                    print(f"❌ Error: {result['error']}")
            else:
                print(f"❌ Failed: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Manual test failed: {e}")

if __name__ == "__main__":
    print("🚀 LCK MODEL TESTING SUITE\n")
    
    # Run automatic tests
    test_model_predictions()
    
    # Run manual test
    manual_test()
    
    print("\n" + "=" * 50)
    print("✅ TESTING COMPLETE!")
    print("\nExpected Results:")
    print("- Probabilities should be between 35-65% (realistic)")
    print("- No extreme values like 95% vs 5%")
    print("- Confidence levels should be reasonable")
    print("- Model should be loaded successfully")