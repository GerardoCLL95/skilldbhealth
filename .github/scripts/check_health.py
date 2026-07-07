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
            
        # Write to GitHub Actions Job Summary if running in GitHub Actions
        summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary_file:
            try:
                with open(summary_file, "a", encoding="utf-8") as sf:
                    sf.write("### 📊 Database Health Summary\n\n")
                    sf.write("| Database Name | DB Type | Status | Active Status |\n")
                    sf.write("| :--- | :---: | :---: | :---: |\n")
                    for db in data:
                        name = db.get("nombre", "Unknown")
                        tipo = db.get("tipo_db", "N/A")
                        raw_status = db.get("status", "UNKNOWN").upper()
                        
                        if raw_status == "OK":
                            status_str = "🟢 OK"
                        elif raw_status in ("WARNING", "WARN"):
                            status_str = "🟡 WARNING"
                        elif raw_status == "CRITICAL":
                            status_str = "🔴 CRITICAL"
                        else:
                            status_str = "⚪ UNKNOWN"
                            
                        active_str = "✔️ Active" if db.get("activa", True) else "❌ Inactive"
                        sf.write(f"| **{name}** | `{tipo}` | {status_str} | {active_str} |\n")
                    
                    sf.write("\n#### Statistics:\n")
                    sf.write(f"- **Total Configured**: {total_dbs}\n")
                    sf.write(f"- **Healthy (OK)**: {healthy_dbs_count}\n")
                    sf.write(f"- **Unhealthy/Unknown**: {len(unhealthy_dbs)}\n")
                    sf.write(f"- **Inactive**: {inactive_dbs_count}\n\n")
                    
                    if unhealthy_dbs:
                        sf.write("> ⚠️ **Warning**: Found active databases with non-OK status.\n")
                    else:
                        sf.write("> 🎉 **All active databases are healthy!**\n")
            except Exception as se_err:
                print(f"Error writing to GITHUB_STEP_SUMMARY: {se_err}")

        sys.exit(0)
except Exception as e:
    print(f"Error connecting to database health API: {e}")
    sys.exit(1)
