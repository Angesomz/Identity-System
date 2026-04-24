import redis
from fastapi import Request, HTTPException
from configs.settings import get_settings

settings = get_settings()

# Initialize Redis
try:
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    print(f"Warning: Redis connection failed: {e}. Rate limiting disabled.")
    r = None

async def check_rate_limit(request: Request):
    if not r:
        return
        
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    # Simple fixed window counter
    current = r.get(key)
    
    if current and int(current) > 100: # 100 req/min
        raise HTTPException(status_code=429, detail="Too many requests")
        
    p = r.pipeline()
    p.incr(key)
    p.expire(key, 60) # Reset every minute
    p.execute()
