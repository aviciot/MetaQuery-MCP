# 🤖 Slack Bot for Performance MCP

Transform your MCP server into a Slack bot that your team can use to monitor database performance!

---

## 🎯 What It Does

The Slack bot allows your team to:
- ✅ Check database health with `/db-health transformer_master`
- ✅ Find slow queries with `/top-queries transformer_master cpu_time 10`
- ✅ Analyze SQL queries with `/analyze-query transformer_master SELECT ...`
- ✅ Chat naturally: `@PerfBot check health of transformer_master`

---

## 📋 Prerequisites

1. **MCP Server running** (already done! ✅)
2. **Slack workspace** with admin access
3. **Python 3.12+** installed
4. **Network access** from Slack to your MCP server

---

## 🚀 Setup Instructions

### **Step 1: Create Slack App**

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name it: `Performance MCP Bot`
4. Select your workspace

### **Step 2: Configure Bot Permissions**

1. In your app settings, go to **OAuth & Permissions**
2. Add these **Bot Token Scopes**:
   ```
   - app_mentions:read (to respond to @mentions)
   - chat:write (to send messages)
   - commands (to handle slash commands)
   ```
3. Click **"Install to Workspace"**
4. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

### **Step 3: Enable Socket Mode**

1. Go to **Settings** → **Socket Mode**
2. Enable Socket Mode
3. Generate an **App-Level Token**
   - Name: `socket_token`
   - Scope: `connections:write`
4. Copy the **App-Level Token** (starts with `xapp-`)

### **Step 4: Create Slash Commands**

Go to **Features** → **Slash Commands**, create these:

#### Command 1: `/db-health`
- **Command**: `/db-health`
- **Request URL**: (leave blank for Socket Mode)
- **Short Description**: Check database health
- **Usage Hint**: `[database_name]`

#### Command 2: `/top-queries`
- **Command**: `/top-queries`
- **Request URL**: (leave blank)
- **Short Description**: Show top queries by metric
- **Usage Hint**: `<database> [metric] [limit]`

#### Command 3: `/analyze-query`
- **Command**: `/analyze-query`
- **Request URL**: (leave blank)
- **Short Description**: Analyze a SQL query
- **Usage Hint**: `<database> <SQL query>`

#### Command 4: `/db-help`
- **Command**: `/db-help`
- **Request URL**: (leave blank)
- **Short Description**: Show available commands

### **Step 5: Enable Event Subscriptions**

1. Go to **Event Subscriptions**
2. Enable Events
3. Subscribe to **Bot Events**:
   ```
   - app_mention (allows @bot mentions)
   ```

### **Step 6: Install Dependencies**

```powershell
cd 'C:\Users\acohen.SHIFT4CORP\Desktop\PythonProjects\MCP Performance\slack_bot'
pip install -r requirements.txt
```

### **Step 7: Configure Environment**

1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` with your values:
   ```env
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   SLACK_APP_TOKEN=xapp-your-app-token-here
   MCP_SERVER_URL=http://localhost:8300
   MCP_API_KEY=your-mcp-api-key-here
   ```

### **Step 8: Run the Bot**

```powershell
cd slack_bot
python slack_bot.py
```

You should see:
```
⚡ Slack bot is running!
```

---

## 💬 Usage Examples

### **1. Check Database Health**
```
/db-health transformer_master
```
**Response:**
```
🏥 Database Health: transformer_master
CPU Usage: 45.2%        Active Sessions: 12
Buffer Cache Hit: 98.5% Memory Used: 256 MB

Top Wait Events:
• db file sequential read: 1,250 waits (450ms)
• log file sync: 890 waits (230ms)
```

### **2. Find Slow Queries**
```
/top-queries transformer_master cpu_time 5
```
**Response:**
```
🔥 Top 5 Queries by CPU_TIME
Database: transformer_master

#1 - SQL_ID: abc123xyz
SELECT * FROM ows.merchant_statement WHERE ready_date > SYSDATE - 30...
• Executions: 15,420
• CPU Time: 345.60s (avg: 22.4ms)
• Elapsed Time: 389.20s
```

### **3. Analyze a Query**
```
/analyze-query transformer_master SELECT * FROM users WHERE created_at > SYSDATE - 7
```
**Response:**
```
🔍 Query Analysis Results
Cost: 125          Cardinality: 1,500
Operation: FULL TABLE SCAN    Object: USERS

Tables:
• OWNER.USERS: 50,000 rows

⚠️ Recommendations:
- Add index on created_at column
- Avoid SELECT * - specify needed columns
```

### **4. Natural Language (Mention Bot)**
```
@PerfBot check health of transformer_master
```
**Response:**
```
✅ Health check for transformer_master completed. Use /db-health transformer_master for detailed view.
```

---

## 🔧 Advanced Configuration

### **Deploy as Windows Service**

1. Install NSSM (Non-Sucking Service Manager):
   ```powershell
   choco install nssm
   ```

2. Create service:
   ```powershell
   nssm install SlackPerfBot "C:\Python312\python.exe" "C:\...\slack_bot\slack_bot.py"
   nssm set SlackPerfBot AppDirectory "C:\...\slack_bot"
   nssm start SlackPerfBot
   ```

### **Docker Deployment**

Create `slack_bot/Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY slack_bot.py .
COPY .env .

CMD ["python", "slack_bot.py"]
```

Run:
```powershell
docker build -t slack-perf-bot ./slack_bot
docker run -d --name slack-bot --env-file slack_bot/.env slack-perf-bot
```

### **Add More Commands**

Edit `slack_bot.py` and add new command handlers:

```python
@app.command("/performance-trends")
def handle_trends(ack, command, respond):
    ack()
    db_name = command['text'].strip()
    
    # Call MCP tool
    result = mcp.call_tool(
        "get_performance_trends",
        db_name=db_name,
        metric="cpu_usage",
        hours=24
    )
    
    # Format and respond
    respond(f"📈 Performance trends for {db_name}...")
```

---

## 🛡️ Security Considerations

### **1. Network Security**
- If MCP server is not public, run bot on same network
- Use VPN or SSH tunnel for external access
- Consider firewall rules to restrict access

### **2. Slack Permissions**
- Use Socket Mode (no public webhook URLs)
- Restrict bot to specific channels
- Use Slack's built-in access controls

### **3. API Key Rotation**
- Regularly rotate MCP API keys
- Store secrets in environment variables, never in code
- Use different keys for production/development

### **4. Query Restrictions**
- Bot only has READ access (Level 2 safeguards)
- Cannot modify data or execute DML/DDL
- Query analysis doesn't execute queries, only explains them

---

## 🐛 Troubleshooting

### **Bot not responding to commands**
```powershell
# Check bot is running
# Check logs for errors
# Verify tokens in .env are correct
# Test MCP server directly: curl http://localhost:8300/healthz
```

### **"MCP Error: 401 Unauthorized"**
```
# Verify MCP_API_KEY matches settings.yaml
# Check authentication is enabled in settings.yaml
# Restart MCP server: docker compose restart
```

### **"Connection timeout"**
```
# Check MCP_SERVER_URL is correct
# Verify MCP server is running: docker compose ps
# Test connectivity: curl http://localhost:8300/healthz
```

---

## 📊 Monitoring & Logging

The bot logs all activity. Check logs:
```powershell
# If running directly
python slack_bot.py 2>&1 | Tee-Object -FilePath bot.log

# If running as Docker
docker logs slack-bot --tail=100 -f
```

---

## 🎓 Next Steps

1. ✅ **Test in a private channel first**
2. ✅ **Add more commands** based on team needs
3. ✅ **Set up alerts** (e.g., notify when CPU > 80%)
4. ✅ **Create dashboards** using historical data
5. ✅ **Integrate with LLM** for natural language queries

---

## 🤝 Integration with Claude (Advanced)

Want natural language? Integrate Claude API:

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")

@app.event("app_mention")
def handle_mention(event, say):
    user_message = event['text']
    
    # Send to Claude with MCP context
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": user_message}],
        # Add MCP server details
    )
    
    say(response.content[0].text)
```

This gives you full natural language + MCP power in Slack! 🚀

---

## 📞 Support

- **MCP Server Issues**: Check `docker compose logs`
- **Slack Bot Issues**: Check bot logs
- **API Questions**: See `server/prompts/analysis_prompts.py` for available prompts
