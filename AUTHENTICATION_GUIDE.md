# MCP Server Authentication Guide

## Overview

The MCP server supports **optional API key authentication** via Bearer tokens in the Authorization header. When enabled, all MCP endpoints require a valid API key, while health check endpoints remain public.

## Configuration

### 1. Enable Authentication

Edit `server/config/settings.yaml`:

```yaml
server:
  name: performance_mcp
  
  authentication:
    enabled: true  # Set to false to disable authentication
    api_keys:
      - name: "claude_desktop"
        key: "your-secure-api-key-here"
        description: "Claude Desktop client"
      
      - name: "development"
        key: "dev-api-key-12345"
        description: "Development and testing"
```

### 2. Generate Secure API Keys

Use the provided utility script:

```bash
# Generate 1 key
python generate_api_key.py

# Generate multiple keys
python generate_api_key.py --count 5
```

Example output:
```
🔐 Generated 1 secure API key(s):

--------------------------------------------------------------------------------

1. dQw4w9WgXcQ-7yD4KJ3oP2lM8nB6vC5xZ1aS3fG4hJ7k

   Add to settings.yaml:
   authentication:
     enabled: true
     api_keys:
       - name: 'client_1'
         key: 'dQw4w9WgXcQ-7yD4KJ3oP2lM8nB6vC5xZ1aS3fG4hJ7k'
         description: 'Description here'
```

## Client Configuration

### Claude Desktop

Edit your Claude Desktop config file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "performance": {
      "url": "http://localhost:8300/mcp",
      "headers": {
        "Authorization": "Bearer your-secure-api-key-here"
      }
    }
  }
}
```

### MCP Inspector

When testing with MCP Inspector, add the Authorization header:

```bash
# In MCP Inspector settings
Authorization: Bearer your-secure-api-key-here
```

### HTTP Clients (curl, httpx, requests)

```bash
# curl
curl -H "Authorization: Bearer your-api-key" http://localhost:8300/mcp

# Python httpx
import httpx
headers = {"Authorization": "Bearer your-api-key"}
response = httpx.post("http://localhost:8300/mcp", headers=headers, json=...)

# Python requests
import requests
headers = {"Authorization": "Bearer your-api-key"}
response = requests.post("http://localhost:8300/mcp", headers=headers, json=...)
```

## Public Endpoints

The following endpoints remain **public** (no authentication required):

- `/healthz` - Health check
- `/version` - Server version info
- `/_info` - Basic server info

All other endpoints require authentication when enabled.

## Authentication Flow

1. **Client sends request** with `Authorization: Bearer <api_key>` header
2. **Middleware validates** API key against configured keys in settings.yaml
3. **If valid**: Request proceeds to MCP handler
4. **If invalid/missing**: Returns `401 Unauthorized` with error message

## Error Responses

### Missing Authorization Header

```json
{
  "error": "Authentication required",
  "message": "Missing Authorization header. Format: Authorization: Bearer <api_key>"
}
```

### Invalid Format

```json
{
  "error": "Invalid authentication format",
  "message": "Expected format: Authorization: Bearer <api_key>"
}
```

### Invalid API Key

```json
{
  "error": "Invalid API key",
  "message": "The provided API key is not valid"
}
```

## Logging

When authentication is enabled, the server logs:

```
🔐 Authentication ENABLED - 2 API key(s) configured
Authenticated request from: claude_desktop (172.17.0.1)
```

When disabled:

```
🔓 Authentication DISABLED - Server is open to all clients
```

## Security Best Practices

### 1. Generate Strong Keys

Always use the `generate_api_key.py` script or equivalent:

```python
import secrets
api_key = secrets.token_urlsafe(32)  # 256 bits of entropy
```

❌ **Never use**:
- Weak keys like "password123"
- Dictionary words
- Predictable patterns

### 2. Rotate Keys Regularly

- Change API keys every 90 days
- Immediately rotate if compromised
- Keep old keys for brief transition period

### 3. Use Different Keys Per Client

```yaml
api_keys:
  - name: "claude_desktop_laptop"
    key: "key-1-here"
  - name: "claude_desktop_desktop"
    key: "key-2-here"
  - name: "ci_cd_pipeline"
    key: "key-3-here"
```

This allows you to:
- Track which client made which request
- Revoke specific clients without affecting others
- Audit access patterns

### 4. Environment Variables (Production)

Don't commit API keys to git. Use environment variables:

```yaml
authentication:
  enabled: true
  api_keys:
    - name: "production_client"
      key: "${PROD_API_KEY}"  # Set in environment
```

Then:
```bash
export PROD_API_KEY="your-secret-key-here"
docker compose up
```

### 5. HTTPS in Production

Authentication over HTTP is vulnerable to interception. Use HTTPS:

```bash
# Behind reverse proxy (recommended)
nginx → https → clients
nginx → http → mcp server (localhost only)

# Or use TLS directly
uvicorn server:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

## Disabling Authentication

For local development or trusted networks, you can disable authentication:

```yaml
authentication:
  enabled: false  # No authentication required
```

Server will log:
```
🔓 Authentication DISABLED - Server is open to all clients
```

## Troubleshooting

### "Authentication required" but I disabled it

1. Restart the Docker container: `docker compose restart`
2. Check settings.yaml: `authentication.enabled: false`
3. Check logs: Should see "🔓 Authentication DISABLED"

### API key not working

1. Verify exact match (case-sensitive, no extra spaces)
2. Check settings.yaml has your key in the `api_keys` list
3. Ensure format: `Authorization: Bearer <key>` (note the space after Bearer)
4. Restart container after changing settings.yaml

### Claude Desktop not connecting

1. Ensure config file syntax is valid JSON
2. Check the `Authorization` header is in `headers` object
3. Verify API key matches settings.yaml
4. Restart Claude Desktop after config changes

## Performance Impact

Authentication middleware adds negligible overhead:
- **Header parsing**: < 1ms
- **Key validation**: O(1) dictionary lookup
- **Logging**: Async, non-blocking

No impact on MCP tool execution time.

## Example: Multi-Client Setup

```yaml
# settings.yaml
authentication:
  enabled: true
  api_keys:
    # Production clients
    - name: "claude_desktop_prod"
      key: "prod-key-abc123..."
      description: "Production Claude Desktop"
    
    # Development
    - name: "local_dev"
      key: "dev-key-xyz789..."
      description: "Local development testing"
    
    # CI/CD
    - name: "github_actions"
      key: "ci-key-def456..."
      description: "GitHub Actions integration tests"
    
    # Team members
    - name: "alice_laptop"
      key: "alice-key-ghi789..."
      description: "Alice's development machine"
    
    - name: "bob_desktop"
      key: "bob-key-jkl012..."
      description: "Bob's desktop workstation"
```

Each client uses their own key. Logs show which client made each request.

## Migration Path

### Phase 1: Add Authentication (Optional)

Enable with permissive keys for testing:

```yaml
authentication:
  enabled: true
  api_keys:
    - name: "everyone"
      key: "temporary-shared-key"
```

### Phase 2: Distribute Individual Keys

Generate unique keys for each client:

```bash
python generate_api_key.py --count 5
```

Update each client's config with their key.

### Phase 3: Remove Shared Key

Once all clients are migrated:

```yaml
authentication:
  enabled: true
  api_keys:
    - name: "client_1"
      key: "unique-key-1"
    - name: "client_2"
      key: "unique-key-2"
    # removed: shared key
```

## Summary

✅ **Optional** - Disabled by default, enable when needed  
✅ **Simple** - Bearer token in Authorization header  
✅ **Secure** - 256-bit cryptographically random keys  
✅ **Flexible** - Multiple keys, per-client tracking  
✅ **Fast** - Negligible performance impact  
✅ **Compatible** - Works with Claude Desktop, MCP Inspector, any HTTP client  

For most use cases, authentication can remain disabled. Enable it when:
- Server is exposed to internet
- Multiple users share the server
- Compliance requires access control
- You need audit logs of who accessed what
