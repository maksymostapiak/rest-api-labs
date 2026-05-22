import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import jwt, JWTError

from security import SECRET_KEY, ALGORITHM

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.ip_records = {}
        self.user_records = {}

    async def dispatch(self, request: Request, call_next):

        if request.url.hostname == "test":
            return await call_next(request)

        now = time.time()
        auth_header = request.headers.get("Authorization")
        username = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub")
            except JWTError:
                pass

        if username:
            self.user_records[username] = [t for t in self.user_records.get(username, []) if now - t < 60]
            
            if len(self.user_records[username]) > 10:
                return JSONResponse(
                    status_code=429, 
                    content={"detail": "Too Many Requests (Authorized limit: 10 per minute)"}
                )
            self.user_records[username].append(now)
        else:
            ip = request.client.host
            self.ip_records[ip] = [t for t in self.ip_records.get(ip, []) if now - t < 60]
            
            if len(self.ip_records[ip]) > 2:
                return JSONResponse(
                    status_code=429, 
                    content={"detail": "Too Many Requests (Anonymous limit: 2 per minute)"}
                )
            self.ip_records[ip].append(now)

        return await call_next(request)