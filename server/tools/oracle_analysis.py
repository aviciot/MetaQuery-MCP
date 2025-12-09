# server/tools/oracle_analysis.py

import logging
import traceback
import json
from mcp_app import mcp
from db_connector import oracle_connector
from tools.oracle_collector_impl import run_full_oracle_analysis as run_collector
from tools.plan_visualizer import build_visual_plan, get_plan_summary
from history_tracker import normalize_and_hash, store_history, get_recent_history, compare_with_history
from config import config


logger = logging.getLogger("oracle_analysis")
# Set log level from config
log_level = getattr(logging, config.log_level, logging.INFO)
logger.setLevel(log_level)

@mcp.tool(
    name="analyze_full_sql_context",
    description=(
        "🔍 Analyzes Oracle SQL SELECT queries for performance optimization.\n\n"
        "⚠️ SECURITY RESTRICTIONS - This tool ONLY accepts:\n"
        "✅ SELECT queries (including WITH clauses/CTEs)\n"
        "✅ Read-only operations for analysis\n\n"
        "❌ BLOCKED OPERATIONS (will be rejected immediately):\n"
        "❌ Data modification: INSERT, UPDATE, DELETE, MERGE\n"
        "❌ Schema changes: CREATE, DROP, ALTER, TRUNCATE, RENAME\n"
        "❌ Permissions: GRANT, REVOKE\n"
        "❌ Transactions: COMMIT, ROLLBACK, SAVEPOINT\n"
        "❌ System ops: SHUTDOWN, STARTUP, EXECUTE, CALL\n"
        "❌ PL/SQL blocks: BEGIN, DECLARE\n"
        "❌ SELECT INTO (data insertion)\n\n"
        "📊 Returns: Execution plan, table/index stats, performance recommendations.\n\n"
        "⚡ Usage: Only call this tool with valid SELECT queries that you want to optimize."
    ),
)
def analyze_full_sql_context(db_name: str, sql_text: str):
    """
    MCP tool entrypoint.
    Opens DB connection and calls the real collector.
    """
    # Log tool invocation details if enabled
    if config.show_tool_calls:
        logger.info("=" * 80)
        logger.info("🔧 TOOL CALLED BY LLM: analyze_full_sql_context")
        logger.info(f"   📊 Database: {db_name}")
        logger.info(f"   📝 SQL Length: {len(sql_text)} characters")
        if logger.isEnabledFor(logging.DEBUG):
            # Only show full SQL in DEBUG mode
            logger.debug(f"   💬 Full SQL:\n{sql_text}")
        else:
            # Show truncated version in INFO
            sql_preview = sql_text[:200] + "..." if len(sql_text) > 200 else sql_text
            logger.info(f"   💬 SQL Preview: {sql_preview}")
        logger.info("=" * 80)
    else:
        logger.info(f"🔍 analyze_full_sql_context(db={db_name}) called")

    if not sql_text or not sql_text.strip():
        return {"error": "sql_text is empty", "facts": {}, "prompt": ""}

    try:
        # Open DB connection
        conn = oracle_connector.connect(db_name)
        cur = conn.cursor()

        logger.info("📡 Connected to Oracle, collecting performance metadata…")

        # PRE-VALIDATE SQL before expensive metadata collection
        logger.info("🔍 Validating SQL query (safety + syntax)...")
        
        # Import validation function
        from tools.oracle_collector_impl import validate_sql
        
        is_valid, error_msg, is_dangerous = validate_sql(cur, sql_text)
        
        if is_dangerous:
            logger.error(f"🚨 DANGEROUS OPERATION BLOCKED: {error_msg}")
            logger.error("   This query was blocked for SECURITY reasons")
            return {
                "error": f"SECURITY BLOCK: {error_msg}",
                "facts": {},
                "prompt": (
                    f"🚨 SECURITY: This query was BLOCKED for safety reasons.\n\n"
                    f"Reason: {error_msg}\n\n"
                    f"This tool only allows SELECT queries for analysis.\n"
                    f"The following operations are PROHIBITED:\n"
                    f"- Data modification (INSERT, UPDATE, DELETE, MERGE)\n"
                    f"- Schema changes (CREATE, DROP, ALTER, TRUNCATE)\n"
                    f"- Permission changes (GRANT, REVOKE)\n"
                    f"- System operations (SHUTDOWN, STARTUP)\n"
                    f"- Procedure execution (EXECUTE, CALL)\n"
                    f"- PL/SQL blocks (BEGIN, DECLARE)\n\n"
                    f"Please provide a SELECT query only."
                )
            }
        
        if not is_valid:
            logger.error(f"❌ SQL VALIDATION FAILED: {error_msg}")
            logger.error("   Cannot analyze invalid SQL - returning error to user")
            return {
                "error": f"Invalid SQL query: {error_msg}",
                "facts": {},
                "prompt": (
                    f"The SQL query is INVALID and cannot be analyzed.\n\n"
                    f"Error: {error_msg}\n\n"
                    f"Suggestions:\n"
                    f"1. Check that all table and column names are spelled correctly\n"
                    f"2. Verify table aliases match the table names\n"
                    f"3. Ensure all referenced columns exist in the tables\n"
                    f"4. Test the query in SQL*Plus or another SQL client first\n\n"
                    f"You can use this query to find correct column names:\n"
                    f"SELECT column_name FROM all_tab_columns WHERE owner='SCHEMA' AND table_name='TABLE';"
                )
            }
        
        logger.info("✅ SQL query is valid and safe")

        # Check historical executions
        fingerprint = normalize_and_hash(sql_text)
        history = get_recent_history(fingerprint, db_name)

        # Call real collector
        result = run_collector(cur, sql_text)
        
        facts = result.get("facts", {})
        plan_details = facts.get("plan_details", [])
        
        logger.info(f"📋 Collector returned {len(plan_details)} plan steps")
        if not plan_details:
            logger.warning("⚠️  EXPLAIN PLAN returned no steps - check if query is valid")

        # Add visual plan
        if plan_details:
            facts["visual_plan"] = build_visual_plan(plan_details)
            facts["plan_summary"] = get_plan_summary(plan_details)
        
        # Add historical context
        if history:
            facts["historical_context"] = compare_with_history(history, facts)
            logger.info(f"📊 Historical context: {facts['historical_context'].get('message', 'N/A')}")
        
        # Store current execution in history
        if plan_details:
            plan_hash = plan_details[0].get("plan_hash_value", "unknown")
            cost = plan_details[0].get("cost", 0)
            table_stats = {t["table_name"]: t["num_rows"] for t in facts.get("table_stats", [])}
            plan_operations = [
                f"{s.get('operation', '')} {s.get('options', '')}".strip()
                for s in plan_details[:5]  # Top 5 operations
            ]
            store_history(fingerprint, db_name, plan_hash, cost, table_stats, plan_operations)

        logger.info(f"✅ Analysis complete with {len(plan_details)} plan steps")
        return result

    except Exception as e:
        logger.exception("❌ Exception during analysis")
        return {
            "error": f"Internal error: {e}",
            "trace": traceback.format_exc(),
            "facts": {},
            "prompt": ""
        }
    finally:
        try:
            if 'conn' in locals():
                conn.close()
        except:
            pass


@mcp.tool(
    name="compare_query_plans",
    description=(
        "🔍 Compares execution plans of two SELECT queries (original vs optimized).\n\n"
        "⚠️ SECURITY RESTRICTIONS - This tool ONLY accepts:\n"
        "✅ SELECT queries (including WITH clauses/CTEs)\n"
        "✅ Read-only operations for analysis\n\n"
        "❌ BLOCKED: All data modification, schema changes, and system operations\n"
        "(Same restrictions as analyze_full_sql_context)\n\n"
        "📊 Returns: Side-by-side cost comparison, operation differences, performance verdict.\n\n"
        "⚡ Usage: Provide two valid SELECT queries to compare their execution plans."
    ),
)
def compare_query_plans(db_name: str, original_sql: str, optimized_sql: str):
    """
    Compare two query execution plans to validate optimization improvements.
    """
    logger.info(f"🔍 compare_query_plans(db={db_name})")
    
    try:
        conn = oracle_connector.connect(db_name)
        cur = conn.cursor()
        
        # Import validation function
        from tools.oracle_collector_impl import validate_sql
        
        # Validate BOTH queries for safety
        logger.info("🔍 Validating original query...")
        is_valid_orig, error_orig, is_dangerous_orig = validate_sql(cur, original_sql)
        
        if is_dangerous_orig:
            logger.error(f"🚨 Original query BLOCKED: {error_orig}")
            return {
                "error": f"SECURITY BLOCK (original query): {error_orig}",
                "comparison": None
            }
        
        if not is_valid_orig:
            logger.error(f"❌ Original query invalid: {error_orig}")
            return {
                "error": f"Invalid original query: {error_orig}",
                "comparison": None
            }
        
        logger.info("🔍 Validating optimized query...")
        is_valid_opt, error_opt, is_dangerous_opt = validate_sql(cur, optimized_sql)
        
        if is_dangerous_opt:
            logger.error(f"🚨 Optimized query BLOCKED: {error_opt}")
            return {
                "error": f"SECURITY BLOCK (optimized query): {error_opt}",
                "comparison": None
            }
        
        if not is_valid_opt:
            logger.error(f"❌ Optimized query invalid: {error_opt}")
            return {
                "error": f"Invalid optimized query: {error_opt}",
                "comparison": None
            }
        
        logger.info("✅ Both queries are valid and safe")
        
        # Analyze original query
        logger.info("📊 Analyzing original query...")
        original_result = run_collector(cur, original_sql)
        
        # Analyze optimized query
        logger.info("📊 Analyzing optimized query...")
        optimized_result = run_collector(cur, optimized_sql)
        
        # Debug: Log what we got
        logger.info(f"   Original result keys: {list(original_result.keys())}")
        logger.info(f"   Optimized result keys: {list(optimized_result.keys())}")
        
        # Extract facts from results
        original_facts = original_result.get("facts", {})
        optimized_facts = optimized_result.get("facts", {})
        
        logger.info(f"   Original facts keys: {list(original_facts.keys())}")
        logger.info(f"   Optimized facts keys: {list(optimized_facts.keys())}")
        
        # Extract key metrics from plan_details
        original_plan = original_facts.get("plan_details", [])
        optimized_plan = optimized_facts.get("plan_details", [])
        
        logger.info(f"   Original plan steps: {len(original_plan)}")
        logger.info(f"   Optimized plan steps: {len(optimized_plan)}")
        
        if original_plan:
            logger.info(f"   Original plan[0] keys: {list(original_plan[0].keys())}")
            logger.info(f"   Original plan[0] cost: {original_plan[0].get('cost', 'N/A')}")
        
        # Get cost from first step (root operation) of execution plan
        original_cost = original_plan[0].get("cost", 0) if original_plan else 0
        optimized_cost = optimized_plan[0].get("cost", 0) if optimized_plan else 0
        
        improvement = 0
        if original_cost > 0:
            improvement = ((original_cost - optimized_cost) / original_cost) * 100
        
        comparison = {
            "original": {
                "cost": original_cost,
                "plan_summary": original_facts.get("summary", {}),
                "total_steps": len(original_plan),
                "tables": original_facts.get("summary", {}).get("tables", 0),
                "indexes": original_facts.get("summary", {}).get("indexes", 0)
            },
            "optimized": {
                "cost": optimized_cost,
                "plan_summary": optimized_facts.get("summary", {}),
                "total_steps": len(optimized_plan),
                "tables": optimized_facts.get("summary", {}).get("tables", 0),
                "indexes": optimized_facts.get("summary", {}).get("indexes", 0)
            },
            "comparison": {
                "cost_reduction": original_cost - optimized_cost,
                "improvement_percentage": round(improvement, 2),
                "is_better": optimized_cost < original_cost,
                "steps_difference": len(original_plan) - len(optimized_plan)
            }
        }
        
        logger.info(f"✅ Comparison: {improvement:.1f}% improvement")
        return comparison
        
    except Exception as e:
        logger.exception("❌ Exception during comparison")
        return {"error": str(e), "trace": traceback.format_exc()}
    finally:
        try:
            if 'conn' in locals():
                conn.close()
        except:
            pass


@mcp.tool(
    name="list_available_databases",
    description=(
        "Lists all configured database presets and tests their connectivity. "
        "Shows which databases are available for SQL analysis."
    ),
)
def list_available_databases():
    """
    Returns list of configured database presets with accessibility status.
    Tests connection to each database to verify availability.
    """
    logger.info("🔍 list_available_databases() called")
    
    databases = []
    
    for db_name, db_config in config.database_presets.items():
        db_info = {
            "name": db_name,
            "user": db_config.get("user", ""),
            "dsn": db_config.get("dsn", ""),
            "status": "unknown",
            "message": ""
        }
        
        # Test connection
        try:
            conn = oracle_connector.connect(db_name)
            cur = conn.cursor()
            
            version = "Unknown"
            db_instance = "Unknown"
            
            # Try to get database version and name (requires V$ access)
            try:
                cur.execute("SELECT banner FROM v$version WHERE ROWNUM = 1")
                row = cur.fetchone()
                if row:
                    version = row[0]
                
                cur.execute("SELECT name FROM v$database")
                row = cur.fetchone()
                if row:
                    db_instance = row[0]
            except Exception as v_error:
                # User doesn't have V$ access, but connection is valid
                if "ORA-00942" in str(v_error):
                    logger.info(f"⚠️  {db_name}: Connected but no V$ view access")
                else:
                    raise  # Re-raise if it's not a permission issue
            
            db_info["status"] = "accessible"
            db_info["message"] = "Connected successfully" if version != "Unknown" else "Connected (limited V$ access)"
            db_info["version"] = version
            db_info["instance"] = db_instance
            
            conn.close()
            logger.info(f"✅ {db_name}: accessible")
            
        except Exception as e:
            db_info["status"] = "error"
            db_info["message"] = str(e)
            logger.warning(f"❌ {db_name}: {e}")
        
        databases.append(db_info)
    
    result = {
        "databases": databases,
        "total": len(databases),
        "accessible": sum(1 for db in databases if db["status"] == "accessible"),
        "errors": sum(1 for db in databases if db["status"] == "error")
    }
    
    # Return dict directly - no JSON serialization
    return result
