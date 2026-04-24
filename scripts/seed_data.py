import sys
import os
import numpy as np
import faiss

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import SessionLocal
from database.migrations.init_db import init_db
from database.models import UserIdentity
from vector_cluster.shard_router import ShardRouter
from configs.settings import get_settings

def seed_and_verify():
    print("🚀 Starting System Verification & Seeding...")
    settings = get_settings()
    
    # 1. Initialize DB
    print("🔹 Initializing Database...")
    init_db()
    
    db = SessionLocal()
    router = ShardRouter()
    
    try:
        # 2. Check if test user exists
        test_national_id = "TEST_USER_001"
        existing = db.query(UserIdentity).filter_by(national_id=test_national_id).first()
        
        if existing:
            print(f"🔹 Test user {test_national_id} already exists. Skipping creation.")
            user_id = existing.id
        else:
            print(f"🔹 Creating test user {test_national_id}...")
            new_user = UserIdentity(
                national_id=test_national_id,
                full_name="Test Citizen",
                is_active=True
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user_id = new_user.id
            print(f"✅ User created with ID: {user_id}")

        # 3. Generate and Add Vector
        print("🔹 Generating test vector...")
        # specific random seed for reproducibility
        np.random.seed(42) 
        vector = np.random.rand(512).astype(np.float32)
        faiss.normalize_L2(vector.reshape(1, -1))
        
        print(f"🔹 Adding vector to Shard Router for User ID {user_id}...")
        router.route_add(vector, user_id)
        
        # 4. Verify Search (The "Match Not Found" fix)
        print("🔹 Verifying search functionality...")
        # Search with the EXACT same vector
        results = router.distribute_search(vector, k=5)
        
        print(f"🔍 Search Results: {results}")
        
        match_found = False
        for uid, score in results:
            if uid == user_id:
                print(f"✅ MATCH CONFIRMED! User {uid} found with score {score:.4f}")
                match_found = True
                break
        
        if not match_found:
            print("❌ MATCH FAILED: Test user not found in top k results.")
            print("Troubleshooting: Check FAISS index persistence and thresholds.")
        else:
            print("✨ System Verification PASSED. The 'match not found' issue should be resolved locally.")

    except Exception as e:
        print(f"❌ Error during seeding/verification: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_and_verify()
