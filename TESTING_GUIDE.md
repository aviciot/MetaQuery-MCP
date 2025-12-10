# Testing Guide: History Tracking & LLM Response

## Issue Summary
1. **History Tracking**: Need to verify fingerprinting and historical data is working
2. **LLM Response Format**: Something changed in how LLM presents the analysis

---

## ✅ FIXED: Table Extraction Issue

**Problem**: MySQL was extracting "AVI" as table name instead of "customer_order"  
**Root Cause**: Regex didn't handle `schema.table` notation  
**Fix Applied**: Updated regex to handle `avi.customer_order` → extracts `customer_order`

---

## 🧪 Test 1: Verify Table Extraction Fix

### Run this query 2-3 times to build history:

```sql
analyze this query on the mysql_devdb03_avi database - provide optimized version if possible,

SELECT *
FROM avi.customer_order
WHERE amount > 20
ORDER BY status, order_date;
```

### Expected Behavior:

**First Run** (New Query):
- LLM should start with: `🆕 **First Execution** - Establishing baseline`
- Check Claude logs for: `[MYSQL-COLLECTOR] Tables found: ['CUSTOMER_ORDER']` (not 'AVI')
- Check logs for: `📊 Found 0 historical executions for fingerprint...`

**Second Run** (Same Query):
- LLM should start with: `🕒 **Query History**` section
- Show: "This query has been executed 1 time before"
- Check logs for: `📊 Found 1 historical executions for fingerprint...`
- Historical context should show previous cost/timestamp

**Third Run** (Historical Trend):
- LLM should show: "This query has been executed 2 times before"
- Historical context shows performance trend
- Check logs for: `📊 Found 2 historical executions for fingerprint...`

---

## 🧪 Test 2: Verify Fingerprint Normalization

Run these queries **one after another** - they should all match the **same fingerprint**:

### Query A:
```sql
SELECT * FROM avi.customer_order WHERE amount > 20 ORDER BY status, order_date;
```

### Query B (different literal value):
```sql
SELECT * FROM avi.customer_order WHERE amount > 100 ORDER BY status, order_date;
```

### Query C (different literal value):
```sql
SELECT * FROM avi.customer_order WHERE amount > 999 ORDER BY status, order_date;
```

### Expected Behavior:
- All 3 queries should have **THE SAME FINGERPRINT** (logs will show: `fingerprint da013dea...`)
- Query B should see 1 historical execution (from Query A)
- Query C should see 2 historical executions (from Query A + B)
- LLM should recognize it's the same query pattern with different parameter values

---

## 🧪 Test 3: Check Database Isolation

Run the same query on **different databases**:

### On MySQL:
```sql
analyze this query on mysql_devdb03_avi
SELECT * FROM customer_order WHERE amount > 20;
```

### On Oracle (if you have similar table):
```sql
analyze this query on way4_docker7
SELECT * FROM merchant_statement WHERE contract_id = 12345;
```

### Expected Behavior:
- Each database tracks history **separately**
- MySQL history does NOT affect Oracle history
- Check logs: `db_name` field should differ

---

## 📊 How to Check Logs

### Look for these log entries:

1. **Fingerprinting**:
```
📊 Found N historical executions for fingerprint da013dea...
```

2. **Table Extraction (FIXED)**:
```
[MYSQL-COLLECTOR] Tables found: ['CUSTOMER_ORDER']  ← Should be customer_order, not AVI
```

3. **History Storage**:
```
📊 Historical context: <message>
```

4. **Plan Steps**:
```
[MYSQL-COLLECTOR] Extracted N plan steps  ← Should be > 0 now
```

---

## 🔍 Check LLM Response Format

### What LLM Should Include:

**For NEW Query** (first execution):
```
🆕 **First Execution** - Establishing baseline for this query pattern

[Then proceed with normal analysis...]
```

**For REPEATED Query** (2nd+ execution):
```
🕒 **Query History**

This query pattern has been executed N time(s) before.

📊 Historical Performance:
- Previous execution: <timestamp>
- Previous cost: <cost>
- Current cost: <cost>
- Trend: [Improved/Degraded/Stable]

⚠️ <Context-specific insight based on history>

[Then proceed with normal analysis...]
```

---

## 🐛 If History Tracking Doesn't Work

Run the standalone test script (already created):

```powershell
python test_history_tracking.py
```

This will test:
1. Fingerprinting (same query with different literals → same fingerprint)
2. History storage and retrieval
3. Database isolation

### Clear test data:
```powershell
python test_history_tracking.py --clear
```

### Show database contents:
```powershell
python test_history_tracking.py --show
```

---

## 📁 History Database Location

Inside Docker container: `/app/data/query_history.db`

On your machine (volume-mounted): Check if you have a volume mount in `docker-compose.yml`

### To inspect database manually:

1. Enter container:
```powershell
docker exec -it performance_mcp sh
```

2. Query database:
```sh
sqlite3 /app/data/query_history.db
.schema
SELECT * FROM executions ORDER BY timestamp DESC LIMIT 5;
.quit
```

---

## ✅ Success Criteria

### History Tracking Works If:
- [ ] Same query pattern (different literals) shows historical context
- [ ] LLM mentions "This query has been executed N times before"
- [ ] Logs show: `📊 Found N historical executions`
- [ ] Table extraction finds correct table (not "AVI")
- [ ] Plan steps > 0 (not 0 plan steps anymore)

### LLM Response Format Correct If:
- [ ] First run starts with: `🆕 **First Execution**`
- [ ] Subsequent runs start with: `🕒 **Query History**`
- [ ] Historical context section appears BEFORE execution plan analysis
- [ ] Performance trend is mentioned (Improved/Degraded/Stable)

---

## 🔧 Quick Fixes

### If table extraction still shows "AVI":
- Check logs for: `[MYSQL-COLLECTOR] extract_tables_from_sql: ['AVI']`
- The fix was applied, so rebuild: `docker compose up --build`

### If no history shows up:
- Check if database file exists: `docker exec performance_mcp ls -la /app/data/`
- Run test script: `python test_history_tracking.py`
- Check fingerprint in logs - should be consistent across runs

### If LLM doesn't show historical context:
- Check `facts["historical_context"]` in tool response
- Verify prompt includes: `START your response with the historical context`
- Check if `history_count` > 0 in facts

---

## 💡 Tips

1. **Use Claude Desktop** with MCP configured to see full LLM responses
2. **Watch Docker logs** in real-time: `docker compose logs -f`
3. **Run same query 3+ times** to see trend analysis kick in
4. **Try different literal values** to test fingerprint normalization
5. **Check timestamps** in historical context to confirm recency

---

## 📞 What to Report Back

If issues persist, share:
1. Docker logs showing fingerprint hash
2. LLM's actual response (first paragraph)
3. Result of `python test_history_tracking.py`
4. Output of: `[MYSQL-COLLECTOR] Tables found: [...]`
