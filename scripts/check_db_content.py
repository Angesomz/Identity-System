
import sys
import os
from sqlalchemy import create_engine, text

# Ensure project root is in path
sys.path.append(os.getcwd())

from configs.settings import get_settings

def check_db():
    settings = get_settings()
    print(f"Checking Database: {settings.DATABASE_URL}")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            # Check for identities table
            result = conn.execute(text("SELECT count(*) FROM identities"))
            count = result.scalar()
            print(f"Total Identities Found: {count}")
            
            if count > 0:
                rows = conn.execute(text("SELECT id, national_id, full_name FROM identities LIMIT 5"))
                print("Sample Identities:")
                for row in rows:
                    print(row)
            else:
                print("Database is empty.")
                
    except Exception as e:
        print(f"Database check failed: {e}")

if __name__ == "__main__":
    check_db()
