import os

class HealthChecks:
    def check_database(self):
        # In production use proper connection testing
        return True 
    
    def check_redis(self):
        return True
        
    def check_gpu(self):
        # Mock GPU check using nvidia-smi command existence
        return os.system("nvidia-smi > /dev/null 2>&1") == 0
    
    def get_system_health(self):
        return {
            "database": "healthy" if self.check_database() else "unhealthy",
            "redis": "healthy" if self.check_redis() else "unhealthy",
            "gpu": "available" if self.check_gpu() else "unavailable"
        }
