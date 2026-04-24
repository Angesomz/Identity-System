import time
import uuid
import random
from locust import HttpUser, task, between

class IdentityUser(HttpUser):
    wait_time = between(1, 2.5)

    def on_start(self):
        """Authenticate and get token."""
        # Mock authentication to get a token
        # In a real scenario, this would call an auth endpoint
        self.token = "mock_token" 
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def search_identity(self):
        """Simulate frequent search requests."""
        payload = {
            "image_base64": "base64_encoded_dummy_image_data...",
            "top_k": 5
        }
        with self.client.post("/search/identify", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Search failed with status {response.status_code}")

    @task(1)
    def enroll_identity(self):
        """Simulate occasional enrollment."""
        payload = {
            "national_id": str(uuid.uuid4()),
            "full_name": f"Citizen {random.randint(1000, 9999)}",
            "image_base64": "base64_encoded_dummy_image_data..."
        }
        self.client.post("/enroll", json=payload, headers=self.headers)

# To run: locust -f load_test.py --host=http://localhost:8000
