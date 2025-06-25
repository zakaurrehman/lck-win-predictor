#!/usr/bin/env python3
"""
LCK Match Prediction App - Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all required files and dependencies exist"""
    print("🔍 Checking project requirements...")
    
    # Check if we're in the right directory
    required_dirs = ['data', 'models', 'templates']
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    
    # Check for model file
    model_file = 'models/final_phase3_models.pkl'
    if not os.path.exists(model_file):
        print(f"❌ Model file not found: {model_file}")
        return False
    
    # Check for key data files
    required_files = [
        'data/team_recent_form.csv',
        'data/player_stats.csv',
        'data/lck_full_dataset.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠️  Missing data files: {', '.join(missing_files)}")
        print("App will use default values for missing data.")
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ app.py not found!")
        return False
    
    # Check if templates/index.html exists
    if not os.path.exists('templates/index.html'):
        print("❌ templates/index.html not found!")
        return False
    
    print("✅ All required files found!")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    try:
        # Try to install requirements
        if os.path.exists('requirements.txt'):
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        else:
            # Install individual packages
            packages = [
                'Flask==2.3.3',
                'pandas==2.0.3',
                'numpy==1.24.3',
                'scikit-learn==1.3.0'
            ]
            for package in packages:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_templates_dir():
    """Create templates directory and index.html if missing"""
    if not os.path.exists('templates'):
        os.makedirs('templates')
        print("📁 Created templates directory")
    
    if not os.path.exists('templates/index.html'):
        print("⚠️  templates/index.html missing. Please copy the HTML template file.")
        return False
    
    return True

def start_app():
    """Start the Flask application"""
    print("🚀 Starting LCK Match Prediction App...")
    print("📊 Model Accuracy: 79.88%")
    print("🌐 Server will start at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    try:
        # Import and run the Flask app
        import app
        app.app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Failed to import app.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to start app: {e}")
        return False

def main():
    """Main function to run the startup process"""
    print("=" * 50)
    print("🏆 LCK MATCH PREDICTION APP")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py') and not os.path.exists('models'):
        print("❌ Please run this script from the project root directory")
        print("   (The directory containing app.py and the models folder)")
        return
    
    # Step 1: Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix the issues above.")
        return
    
    # Step 2: Create templates directory if needed
    if not create_templates_dir():
        print("\n❌ Templates setup failed.")
        return
    
    # Step 3: Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed.")
        return
    
    # Step 4: Start the app
    print("\n" + "=" * 50)
    start_app()

if __name__ == "__main__":
    main()