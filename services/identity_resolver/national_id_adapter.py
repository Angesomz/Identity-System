class NationalIDAdapter:
    """
    Interface for communicating with external National ID systems.
    """
    def fetch_details(self, national_id: str) -> dict:
        # Mock external system call
        # In production this would be a secure SOAP/REST call
        print(f"Fetching details for National ID: {national_id}")
        return {
            "national_id": national_id,
            "status": "VALID",
            "citizen_data": {
                "dob": "1990-01-01",
                "region": "Addis Ababa"
            }
        }
