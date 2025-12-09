from mcp_app import mcp
import json

def sanitize_for_prompt(text: str) -> str:
    """
    Sanitize text for safe inclusion in prompts.
    Escapes quotes and newlines to prevent injection.
    """
    if not text:
        return ""
    # Escape backslashes first, then quotes
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    text = text.replace('\n', '\\n')
    text = text.replace('\r', '\\r')
    return text

def validate_query_input(query: str) -> tuple[bool, str]:
    """
    Basic validation for SQL queries in prompts.
    Returns (is_valid, error_message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    # Check for extremely long queries (potential DoS)
    if len(query) > 100000:  # 100KB limit
        return False, f"Query too long ({len(query)} chars). Maximum is 100,000 characters."
    
    # Basic check - query should start with SELECT or WITH (after whitespace)
    first_word = query.strip().upper().split()[0] if query.strip() else ""
    if first_word not in ('SELECT', 'WITH'):
        return False, f"Query must start with SELECT or WITH, found: {first_word}"
    
    return True, ""

@mcp.prompt()
def oracle_full_analysis(db_name: str, query: str):
    """Full Oracle query performance analysis - checks everything"""
    
    # SECURITY: Validate inputs
    is_valid, error = validate_query_input(query)
    if not is_valid:
        return f"ERROR: {error}\n\nPlease provide a valid SELECT query."
    
    # SECURITY: Sanitize for safe embedding
    safe_db = sanitize_for_prompt(db_name)
    safe_query = sanitize_for_prompt(query)
    
    # Use JSON format for tool call to avoid injection
    tool_instruction = f'Call: analyze_full_sql_context with db_name="{safe_db}" and sql_text containing the query below'
    
    return f"""Analyze this Oracle query for ALL performance issues.

Database: {db_name}
Query to analyze:
```sql
{query}
```

Tool Instruction: {tool_instruction}

Focus on:
- Execution plan cost and operations
- Index usage (SKIP SCAN, missing indexes, wrong column order)
- Partition pruning effectiveness
- Table/join efficiency
- Cardinality estimates

Provide specific fixes with DDL statements."""

@mcp.prompt()
def oracle_index_analysis(db_name: str, query: str):
    """Analyze only index-related problems"""
    
    # SECURITY: Validate inputs
    is_valid, error = validate_query_input(query)
    if not is_valid:
        return f"ERROR: {error}\n\nPlease provide a valid SELECT query."
    
    return f"""Check index problems for this Oracle query.

Database: {db_name}
Query to analyze:
```sql
{query}
```

Use tool: analyze_full_sql_context(db_name="{db_name}", sql_text=<query_above>)

Focus ONLY on:
- INDEX SKIP SCAN problems
- Missing indexes
- Wrong index column order
- Unused indexes

Ignore: partitions, joins, table stats (unless related to index usage)

Provide CREATE INDEX statements to fix issues."""

@mcp.prompt()
def oracle_partition_analysis(db_name: str, query: str):
    """Analyze partition pruning problems"""
    
    # SECURITY: Validate inputs
    is_valid, error = validate_query_input(query)
    if not is_valid:
        return f"ERROR: {error}\n\nPlease provide a valid SELECT query."
    
    return f"""Check partition pruning for this Oracle query.

Database: {db_name}
Query to analyze:
```sql
{query}
```

Use tool: analyze_full_sql_context(db_name="{db_name}", sql_text=<query_above>)

Focus ONLY on:
- Are all partitions being scanned?
- Is partition key in WHERE clause?
- PARTITION HASH ALL vs SINGLE
- Partition key recommendations

Ignore: index problems, join problems (unless related to partitions)

Explain how to improve partition pruning."""

@mcp.prompt()
def oracle_rewrite_query(db_name: str, original_query: str):
    """Rewrite and optimize Oracle query based on analysis"""
    
    # SECURITY: Validate inputs
    is_valid, error = validate_query_input(original_query)
    if not is_valid:
        return f"ERROR: {error}\n\nPlease provide a valid SELECT query."
    
    return f"""Rewrite this Oracle query for better performance.

Database: {db_name}
Original Query to analyze and rewrite:
```sql
{original_query}
```

Steps:
1. Use tool: analyze_full_sql_context(db_name="{db_name}", sql_text=<query_above>)
2. Analyze execution plan and identify bottlenecks
3. Rewrite query to fix issues:
   - Simplify CTEs (eliminate nested scans)
   - Pre-calculate derived fields
   - Replace string parsing with direct columns
   - Add hints if needed (MATERIALIZE, INDEX, etc.)
   - Optimize joins order

Output:
- Optimized query (full SQL)
- List of changes made
- Expected performance improvement
- DDL for any required indexes

Make query production-ready and maintainable."""


@mcp.prompt()
def oracle_what_if_growth(db_name: str, query: str, growth_scenario: str = ""):
    """Predict performance impact as data grows (what-if analysis)"""
    
    # SECURITY: Validate inputs
    is_valid, error = validate_query_input(query)
    if not is_valid:
        return f"ERROR: {error}\n\nPlease provide a valid SELECT query."
    
    scenario_text = growth_scenario or "2x, 5x, and 10x data growth"
    
    return f"""Predict how this Oracle query will perform under this scenario: {scenario_text}

Database: {db_name}
Query to analyze:
```sql
{query}
```

IMPORTANT - Tool Usage Strategy:
- If this is your FIRST analysis of this query: Call analyze_full_sql_context(db_name="{db_name}", sql_text=<query_above>)
- If you ALREADY analyzed this query in previous messages: DO NOT call the tool again - reuse the data you already have
- Only re-analyze if user explicitly says "re-analyze" or "check again"

Performance Prediction Method:
1. Use current execution plan operations from your analysis:
   - TABLE ACCESS FULL scales O(n) - linearly with row count
   - INDEX RANGE SCAN scales O(log n) - slowly (add ~10% per 10x growth)
   - INDEX SKIP SCAN scales O(n) - linearly (already inefficient)
   - NESTED LOOPS scale O(n²) - quadratically (danger zone!)
   - HASH JOIN scales O(n) - linearly with larger table

2. Calculate projected row counts:
   - Take current num_rows from table_stats
   - Apply growth scenario multiplier
   - Example: 378 rows → {scenario_text} → show new counts

3. Predict cost changes:
   - For each plan operation, estimate new cost based on scaling behavior
   - Example: FULL SCAN 100 cost on 500 rows → 1000 cost on 5000 rows (10x data = 10x cost)

4. Identify tipping points:
   - At what data size do NESTED LOOPS become unacceptable?
   - When should SKIP SCAN be replaced with proper index?
   - When does FULL SCAN justify adding index?

Output Format:
- Current baseline (cost, row counts per table)
- Projected metrics for each scenario (cost, runtime factor)
- First bottleneck operation and threshold
- Proactive recommendations with DDL if needed

Be specific with numbers and calculations."""


# LEGACY PROMPT - KEEPING FOR BACKWARD COMPATIBILITY
@mcp.prompt()
def oracle_query_tuning_prompt(query: str, execution_plan: str = "", error_message: str = ""):
    """Legacy prompt - use oracle_full_analysis instead"""
    plan = execution_plan or "No execution plan provided"
    err = error_message or "No errors"
    
    return f"""Analyze this Oracle query for performance issues.

Query: {query}
Execution Plan: {plan}
Error: {err}

Provide specific optimization recommendations."""
