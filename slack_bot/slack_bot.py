"""
Slack Bot for Performance MCP
Allows Slack users to query database performance via slash commands
"""
import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import json

# ============================================================================
# CONFIGURATION
# ============================================================================
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8300")
MCP_API_KEY = os.environ.get("MCP_API_KEY")

# Initialize Slack app
app = App(token=SLACK_BOT_TOKEN)

# ============================================================================
# MCP CLIENT HELPER
# ============================================================================
class MCPClient:
    """Client to interact with MCP server"""
    
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def call_tool(self, tool_name, **params):
        """Call an MCP tool"""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        response = requests.post(
            f"{self.base_url}/mcp",
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"MCP Error: {response.status_code} - {response.text}")
    
    def get_database_health(self, db_name):
        """Get database health metrics"""
        return self.call_tool("get_database_health", db_name=db_name)
    
    def get_top_queries(self, db_name, metric="cpu_time", limit=10):
        """Get top queries by metric"""
        return self.call_tool(
            "get_top_queries",
            db_name=db_name,
            metric=metric,
            limit=limit
        )
    
    def analyze_query(self, db_name, sql_text):
        """Analyze a SQL query"""
        return self.call_tool(
            "analyze_full_sql_context",
            db_name=db_name,
            sql_text=sql_text
        )

# Initialize MCP client
mcp = MCPClient(MCP_SERVER_URL, MCP_API_KEY)

# ============================================================================
# SLACK COMMANDS
# ============================================================================

@app.command("/db-health")
def handle_db_health(ack, command, respond):
    """
    Slack command: /db-health transformer_master
    Shows database health metrics
    """
    ack()
    
    try:
        db_name = command['text'].strip() or "transformer_master"
        
        respond(f"⏳ Checking health for `{db_name}`...")
        
        result = mcp.get_database_health(db_name)
        data = result['result']['content'][0]['text']
        health_data = json.loads(data)
        
        # Format response
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🏥 Database Health: {db_name}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*CPU Usage:*\n{health_data.get('cpu_usage', 'N/A')}%"},
                    {"type": "mrkdwn", "text": f"*Active Sessions:*\n{health_data.get('active_sessions', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Buffer Cache Hit:*\n{health_data.get('buffer_cache_hit_ratio', 'N/A')}%"},
                    {"type": "mrkdwn", "text": f"*Memory Used:*\n{health_data.get('memory_used_mb', 'N/A')} MB"}
                ]
            }
        ]
        
        # Add wait events if available
        if 'top_wait_events' in health_data and health_data['top_wait_events']:
            wait_text = "\n".join([
                f"• {event['event']}: {event['waits']} waits ({event['time_ms']}ms)"
                for event in health_data['top_wait_events'][:3]
            ])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Top Wait Events:*\n{wait_text}"
                }
            })
        
        respond(blocks=blocks)
        
    except Exception as e:
        respond(f"❌ Error: {str(e)}")


@app.command("/top-queries")
def handle_top_queries(ack, command, respond):
    """
    Slack command: /top-queries transformer_master cpu_time 5
    Shows top N queries by metric
    """
    ack()
    
    try:
        parts = command['text'].strip().split()
        db_name = parts[0] if len(parts) > 0 else "transformer_master"
        metric = parts[1] if len(parts) > 1 else "cpu_time"
        limit = int(parts[2]) if len(parts) > 2 else 5
        
        respond(f"⏳ Fetching top {limit} queries by {metric} from `{db_name}`...")
        
        result = mcp.get_top_queries(db_name, metric, limit)
        data = result['result']['content'][0]['text']
        queries_data = json.loads(data)
        
        # Format response
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔥 Top {limit} Queries by {metric.upper()}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"Database: *{db_name}*"}
                ]
            }
        ]
        
        # Add each query
        for idx, query in enumerate(queries_data.get('queries', [])[:limit], 1):
            sql_preview = query.get('sql_text', '')[:100] + "..." if len(query.get('sql_text', '')) > 100 else query.get('sql_text', '')
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*#{idx} - SQL_ID: `{query.get('sql_id', 'N/A')}`*\n"
                           f"```{sql_preview}```\n"
                           f"• Executions: {query.get('executions', 0):,}\n"
                           f"• CPU Time: {query.get('cpu_time_total_sec', 0):.2f}s (avg: {query.get('cpu_time_per_exec_ms', 0):.2f}ms)\n"
                           f"• Elapsed Time: {query.get('elapsed_time_total_sec', 0):.2f}s"
                }
            })
            blocks.append({"type": "divider"})
        
        respond(blocks=blocks)
        
    except Exception as e:
        respond(f"❌ Error: {str(e)}")


@app.command("/analyze-query")
def handle_analyze_query(ack, command, respond):
    """
    Slack command: /analyze-query transformer_master SELECT * FROM ...
    Analyzes a SQL query and provides recommendations
    """
    ack()
    
    try:
        text = command['text'].strip()
        parts = text.split(maxsplit=1)
        
        if len(parts) < 2:
            respond("❌ Usage: `/analyze-query <database> <SQL query>`")
            return
        
        db_name = parts[0]
        sql_text = parts[1]
        
        respond(f"⏳ Analyzing query on `{db_name}`...\n```{sql_text[:200]}```")
        
        result = mcp.analyze_query(db_name, sql_text)
        data = result['result']['content'][0]['text']
        analysis = json.loads(data)
        
        # Format response
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔍 Query Analysis Results"
                }
            }
        ]
        
        # Show execution plan summary
        if 'facts' in analysis and 'plan_details' in analysis['facts']:
            plan = analysis['facts']['plan_details'][0] if analysis['facts']['plan_details'] else {}
            blocks.append({
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Cost:*\n{plan.get('cost', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Cardinality:*\n{plan.get('cardinality', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Operation:*\n{plan.get('operation', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*Object:*\n{plan.get('object_name', 'N/A')}"}
                ]
            })
        
        # Show table stats
        if 'facts' in analysis and 'table_stats' in analysis['facts']:
            tables = analysis['facts']['table_stats']
            if tables:
                table_info = "\n".join([
                    f"• {t['owner']}.{t['table_name']}: {t.get('num_rows', 'N/A'):,} rows"
                    for t in tables[:3]
                ])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Tables:*\n{table_info}"
                    }
                })
        
        respond(blocks=blocks)
        
    except Exception as e:
        respond(f"❌ Error: {str(e)}")


@app.command("/db-help")
def handle_help(ack, respond):
    """Show available commands"""
    ack()
    
    help_text = """
*🤖 Performance MCP Bot - Available Commands*

*Health Monitoring:*
• `/db-health <database>` - Check database health metrics
  Example: `/db-health transformer_master`

*Query Analysis:*
• `/top-queries <database> [metric] [limit]` - Show top queries
  Example: `/top-queries transformer_master cpu_time 10`
  Metrics: `cpu_time`, `elapsed_time`, `executions`

• `/analyze-query <database> <SQL>` - Analyze a SQL query
  Example: `/analyze-query transformer_master SELECT * FROM users WHERE id = 1`

*Available Databases:*
• `transformer_master` (Oracle - Performance monitoring enabled)
• `way4_docker7` (Oracle)
• `way4_docker8` (Oracle)
• `mysql_devdb03_avi` (MySQL)

*Tips:*
• All commands work in channels and DMs
• Results are only visible to you (ephemeral)
• For detailed analysis, use the full MCP server via Claude Desktop
"""
    
    respond(help_text)


# ============================================================================
# APP MENTIONS (Chat with bot)
# ============================================================================

@app.event("app_mention")
def handle_mention(event, say):
    """
    Handle @bot mentions for natural language queries
    Example: @PerfBot check health of transformer_master
    """
    text = event['text'].lower()
    
    if 'health' in text:
        # Extract database name
        words = text.split()
        db_name = "transformer_master"
        for i, word in enumerate(words):
            if word in ['of', 'for', 'on'] and i + 1 < len(words):
                db_name = words[i + 1]
                break
        
        try:
            result = mcp.get_database_health(db_name)
            say(f"✅ Health check for `{db_name}` completed. Use `/db-health {db_name}` for detailed view.")
        except Exception as e:
            say(f"❌ Error: {str(e)}")
    
    elif 'slow' in text or 'top' in text:
        say("Use `/top-queries <database>` to see slow queries!")
    
    else:
        say("👋 Hi! I'm the Performance MCP bot. Use `/db-help` to see what I can do!")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Start the bot
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    print("⚡ Slack bot is running!")
    handler.start()
