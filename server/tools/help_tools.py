# server/tools/help_tools.py
"""
Interactive help tool for Performance MCP Server
Allows LLM to query specific help topics when connected to multiple MCPs
"""

from mcp_app import mcp
from config import config


@mcp.tool(
    name="get_mcp_help",
    description=(
        "📚 Get help for Performance MCP Server (SQL query performance analysis).\n\n"
        "This MCP specializes in analyzing Oracle/MySQL query performance WITHOUT execution.\n"
        "Use this tool when you need guidance on available capabilities or how to optimize queries.\n\n"
        "**Available Topics:**\n"
        "• `overview` - Server purpose and capabilities\n"
        "• `tools` - All available tools with usage examples\n"
        "• `oracle` - Oracle-specific workflows\n"
        "• `mysql` - MySQL-specific workflows\n"
        "• `monitoring` - Real-time performance monitoring\n"
        "• `troubleshooting` - Common errors and solutions\n"
        "• `examples` - Step-by-step usage scenarios\n\n"
        "**When to use this MCP:** Query optimization, execution plan analysis, performance troubleshooting"
    ),
)
def get_mcp_help(topic: str = "overview"):
    """
    Interactive help system for Performance MCP capabilities
    
    Args:
        topic: Help topic (overview, tools, oracle, mysql, monitoring, troubleshooting, examples)
    
    Returns:
        Help content for specified topic
    """
    
    help_topics = {
        "overview": {
            "mcp_name": "Performance MCP Server",
            "unique_purpose": "SQL query performance analysis without execution",
            "differentiator": "Specializes in EXPLAIN plans + metadata collection (not data retrieval)",
            
            "what_this_mcp_does": [
                "Generates execution plans (EXPLAIN PLAN) without running queries",
                "Collects table/index statistics from data dictionary",
                "Detects performance anti-patterns (full scans, Cartesian products)",
                "Maps business logic via foreign key relationships + comments",
                "Compares query plans before/after optimization",
                "Monitors real-time database performance (CPU, sessions, waits)"
            ],
            
            "what_this_mcp_does_NOT": [
                "Does NOT execute queries or return data rows",
                "Does NOT modify database schema or data (READ-ONLY)",
                "Does NOT perform ETL or data transformation",
                "Does NOT manage database users or permissions"
            ],
            
            "supported_databases": ["Oracle 11g-21c", "MySQL 5.7-8.0+"],
            "security_model": "READ-ONLY: SELECT queries only, no DML/DDL/DCL",
            
            "when_to_use": [
                "User asks about slow query performance",
                "User needs query optimization suggestions",
                "User wants to understand query logic/relationships",
                "User needs to verify optimization improvements"
            ],
            
            "total_tools_available": len(mcp.tools),
            "next_steps": "Call get_mcp_help(topic='tools') for tool details"
        },
        
        "tools": {
            "oracle_analysis_tools": {
                "analyze_oracle_query": {
                    "purpose": "Main Oracle query performance analysis",
                    "inputs": "db_name (from settings.yaml), sql_text (SELECT query)",
                    "outputs": "Execution plan, table/index stats, full table scans, Cartesian products, query intent",
                    "use_when": "User has slow Oracle query or needs optimization",
                    "example": "analyze_oracle_query(db_name='prod_erp', sql_text='SELECT * FROM orders o JOIN customers c ON o.cust_id=c.id WHERE o.order_date > SYSDATE-30')"
                },
                "compare_oracle_query_plans": {
                    "purpose": "Compare execution plans before/after optimization",
                    "inputs": "db_name, original_sql, optimized_sql",
                    "outputs": "Cost comparison, operation differences, performance delta",
                    "use_when": "User made query changes and wants to verify improvement"
                },
                "explain_oracle_query_logic": {
                    "purpose": "Understand business logic and data relationships",
                    "inputs": "db_name, sql_text",
                    "outputs": "Mermaid ER diagram, FK relationships, table/column comments, primary keys",
                    "use_when": "User needs to understand what legacy query does"
                },
                "get_table_business_context": {
                    "purpose": "Deep dive into specific table structure and relationships",
                    "inputs": "db_name, owner (schema), table_name",
                    "outputs": "Columns, data types, comments, constraints, FKs, indexes",
                    "use_when": "User needs detailed table documentation"
                }
            },
            
            "mysql_analysis_tools": {
                "analyze_mysql_query": {
                    "purpose": "Main MySQL query performance analysis",
                    "inputs": "db_name, sql_text",
                    "outputs": "EXPLAIN FORMAT=JSON, table stats, index usage",
                    "use_when": "User has slow MySQL query"
                },
                "compare_mysql_query_plans": {
                    "purpose": "Compare MySQL query plans",
                    "inputs": "db_name, original_sql, optimized_sql",
                    "outputs": "Plan comparison and cost differences"
                }
            },
            
            "monitoring_tools": {
                "get_oracle_real_time_performance": {
                    "purpose": "Current Oracle database performance metrics",
                    "inputs": "db_name, include_top_sql (optional)",
                    "outputs": "CPU usage, active sessions, buffer cache hit ratio, top SQL",
                    "use_when": "User wants current database health status"
                },
                "get_oracle_historical_stats": {
                    "purpose": "Historical Oracle performance trends",
                    "inputs": "db_name, hours_back",
                    "outputs": "Time-series metrics for trend analysis",
                    "use_when": "User needs to identify performance patterns over time"
                },
                "analyze_oracle_session_activity": {
                    "purpose": "Current active Oracle sessions and their queries",
                    "inputs": "db_name",
                    "outputs": "Active sessions, wait events, blocking sessions",
                    "use_when": "User investigating long-running or blocked queries"
                },
                "check_database_health": {
                    "purpose": "Overall database health check",
                    "inputs": "db_name",
                    "outputs": "Health score, issues detected, recommendations",
                    "use_when": "User needs pre-deployment check or routine audit"
                }
            },
            
            "most_common_tool": "analyze_oracle_query (used in ~70% of cases)",
            "typical_sequence": "analyze → review issues → suggest fix → compare plans"
        },
        
        "oracle": {
            "typical_workflow": [
                "1. User provides slow Oracle query",
                "2. Call analyze_oracle_query(db_name='prod', sql_text='...')",
                "3. Review facts['execution_plan'] for expensive operations",
                "4. Check facts['full_table_scans'] for missing indexes",
                "5. Check facts['cartesian_detections'] for missing join conditions",
                "6. Suggest: CREATE INDEX or query rewrite",
                "7. Call compare_oracle_query_plans to verify improvement"
            ],
            
            "key_facts_to_check": {
                "execution_plan": "Visual operation tree with costs (most important)",
                "full_table_scans": "Tables scanned without indexes (factual detection)",
                "cartesian_detections": "Missing or ineffective join conditions",
                "query_intent": "Detected pattern (aggregation, pagination, etc)",
                "table_stats": "Row counts and last analyzed dates",
                "index_stats": "Available indexes for optimization"
            },
            
            "output_preset_impact": {
                "current_preset": config.output_preset,
                "standard": "Full data (15K-40K tokens) - best for deep analysis",
                "compact": "Plan objects only (6K-18K tokens) - routine work",
                "minimal": "Essentials only (1.5K-4.5K tokens) - large queries",
                "recommendation": "Use compact for most cases, standard for index tuning projects"
            },
            
            "common_issues": {
                "full_table_scan_on_large_table": "Suggest index on WHERE clause columns",
                "cartesian_product": "Missing join condition between tables",
                "high_cost_operation": "Consider query rewrite or better indexes",
                "stale_statistics": "Table not analyzed recently, suggest DBMS_STATS"
            }
        },
        
        "mysql": {
            "typical_workflow": [
                "1. Call analyze_mysql_query(db_name='prod', sql_text='...')",
                "2. Review EXPLAIN FORMAT=JSON output",
                "3. Check for table scans (type='ALL')",
                "4. Check for filesort or temporary tables",
                "5. Suggest index or query optimization",
                "6. Use compare_mysql_query_plans to verify"
            ],
            
            "mysql_specific_patterns": {
                "type_ALL": "Full table scan - needs index",
                "Using_filesort": "ORDER BY not using index - consider composite index",
                "Using_temporary": "Complex GROUP BY - may need query rewrite",
                "Using_index": "Good! Covering index used"
            }
        },
        
        "monitoring": {
            "real_time_monitoring": "Use get_oracle_real_time_performance for current state",
            "historical_analysis": "Use get_oracle_historical_stats for trends",
            "session_investigation": "Use analyze_oracle_session_activity for blocking",
            
            "when_to_monitor": [
                "User reports 'database is slow'",
                "Before/after deployment comparison",
                "Capacity planning and trending",
                "Investigating production incidents"
            ],
            
            "key_metrics": {
                "cpu_usage_pct": "Above 80% indicates resource constraint",
                "active_sessions": "High spike may indicate blocking",
                "buffer_cache_hit_ratio": "Below 90% suggests memory tuning needed",
                "top_sql": "Identify most expensive queries"
            }
        },
        
        "troubleshooting": {
            "permission_errors": {
                "symptom": "ORA-00942: table or view does not exist",
                "cause": "Missing Oracle dictionary grants",
                "fix": "GRANT SELECT ON SYS.ALL_TABLES TO user; (see README.md for full list)"
            },
            "connection_refused": {
                "symptom": "Cannot connect to database",
                "fix": "Check settings.yaml credentials, use host.docker.internal for Docker"
            },
            "query_rejected": {
                "symptom": "Query rejected: Not a SELECT query",
                "cause": "Tool only accepts SELECT (security restriction)",
                "fix": "For DML, analyze the SELECT portion separately"
            },
            "token_limit_exceeded": {
                "symptom": "Response too large for LLM context",
                "fix": f"Change output_preset to 'compact' or 'minimal' (current: {config.output_preset})"
            },
            "stale_cache": {
                "symptom": "Analysis shows old table statistics",
                "fix": "Cache expires after 24 hours, restart container to force refresh"
            }
        },
        
        "examples": {
            "example_1_slow_query": {
                "scenario": "User: 'This query takes 5 minutes, why?'",
                "steps": [
                    "1. get_mcp_help(topic='tools') → Confirm analyze_oracle_query available",
                    "2. analyze_oracle_query(db_name='prod', sql_text=<user_query>)",
                    "3. Review facts['execution_plan'] → Find high-cost operations",
                    "4. Check facts['full_table_scans'] → Identify tables missing indexes",
                    "5. Explain: 'Query scans ORDERS table (5M rows) without index on ORDER_DATE'",
                    "6. Suggest: 'CREATE INDEX idx_orders_date ON orders(order_date)'",
                    "7. compare_oracle_query_plans with hint: /*+ INDEX(...) */"
                ]
            },
            
            "example_2_legacy_query": {
                "scenario": "User: 'What does this 500-line query do?'",
                "steps": [
                    "1. explain_oracle_query_logic(db_name='prod', sql_text=<query>)",
                    "2. Present Mermaid ER diagram showing table relationships",
                    "3. Explain: 'Query joins ORDERS→CUSTOMERS→ADDRESSES via FKs'",
                    "4. Use table/column comments to describe business purpose",
                    "5. Summarize: 'This appears to be a customer order history report'"
                ]
            },
            
            "example_3_verify_optimization": {
                "scenario": "User: 'I added an index, did it help?'",
                "steps": [
                    "1. compare_oracle_query_plans(original_sql=<before>, optimized_sql=<after>)",
                    "2. Show cost reduction: 'Cost decreased 8234 → 125 (98% improvement)'",
                    "3. Highlight: 'Changed TABLE ACCESS FULL → INDEX RANGE SCAN'",
                    "4. Confirm: 'Yes, optimization is effective'"
                ]
            }
        }
    }
    
    topic_lower = topic.lower()
    
    if topic_lower == "all":
        return {
            "all_help_topics": help_topics,
            "available_topics": list(help_topics.keys()),
            "usage": "Call get_mcp_help(topic='<name>') for focused help"
        }
    
    if topic_lower in help_topics:
        return {
            "mcp_identity": "Performance MCP - SQL Query Optimization Specialist",
            "topic": topic,
            "help_content": help_topics[topic_lower],
            "related_topics": [t for t in help_topics.keys() if t != topic_lower]
        }
    
    return {
        "error": f"Unknown help topic: {topic}",
        "available_topics": list(help_topics.keys()),
        "suggestion": "Call get_mcp_help(topic='overview') for general help",
        "mcp_purpose": "This MCP specializes in SQL query performance analysis"
    }
