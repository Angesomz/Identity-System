import logging
from database.models import AuditLog
from database.connection import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("INSA_AUDIT")

class AuditLogger:
    def log(self, action: str, details: str, user=None):
        logger.info(f"AUDIT [{action}] User: {user} | Details: {details}")
        
    def log_db(self, action: str, ip: str, status: str, identity_id=None, score=None):
        db = SessionLocal()
        try:
            entry = AuditLog(
                action=action,
                request_ip=ip, 
                status=status,
                identity_id=identity_id,
                confidence_score=score
            )
            db.add(entry)
            db.commit()
        finally:
            db.close()
