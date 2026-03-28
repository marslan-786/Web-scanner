import os
import sys
import subprocess
import requests
import json
from pymongo import MongoClient
from datetime import datetime
from colorama import Fore, Style, init

# Colorama کو انیشلائز کرنا تاکہ کنسول پر رنگین آؤٹ پٹ آئے
init(autoreset=True)

print(f"{Fore.CYAN}{'='*50}")
print(f"{Fore.CYAN}🚀 CYBER BEAST ENGINE INITIALIZING... (Railway Pro)")
print(f"{Fore.CYAN}{'='*50}\n")

# ==========================================
# 1. کنفیگریشن (Railway Environment Variables)
# ==========================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MONGO_URI = os.getenv("MONGO_URI")

if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MONGO_URI]):
    print(f"{Fore.RED}[!] ERROR: Environment Variables are missing!")
    print(f"{Fore.RED}[!] Please set TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, and MONGO_URI in Railway.")
    sys.exit(1)
else:
    print(f"{Fore.GREEN}[+] Environment Variables Loaded Successfully.")

# ==========================================
# 2. ڈیٹا بیس کنکشن (MongoDB)
# ==========================================
print(f"{Fore.YELLOW}[*] Connecting to MongoDB...")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["CyberBeastDB"]
    vuln_collection = db["Vulnerabilities"]
    client.server_info()
    print(f"{Fore.GREEN}[+] MongoDB Connected Successfully!\n")
except Exception as e:
    print(f"{Fore.RED}[!] MongoDB Connection Error: {e}")
    sys.exit(1)

# ==========================================
# 3. ٹیلیگرام نوٹیفکیشن فنکشن
# ==========================================
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"{Fore.RED}[!] Telegram API Error: {response.text}")
    except Exception as e:
        print(f"{Fore.RED}[!] Failed to send Telegram message: {e}")

# ==========================================
# 4. لائیو کمانڈ رنر (Real-time Printing)
# ==========================================
def run_tool(command, tool_name):
    print(f"\n{Fore.CYAN}{'-'*50}")
    print(f"{Fore.MAGENTA}[*] STARTING MODULE: {tool_name.upper()}")
    print(f"{Fore.YELLOW}[>] Command: {command}")
    print(f"{Fore.CYAN}{'-'*50}")

    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in process.stdout:
            print(f"{Fore.LIGHTBLACK_EX}[{tool_name}] {line.strip()}")
            
        process.wait() 
        
        if process.returncode != 0:
            error_msg = f"⚠️ *Module Error!*\nTool: `{tool_name}` exited with code {process.returncode}."
            print(f"{Fore.RED}[!] {tool_name} finished with exit code {process.returncode}")
            return False
        else:
            print(f"{Fore.GREEN}[+] {tool_name} COMPLETED SUCCESSFULLY.")
            return True

    except Exception as e:
        print(f"{Fore.RED}[!] System Error while running {tool_name}: {e}")
        return False

# ==========================================
# 5. مین ہیکنگ ورک فلو (The Engine)
# ==========================================
def start_scan(target_domain):
    print(f"\n{Fore.GREEN}{'='*50}")
    print(f"{Fore.GREEN}🎯 INITIATING SCAN ON: {target_domain}")
    print(f"{Fore.GREEN}{'='*50}")
    
    send_telegram_alert(f"🔥 *Scan Started!*\n*Target:* `{target_domain}`\n*System:* Railway Pro Engine")

    subdomains_file = f"subdomains_{target_domain}.txt"
    live_hosts_file = f"live_{target_domain}.txt"
    nuclei_output = f"nuclei_{target_domain}.json"

    # --- Step 1: Subfinder ---
    run_tool(f"subfinder -d {target_domain} -all -o {subdomains_file}", "Subfinder")

    # 👇 [FIX] مین ٹارگٹ کو خود فائل میں ڈالنا تاکہ اسکین کبھی نہ رکے
    print(f"{Fore.YELLOW}[*] Injecting main target '{target_domain}' into the list to ensure scanning continues...")
    with open(subdomains_file, "a") as f:
        f.write(f"{target_domain}\n")

    # --- Step 2: Httpx ---
    if os.path.exists(subdomains_file) and os.path.getsize(subdomains_file) > 0:
        run_tool(f"httpx -l {subdomains_file} -threads 200 -o {live_hosts_file}", "Httpx")
    else:
        print(f"{Fore.RED}[!] No subdomains found and injection failed. Skipping Httpx.")
        return

    # --- Step 3: Nuclei ---
    if os.path.exists(live_hosts_file) and os.path.getsize(live_hosts_file) > 0:
        run_tool(f"nuclei -l {live_hosts_file} -t /root/nuclei-templates -j -o {nuclei_output}", "Nuclei")
    else:
        print(f"{Fore.RED}[!] No live hosts found. Skipping Nuclei.")

    # --- Step 4: Results Processing ---
    print(f"\n{Fore.YELLOW}[*] Processing Results and Saving to MongoDB...")
    bugs_found = 0
    if os.path.exists(nuclei_output):
        with open(nuclei_output, 'r') as file:
            for line in file:
                try:
                    finding = json.loads(line.strip())
                    
                    finding["scan_date"] = datetime.now()
                    finding["target_domain"] = target_domain
                    vuln_collection.insert_one(finding)
                    bugs_found += 1

                    vuln_name = finding.get("info", {}).get("name", "Unknown Bug")
                    severity = finding.get("info", {}).get("severity", "info").upper()
                    matched_url = finding.get("matched-at", "Unknown URL")
                    
                    emoji = "🔴" if severity in ["CRITICAL", "HIGH"] else ("🟠" if severity == "MEDIUM" else ("🟡" if severity == "LOW" else "🔵"))
                    
                    msg = f"{emoji} *New Vulnerability Found!*\n\n📌 *Bug:* {vuln_name}\n⚠️ *Severity:* {severity}\n🔗 *URL:* `{matched_url}`"
                    send_telegram_alert(msg)

                except json.JSONDecodeError:
                    continue

    print(f"{Fore.GREEN}[+] Scan Complete for {target_domain}. Total Bugs: {bugs_found}")
    send_telegram_alert(f"✅ *Scan Completed for:* `{target_domain}`\n*Total Bugs Logged:* {bugs_found}")

    # --- Step 5: Clean up ---
    print(f"{Fore.YELLOW}[*] Cleaning up temporary files...")
    for f in [subdomains_file, live_hosts_file, nuclei_output]:
        if os.path.exists(f):
            os.remove(f)
            print(f"{Fore.LIGHTBLACK_EX} Deleted: {f}")
    
    print(f"{Fore.GREEN}[+] Cleanup Done. Engine is ready for next target.")

# ==========================================
# 6. Execution Entry Point (Multi-Target Loop)
# ==========================================
if __name__ == "__main__":
    # یہاں ہم نے 3 بہترین ٹیسٹنگ ویب سائٹس ڈال دی ہیں
    targets = [
        "vulnweb.com",         # اس کے بہت سے سب ڈومینز ہیں
        "brokencrystals.com",  # API بگز کے لیے
        "demo.testfire.net"    # فنانشل ایپس کے بگز کے لیے
    ]
    
    print(f"{Fore.MAGENTA}[*] Total Targets loaded: {len(targets)}\n")
    
    for target in targets:
        start_scan(target)
        
    print(f"\n{Fore.GREEN}{'='*50}")
    print(f"{Fore.GREEN}🎉 ALL TARGETS SCANNED SUCCESSFULLY. ENGINE GOING TO SLEEP.")
    send_telegram_alert("🏁 *All scans completed successfully! Cyber Beast going to sleep.*")
