from fastapi import HTTPException

class PermissionGuard:
    """
    Enforces granular access control for identity data.
    """
    def check_access(self, user_role: str, action: str):
        allowed_actions = {
            "admin": ["ENROLL", "SEARCH", "DELETE", "VIEW_AUDIT"],
            "operator": ["ENROLL", "SEARCH"],
            "viewer": ["SEARCH"]
        }
        
        if action not in allowed_actions.get(user_role, []):
             raise HTTPException(status_code=403, detail="Insufficient permissions")
        return True
