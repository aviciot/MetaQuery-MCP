# Authentication Quick Start

## 🔐 Enable Authentication

The MCP server supports optional API key authentication.

### 1. Generate API Keys

```bash
python generate_api_key.py
```

### 2. Configure in `settings.yaml`

```yaml
server:
  authentication:
    enabled: true  # Change from false to true
    api_keys:
      - name: "claude_desktop"
        key: "YOUR-GENERATED-KEY-HERE"
        description: "Main client"
```

### 3. Configure Claude Desktop

Edit Claude Desktop config:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "performance": {
      "url": "http://localhost:8300/mcp",
      "headers": {
        "Authorization": "Bearer YOUR-GENERATED-KEY-HERE"
      }
    }
  }
}
```

### 4. Restart Services

```bash
# Restart MCP server
docker compose restart

# Restart Claude Desktop
```

## 📖 Full Documentation

See [AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md) for:
- Security best practices
- Multi-client setup
- Troubleshooting
- Error responses
- Production deployment

## 🔓 Default: Authentication Disabled

By default, authentication is **disabled** for ease of local development. Enable it when:
- Exposing server to network/internet
- Multiple users sharing the server
- Compliance requirements
- Need access audit logs
