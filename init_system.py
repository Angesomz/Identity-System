import sys
import os

# Add the current directory to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.migrations.init_db import init_db

if __name__ == "__main__":
    print("Initializing INSA Identity System...")
    try:
        init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
