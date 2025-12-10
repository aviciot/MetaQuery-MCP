# Visualization & Trend Analysis Test Prompts

## 📊 Understanding Visualization in MCP

### What We Provide:
- ✅ **JSON chart data** (Chart.js compatible format)
- ✅ **Raw time-series data** (timestamps + values)
- ✅ **Trend analysis** (increasing/decreasing/stable)
- ✅ **Statistical summaries** (min, max, average)

### What We DON'T Provide:
- ❌ **Rendered images** - MCP tools return text/JSON only
- ❌ **Interactive charts** - Claude Desktop cannot render charts
- ❌ **Plots/graphs** - No matplotlib/plotly execution in MCP

### How It Works:
1. Tool returns JSON chart data + raw data
2. Claude (LLM) analyzes the data and describes trends to you
3. You can copy the JSON and visualize it externally if needed

---

## 🧪 Test Prompts for Visualization/Trends

### Test 1: CPU Usage Trend (Basic)
```
Show me the CPU usage trend for transformer_master over the last 12 hours.

Analyze the pattern - is it stable, increasing, or decreasing?
Are there any spikes or anomalies?
```

**What to expect:**
- JSON chart data with timestamps and CPU percentages
- Claude will describe: "The CPU usage shows a stable pattern around X%, with a spike to Y% at [time]"

---

### Test 2: Active Sessions Over Time
```
Get the active sessions trend for way4_docker7 over the last 24 hours with 1-hour intervals.

Tell me:
- What's the peak session count and when did it occur?
- What's the typical session count during business hours vs off-hours?
- Are there any concerning patterns?
```

**What to expect:**
- Time-series data showing session counts
- Claude will identify peak times and patterns
- JSON chart data for external visualization

---

### Test 3: Buffer Cache Performance
```
Show me the buffer cache hit ratio trend for transformer_master over the last 6 hours.

Analyze:
- Is the cache hit ratio healthy? (should be >95%)
- Are there any drops that indicate memory pressure?
- What's the trend - improving or degrading?
```

**What to expect:**
- Cache hit ratio percentages over time
- Claude will flag any drops below 95%
- Trend analysis (stable/improving/degrading)

---

### Test 4: Multi-Metric Comparison (Advanced)
```
Get performance trends for transformer_master:
1. CPU usage over last 24 hours
2. Active sessions over last 24 hours

Compare the two trends and tell me if CPU spikes correlate with session increases.
```

**What to expect:**
- Two separate trend datasets
- Claude will analyze correlation between metrics
- Recommendations if patterns are concerning

---

### Test 5: Query Performance Trend (If you have a specific SQL_ID)
```
Show me the performance trend for SQL_ID <your_sql_id> on way4_docker7 over the last 48 hours.

Has the query gotten slower over time?
Are there any execution time spikes?
```

**What to expect:**
- Execution time trends for specific query
- Detection of performance degradation
- Identification of anomalous executions

---

## 📈 Understanding "Graph" vs "Plot" vs "Chart"

### They Mean the Same Thing:
- **Graph** = **Plot** = **Chart** = **Visualization**

All these terms refer to the same thing in our context:
- Time-series data with JSON format
- Trend analysis by the LLM
- No actual image rendering

### Example Prompts (All Equivalent):

```
"Show me a graph of CPU usage"
"Plot CPU usage over time"
"Chart the CPU trend"
"Visualize CPU performance"
"Get CPU usage trend data"
```

**All will return the same JSON chart data + analysis**

---

## 🎯 Best Practices for Visualization Requests

### ✅ DO:
1. **Specify time range**: "last 12 hours", "last 2 days"
2. **Specify metric**: "CPU usage", "active sessions", "cache hit ratio"
3. **Ask for analysis**: "what's the trend?", "any anomalies?"
4. **Request comparisons**: "compare CPU and sessions"

### ❌ DON'T:
1. **Ask for image files**: "show me a PNG chart" (not possible in MCP)
2. **Request interactive features**: "make it clickable" (MCP is text/JSON only)
3. **Expect rendered visuals**: Claude can describe but not show images

---

## 📊 Chart Data Format (JSON)

When you request trends, you get JSON like this:

```json
{
  "type": "line",
  "data": {
    "labels": [
      "2025-12-10T08:00:00",
      "2025-12-10T09:00:00",
      "2025-12-10T10:00:00"
    ],
    "datasets": [{
      "label": "CPU Usage",
      "data": [45.2, 52.1, 48.7],
      "borderColor": "rgb(75, 192, 192)",
      "backgroundColor": "rgba(75, 192, 192, 0.2)"
    }]
  },
  "options": {
    "responsive": true,
    "plugins": {
      "title": {
        "display": true,
        "text": "CPU Usage Over Time"
      }
    }
  }
}
```

This format is compatible with:
- **Chart.js** (JavaScript library)
- **matplotlib** (with conversion)
- **plotly** (with conversion)

---

## 💡 Example Workflow

### Step 1: Get Trend Data
```
Show me CPU usage trend for transformer_master over last 6 hours
```

### Step 2: Claude Analyzes
```
Claude responds:
"The CPU usage shows a stable pattern averaging 48% with a notable 
spike to 72% at 09:30 UTC, likely due to batch job execution. 
The trend is stable overall with no concerning patterns."
```

### Step 3: Optional - Visualize Externally
If you want to see an actual chart:
1. Copy the JSON from `chart.data` in the response
2. Use Chart.js playground: https://www.chartjs.org/docs/latest/samples/
3. Paste the JSON to see the visualization

---

## 🚀 Quick Start Test Sequence

Try these in order to test all features:

```
1. "Check health of transformer_master database"
   → Tests: Basic health metrics

2. "Show CPU trend for transformer_master over last 6 hours"
   → Tests: Basic trend visualization

3. "Show active sessions trend for way4_docker7 over last 12 hours"
   → Tests: Different metric type

4. "Get performance trends for transformer_master: CPU and sessions over last 24 hours"
   → Tests: Multi-metric analysis

5. "Show me top 5 queries by CPU time on transformer_master, exclude system queries"
   → Tests: Query performance monitoring
```

---

## 📝 Notes

### Current Implementation:
- ✅ JSON chart data generation
- ✅ Time-series data collection
- ✅ Trend analysis (statistical)
- ✅ Multiple metrics supported
- ✅ Historical snapshots (30-day retention)

### Not Implemented:
- ❌ Image rendering (Chart.js/matplotlib execution)
- ❌ ASCII art charts (optional feature, not enabled)
- ❌ Real-time streaming (MCP tools are request/response)

### Why No Images?
MCP (Model Context Protocol) is designed for **structured data exchange**, not image rendering. The LLM analyzes the JSON data and describes trends in natural language, which is often more useful than a static image.

---

## 🎓 Summary

**"Visualization"** in our MCP server means:
1. Generate JSON chart data (Chart.js format)
2. LLM analyzes the data
3. LLM describes trends, patterns, and anomalies in plain English
4. You can optionally visualize the JSON externally

**Graph = Plot = Chart = Visualization** - they all mean the same thing and return the same JSON format.
