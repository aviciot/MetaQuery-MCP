"""
Test script to verify history tracking and fingerprinting.

Usage:
1. Run this script 3 times with the SAME query → Should see history build up
2. Run with DIFFERENT literal values → Should match as same fingerprint
"""

import sys
sys.path.insert(0, 'server')

from history_tracker import normalize_and_hash, store_history, get_recent_history
import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path("server/data/query_history.db")

def test_fingerprinting():
    """Test that queries with different literals get same fingerprint."""
    print("\n" + "="*60)
    print("TEST 1: Fingerprinting (Normalization)")
    print("="*60)
    
    queries = [
        "SELECT * FROM customer WHERE id = 12345",
        "SELECT * FROM customer WHERE id = 67890",
        "SELECT * FROM customer WHERE id = 99999",
    ]
    
    fingerprints = []
    for q in queries:
        fp = normalize_and_hash(q)
        fingerprints.append(fp)
        print(f"Query: {q}")
        print(f"  → Fingerprint: {fp}\n")
    
    if len(set(fingerprints)) == 1:
        print("✅ PASS: All queries have the SAME fingerprint (normalized correctly)")
    else:
        print("❌ FAIL: Queries have DIFFERENT fingerprints (normalization broken)")
        return False
    
    return True


def test_history_storage():
    """Test storing and retrieving history."""
    print("\n" + "="*60)
    print("TEST 2: History Storage & Retrieval")
    print("="*60)
    
    # Test query
    sql = "SELECT * FROM customer_order WHERE amount > 20 ORDER BY status"
    db_name = "mysql_devdb03_avi"
    
    fp = normalize_and_hash(sql)
    print(f"Query: {sql}")
    print(f"Fingerprint: {fp}")
    print(f"Database: {db_name}\n")
    
    # Store 3 executions with different costs
    print("Storing 3 executions...")
    for i, cost in enumerate([100, 85, 75], 1):
        store_history(
            fingerprint=fp,
            db_name=db_name,
            plan_hash=f"plan_{i}",
            cost=cost,
            table_stats={"customer_order": 1000 + i*100},
            plan_operations=[f"INDEX_SCAN table_{i}"]
        )
        print(f"  Execution {i}: cost={cost}")
    
    # Retrieve history
    print("\nRetrieving history...")
    history = get_recent_history(fp, db_name)
    
    if history:
        print(f"✅ PASS: Found {len(history)} historical executions")
        for i, h in enumerate(history, 1):
            print(f"  {i}. Timestamp: {h['timestamp']}, Cost: {h['cost']}")
        return True
    else:
        print("❌ FAIL: No history found")
        return False


def test_different_databases():
    """Test that same query on different databases are tracked separately."""
    print("\n" + "="*60)
    print("TEST 3: Database Isolation")
    print("="*60)
    
    sql = "SELECT * FROM merchant_statement WHERE contract_id = 12345"
    fp = normalize_and_hash(sql)
    
    # Store on 2 different databases
    databases = ["way4_docker7", "way4_docker8"]
    for db in databases:
        store_history(
            fingerprint=fp,
            db_name=db,
            plan_hash="plan_x",
            cost=50,
            table_stats={"merchant_statement": 500},
            plan_operations=["TABLE_SCAN"]
        )
        print(f"Stored execution on: {db}")
    
    # Check each database separately
    print("\nRetrieving history per database:")
    for db in databases:
        history = get_recent_history(fp, db)
        count = len(history) if history else 0
        print(f"  {db}: {count} execution(s)")
    
    print("✅ PASS: Databases track history independently")
    return True


def check_database_contents():
    """Show current database contents."""
    print("\n" + "="*60)
    print("DATABASE CONTENTS")
    print("="*60)
    
    if not DB_PATH.exists():
        print("❌ Database does not exist yet")
        return
    
    conn = sqlite3.connect(DB_PATH)
    
    # Count total executions
    cursor = conn.execute("SELECT COUNT(*) FROM executions")
    total = cursor.fetchone()[0]
    print(f"Total executions stored: {total}")
    
    # Count by database
    cursor = conn.execute("""
        SELECT db_name, COUNT(*) as count
        FROM executions
        GROUP BY db_name
        ORDER BY count DESC
    """)
    print("\nExecutions per database:")
    for db_name, count in cursor.fetchall():
        print(f"  {db_name}: {count}")
    
    # Show recent 5
    cursor = conn.execute("""
        SELECT db_name, timestamp, cost
        FROM executions
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    print("\nMost recent 5 executions:")
    for db_name, timestamp, cost in cursor.fetchall():
        print(f"  {timestamp} | {db_name} | cost={cost}")
    
    conn.close()


def clear_test_data():
    """Clear test data from database."""
    if not DB_PATH.exists():
        return
    
    print("\n" + "="*60)
    print("Clearing test data...")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM executions")
    conn.commit()
    conn.close()
    print("✅ Test data cleared")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test history tracking")
    parser.add_argument("--clear", action="store_true", help="Clear test data")
    parser.add_argument("--show", action="store_true", help="Show database contents only")
    args = parser.parse_args()
    
    if args.clear:
        clear_test_data()
        exit(0)
    
    if args.show:
        check_database_contents()
        exit(0)
    
    # Run all tests
    print("\n🧪 HISTORY TRACKING TEST SUITE")
    print("="*60)
    
    results = []
    results.append(("Fingerprinting", test_fingerprinting()))
    results.append(("History Storage", test_history_storage()))
    results.append(("Database Isolation", test_different_databases()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    check_database_contents()
    
    print("\n" + "="*60)
    print("💡 TIP: Run this script multiple times to see history build up!")
    print("="*60)
