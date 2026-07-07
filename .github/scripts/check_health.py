import urllib.request
import json
import os
import sys

token = os.environ.get("DB_HEALTH_TOKEN")
if not token:
    print("Error: DB_HEALTH_TOKEN secret is not configured in the repository.")
    sys.exit(1)

url = "http://38.250.116.71:5000/api/datasources"
req = urllib.request.Request(url)
req.add_header("Authorization", f"Bearer {token}")

try:
    print(f"Connecting to {url}...")
    with urllib.request.urlopen(req, timeout=15) as response:
        if response.status != 200:
            print(f"Error: API returned status code {response.status}")
            sys.exit(1)
        data = json.loads(response.read().decode())
        
        total_dbs = len(data)
        healthy_dbs_count = sum(1 for db in data if db.get("status") == "OK" and db.get("activa", True))
        unhealthy_dbs = [db for db in data if db.get("activa", True) and db.get("status") != "OK"]
        inactive_dbs_count = sum(1 for db in data if not db.get("activa", True))
        
        print("\n========================================")
        print("         DATABASE HEALTH SUMMARY")
        print("========================================")
        print(f"Total Configured : {total_dbs}")
        print(f"Healthy (OK)     : {healthy_dbs_count}")
        print(f"Unhealthy/Unk    : {len(unhealthy_dbs)}")
        print(f"Inactive         : {inactive_dbs_count}")
        print("----------------------------------------")
        print("Database Details:")
        
        for db in data:
            name = db.get("nombre", "Unknown")
            status = db.get("status", "UNKNOWN").upper()
            tipo = db.get("tipo_db", "N/A")
            active = "Active" if db.get("activa", True) else "Inactive"
            print(f" [{status}] {name} ({tipo}) - {active}")
            
        print("========================================\n")
        
        if unhealthy_dbs:
            print(f"Warning: Found {len(unhealthy_dbs)} unhealthy/unknown database(s) in active state.")
        else:
            print("All active databases are healthy.")
            
        sys.exit(0)
except Exception as e:
    print(f"Error connecting to database health API: {e}")
    sys.exit(1)
