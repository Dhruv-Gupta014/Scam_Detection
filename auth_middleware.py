"""
Authentication and Rate Limiting for API
"""
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta, timezone
from config import API_KEY, RATE_LIMIT_PER_MINUTE
from collections import defaultdict

class RateLimiter:
    """Simple rate limiter using in-memory storage"""
    
    def __init__(self, requests_per_minute: int = RATE_LIMIT_PER_MINUTE):
        self.requests_per_minute = requests_per_minute
        self.request_history = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> tuple[bool, dict]:
        """Check if request is allowed"""
        now = datetime.now(timezone.utc)
        minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        self.request_history[identifier] = [
            req_time for req_time in self.request_history[identifier]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.request_history[identifier]) >= self.requests_per_minute:
            return False, {
                "limit": self.requests_per_minute,
                "current": len(self.request_history[identifier]),
                "reset_in_seconds": 60
            }
        
        # Add current request
        self.request_history[identifier].append(now)
        return True, {
            "limit": self.requests_per_minute,
            "current": len(self.request_history[identifier]),
            "remaining": self.requests_per_minute - len(self.request_history[identifier])
        }

rate_limiter = RateLimiter()

def check_api_key(f):
    """Decorator to check API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            return jsonify({
                "error": "Missing API key",
                "message": "Please provide X-API-Key header",
                "code": "AUTH_MISSING_KEY"
            }), 401
        
        if api_key != API_KEY:
            return jsonify({
                "error": "Invalid API key",
                "message": "The provided API key is invalid",
                "code": "AUTH_INVALID_KEY"
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def check_rate_limit(f):
    """Decorator to check rate limits"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client identifier
        client_id = request.headers.get("X-Client-ID", request.remote_addr)
        
        allowed, limit_info = rate_limiter.is_allowed(client_id)
        
        if not allowed:
            return jsonify({
                "error": "Rate limit exceeded",
                "message": f"You have exceeded the rate limit of {limit_info['limit']} requests per minute",
                "code": "RATE_LIMIT_EXCEEDED",
                "rate_limit": limit_info
            }), 429
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_json_request(f):
    """Decorator to validate JSON request"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                "error": "Invalid content type",
                "message": "Content-Type must be application/json",
                "code": "INVALID_CONTENT_TYPE"
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function
