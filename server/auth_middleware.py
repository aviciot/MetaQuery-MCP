"""
Authentication Middleware for MCP Server

Provides API key-based authentication via Authorization header.
Format: Authorization: Bearer <api_key>

When authentication is enabled in settings.yaml:
- All MCP endpoints require valid API key
- Health/info endpoints remain public
- Invalid/missing keys return 401 Unauthorized
"""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    API Key Authentication Middleware
    
    Validates Bearer tokens against configured API keys in settings.yaml.
    Public endpoints (health checks) are exempt from authentication.
    """
    
    def __init__(self, app, config):
        super().__init__(app)
        self.config = config
        self.public_paths = [
            "/healthz",
            "/version",
            "/_info",
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication if disabled
        if not self.config.auth_enabled:
            return await call_next(request)
        
        # Allow public endpoints
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # Check Authorization header
        auth_header = request.headers.get("Authorization", "")
        
        if not auth_header:
            logger.warning(f"Missing Authorization header from {request.client.host}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Authentication required",
                    "message": "Missing Authorization header. Format: Authorization: Bearer <api_key>"
                }
            )
        
        # Extract Bearer token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning(f"Invalid Authorization format from {request.client.host}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Invalid authentication format",
                    "message": "Expected format: Authorization: Bearer <api_key>"
                }
            )
        
        api_key = parts[1]
        
        # Validate API key
        if api_key not in self.config.api_keys:
            logger.warning(f"Invalid API key from {request.client.host}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Invalid API key",
                    "message": "The provided API key is not valid"
                }
            )
        
        # Log successful authentication
        client_name = self.config.api_keys[api_key]
        logger.info(f"Authenticated request from: {client_name} ({request.client.host})")
        
        # Add client name to request state for potential logging
        request.state.client_name = client_name
        
        return await call_next(request)
