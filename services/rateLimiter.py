from logging import lastResort
import redis
import logging
# from collections import deque
# from datetime import datetime
import time

#change host to localhost if not running the application itself on docker
pool = redis.ConnectionPool(host='redis', port=6379, db=0)
r = redis.Redis(connection_pool=pool)

logger = logging.getLogger(__name__)

def checkCacheAlive():
    if r.ping():
        logger.info("Redis is running")


def canAllowRequest(tenant: str):
    key = f"rate_limit:{tenant}"
    last_requests = r.lrange(key, 0, -1)
    currtime = time.time()
    while last_requests and currtime - float(last_requests[0]) >= 60:
        r.lpop(key)
        last_requests.pop(0)
    
    if len(last_requests) >= 5:
        return False

    # Record the current request timestamp
    r.rpush(key, currtime)
    r.expire(key, 60)

    return True

        
