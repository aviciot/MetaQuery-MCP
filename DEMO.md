# 🎯 Performance MCP - Live Demo Guide

## 📋 Demo Overview

**Databases:** Oracle (transformer_master, way4_docker7/8) + MySQL (mysql_devdb03_avi)  
**Key Features:** Performance monitoring, query analysis, authentication, safeguards

---

## 🔑 Key MCP Features to Highlight

### 🔐 Security Features
- **API Key Authentication**: Bearer token-based authentication
- **Multi-client Support**: Named API keys with per-request logging
- **Public Endpoints**: Health checks exempt from authentication

### 🛡️ Safeguard Levels
- **Level 1 (READ_ONLY)**: Safe queries only - SELECT, SHOW, DESCRIBE
- **Level 2 (ADMIN_READ)**: Performance views - V$, DBA_, system tables
- **Level 3 (WRITE_OPERATIONS)**: DML operations - INSERT, UPDATE, DELETE
- **Level 4 (DDL_OPERATIONS)**: Schema changes - CREATE, ALTER, DROP
- **Level 5 (CRITICAL_OPERATIONS)**: System commands - GRANT, REVOKE, TRUNCATE

### 📊 Core Capabilities

- **Query Performance Analysis**: Top queries by CPU/elapsed time/executions plan
- **Real-time Performance Monitoring**: Live database health metrics
- **Historical Trend Analysis**: 30-day retention with time-series data
- **Cross-Database Support**: Oracle + MySQL unified interface
- **JSON Chart Data**: Chart.js-compatible visualization data

---

## 🎬 Demo Script

### **Part 1: Database Health Monitoring (onl ORACLE  for now) **

#### Prompt 1: Real-time Oracle Health
```
Check the current health status of transformer_master database
```

**What to highlight:**
- CPU usage, memory stats
- Active sessions breakdown
- Buffer cache hit ratio
- Wait events analysis
- Real-time metrics from V$ views

### **Part 2: Performance Trends & Historical Data (4 mins)**

#### Prompt 3: CPU Trend Analysis
```
Show me CPU usage trend for transformer_master over the last 24 hours
```

**What to highlight:**
- Historical snapshot storage (SQLite)
- Time-series data with timestamps
- JSON chart data format (Chart.js compatible)
- Peak usage identification
- 30-day retention policy

#### Prompt 4: Multi-metric Comparison
```
Compare active sessions and CPU usage for transformer_master over the last 12 hours
```

**What to highlight:**
- Multiple metrics in single request
- Correlation analysis
- Performance patterns
- Snapshot-based historical tracking

#### Prompt 5: Cache Performance
```
Show buffer cache hit ratio trend for transformer_master over the last 6 hours
```

**What to highlight:**
- Cache efficiency tracking
- Performance degradation detection
- Proactive monitoring capabilities

---

### **Part 3: Query Performance Analysis (5 mins)**

#### Prompt 6: Top CPU Consumers (Oracle)
```
Get top 10 queries by CPU time on transformer_master(applicative only)
```

**What to highlight:**
- SQL_ID identification
- Execution counts
- CPU time per execution
- Elapsed time metrics
- Buffer gets (logical reads)


---

### ** Advanced Oracle Analysis **

#### Prompt 9: Execution Plan Analysis for specific sqlid
```
Get the execution plan for SQL_ID: cg51p9bh202pa on transformer_master
```

**What to highlight:**
- Direct V$SQL_PLAN access
- Cost-based optimizer insights
- Access paths (INDEX, FULL TABLE SCAN)
- Join methods
- Cardinality estimates

#### Historical SQL Performance (for same/ sqlid)
```
Get historical performance for SQL_ID:cg51p9bh202pa  on transformer_master
```

**What to highlight:**
- Performance over time
- Execution pattern changes
- Resource consumption trends
- AWR/Statspack-like data

### **Part 5: Cross-Database Comparison (3 mins)**

#### Prompt 12: Multi-Database Health
```
Compare database health across transformer_master and way4_docker7
```

**What to highlight:**
- Unified interface for different DB types
- Side-by-side comparison
- Normalized metrics
- Multi-environment monitoring

#### Performance Comparison (but only master i have permissions)
```
Show me top queries by CPU time on both transformer_master and way4_docker7
```

---

### **Part 6: Query Optimization & Analysis (8 mins)**

This is the most critical part for DBAs and developers - identifying and optimizing problematic queries.

#### **Oracle Query Optimization**

##### Prompt 13: Comprehensive Query Analysis
```
Analyze the performance characteristics of SQL_ID: cg51p9bh202pa on transformer_master. 
Include execution statistics, execution plan, and optimization recommendations.
```

**What to highlight:**
- Full execution statistics (CPU, elapsed time, buffer gets, disk reads)
- Execution plan with cost analysis
- Index usage and access paths
- Potential bottlenecks identification
- Optimization opportunities

##### Prompt 14: Expensive Operations Detection
```
Show me the most expensive operations in the execution plan for SQL_ID: cg51p9bh202pa on transformer_master
```

**What to highlight:**
- TABLE ACCESS FULL (full table scans)
- High-cost operations
- Nested loops vs hash joins
- Sort operations (memory/disk)
- Missing index opportunities

##### Prompt 15: Index Analysis & Recommendations
```
Analyze the indexes used by SQL_ID: cg51p9bh202pa on transformer_master. 
Are there any missing indexes or unused indexes?
```

**What to highlight:**
- Current index usage
- Index scan vs full table scan
- Cardinality issues
- Index selectivity
- Recommendation for new indexes

##### Prompt 16: Query Rewrite Suggestions
```
Based on the execution plan for SQL_ID: cg51p9bh202pa, suggest query rewrites or optimizations
to improve performance on transformer_master
```

**What to highlight:**
- Join order optimization
- Predicate pushdown opportunities
- Subquery vs JOIN alternatives
- EXISTS vs IN clause optimization
- Bind variable usage

##### Prompt 17: Wait Event Analysis for Query
```
What are the main wait events for SQL_ID: cg51p9bh202pa on transformer_master?
Show me where this query is spending time.
```

**What to highlight:**
- db file sequential read (index scans)
- db file scattered read (full table scans)
- CPU time vs wait time ratio
- Disk I/O patterns
- Contention points

##### Prompt 18: Historical Performance Comparison
```
Compare the current performance of SQL_ID: cg51p9bh202pa with its historical performance 
on transformer_master. Has it degraded over time?
```

**What to highlight:**
- Performance trends (improving/degrading)
- Execution count changes
- Resource consumption growth
- Plan changes (plan instability)
- Statistics staleness indicators

##### Prompt 19: SQL Text & Bind Variables
```
Show me the full SQL text for SQL_ID: cg51p9bh202pa on transformer_master. 
Include bind variable information if available.
```

**What to highlight:**
- Complete query text
- Bind variable datatypes
- Bind variable peeking issues
- Query complexity assessment
- Opportunities for query simplification

##### Prompt 20: Similar Queries Detection
```
Find similar queries to SQL_ID: cg51p9bh202pa on transformer_master that might benefit 
from the same optimizations
```

**What to highlight:**
- Query patterns
- Shared optimization opportunities
- Cursor sharing issues
- Literal vs bind variables
- Opportunities for standardization

#### **MySQL Query Optimization**

##### Prompt 21: MySQL Query Performance Analysis
```
Analyze the top 10 queries by execution time on mysql_devdb03_avi. 
Show me which queries need optimization.
```

**What to highlight:**
- Query digest analysis
- Execution counts
- Average execution time
- Row examined vs rows sent ratio (efficiency)
- Lock time and wait time

##### Prompt 22: MySQL Slow Query Analysis
```
Show me queries on mysql_devdb03_avi that have execution time > 1 second. 
Include full table scan detection.
```

**What to highlight:**
- Performance Schema data
- Full table scans (no_index_used, no_good_index_used)
- Slow query patterns
- Sort and temporary table usage
- Query efficiency ratio

##### Prompt 23: MySQL Index Usage Analysis
```
Analyze index usage for the top queries on mysql_devdb03_avi. 
Are indexes being used effectively?
```

**What to highlight:**
- Index hit rate
- Full table scan frequency
- Missing index detection
- Unused indexes (overhead)
- Covering index opportunities

##### Prompt 24: MySQL JOIN Optimization
```
Show me queries with multiple JOINs on mysql_devdb03_avi and analyze their performance.
Are the JOIN orders optimal?
```

**What to highlight:**
- JOIN algorithm used (nested loop, hash join)
- JOIN order optimization
- Derived table performance
- Subquery vs JOIN efficiency
- Temporary table creation

##### Prompt 25: MySQL Query Rewrite Recommendations
```
For the slowest query on mysql_devdb03_avi, provide optimization recommendations including:
- Index suggestions
- Query rewrites
- Schema changes
```

**What to highlight:**
- Specific index recommendations (columns, order)
- Query structure improvements
- WHERE clause optimization
- SELECT * vs specific columns
- Aggregate function optimization

##### Prompt 26: MySQL Buffer Pool Efficiency
```
Analyze the buffer pool efficiency for queries on mysql_devdb03_avi. 
Are queries hitting disk too frequently?
```

**What to highlight:**
- Buffer pool hit ratio
- Physical reads vs logical reads
- Hot data identification
- Memory allocation recommendations
- Cache warming strategies

#### **Cross-Database Query Optimization**

##### Prompt 27: Comparative Performance Analysis
```
Compare the performance characteristics of similar queries on transformer_master (Oracle) 
and mysql_devdb03_avi. Which database handles the workload better?
```

**What to highlight:**
- Query execution time comparison
- Resource consumption patterns
- Optimizer differences (Oracle CBO vs MySQL)
- Index strategy differences
- Scalability considerations

##### Prompt 28: Migration Performance Assessment
```
If we migrate queries from Oracle to MySQL (or vice versa), what performance changes 
should we expect? Analyze current patterns on both databases.
```

**What to highlight:**
- Workload characteristics
- Feature differences (hints, partitioning)
- Execution plan differences
- Lock contention differences
- Migration risks and opportunities

---

### **Query Optimization Best Practices to Mention**

#### Oracle-Specific
- **Statistics**: Ensure table/index statistics are current (`DBMS_STATS`)
- **Hints**: Use hints sparingly (/*+ INDEX */, /*+ PARALLEL */)
- **Partitioning**: Consider partitioning for large tables
- **Result Cache**: Use result cache for frequently accessed data
- **SQL Profile**: Create SQL profiles for specific queries

#### MySQL-Specific
- **EXPLAIN**: Always use EXPLAIN ANALYZE for query analysis
- **Covering Indexes**: Design indexes to cover query needs
- **Query Cache**: Monitor query cache effectiveness (if enabled)
- **JOIN Buffer**: Optimize join_buffer_size for large JOINs
- **Table Structure**: Consider table engine (InnoDB vs MyISAM)

#### Universal Best Practices
- **Avoid SELECT ***: Specify only needed columns
- **Limit Result Sets**: Use WHERE clauses effectively
- **Index Selectivity**: Create indexes on high-cardinality columns
- **Avoid Functions on Columns**: `WHERE UPPER(name) = 'X'` prevents index use
- **Use Batch Operations**: Bulk inserts/updates over individual operations
- **Monitor Regularly**: Set up alerts for query degradation

---
