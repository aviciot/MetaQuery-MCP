-- TEST QUERY 1: Simple single table query (guaranteed to work)
-- This queries the data dictionary which always exists
SELECT table_name, num_rows, last_analyzed
FROM all_tables
WHERE owner = 'OWS'
  AND table_name IN ('MERCHANT_STATEMENT', 'MERCHANT_STATEMENT_ENTRY')
  AND ROWNUM <= 10;

-- TEST QUERY 2: Simple query with JOIN (if you know the correct column names)
-- Replace column_name_here with actual column names from your tables
-- To find column names, run:
-- SELECT column_name FROM all_tab_columns 
-- WHERE owner = 'OWS' AND table_name = 'MERCHANT_STATEMENT';

-- TEST QUERY 3: Minimal working example for MCP testing
SELECT owner, table_name, num_rows
FROM all_tables
WHERE owner = 'OWS'
  AND num_rows > 0
  AND ROWNUM <= 5;
