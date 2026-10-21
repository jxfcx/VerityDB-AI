
from query_engine import run_query

# Test potentially dangerous SQL statements.
test_queries = {
    "DELETE": "DELETE FROM applications;",
    "DROP TABLE": "DROP TABLE applications;",
    "UPDATE": "UPDATE applications SET status = 'Approved';",
    "Unauthorized table": "SELECT * FROM sqlite_master;",
    "Valid SELECT": "SELECT * FROM applications;"
}

for test_name, sql in test_queries.items():
    print(f"\nTesting: {test_name}")

    try:
        columns, rows = run_query(sql)
        print(f"ALLOWED: {len(rows)} rows returned")

    except Exception as error:
        print(f"BLOCKED: {error}")

