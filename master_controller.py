import os
import sys
import subprocess
import requests
import json
import html
from pymongo import MongoClient
from datetime import datetime
from colorama import Fore, Style, init

# Colorama Initialization
init(autoreset=True)

print(f"{Fore.CYAN}{'='*50}")
print(f"{Fore.CYAN}🚀 CYBER BEAST ULTIMATE ENGINE (V3 - TELEGRAM FILES)...")
print(f"{Fore.CYAN}{'='*50}\n")

# ==========================================
# 1. Configuration (Railway Environment)
# ==========================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MONGO_URI = os.getenv("MONGO_URI")

if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, MONGO_URI]):
    print(f"{Fore.RED}[!] ERROR: Environment Variables are missing!")
    sys.exit(1)

# ==========================================
# 2. Database Connection (MongoDB)
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
# 3. Telegram HTML Notifier & File Sender
# ==========================================
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"{Fore.RED}[!] Failed to send Telegram message: {e}")

def send_telegram_document(file_path, caption=""):
    """یہ نیا فنکشن ہے جو سرور سے فائل اٹھا کر آپ کو ٹیلیگرام پر بھیجے گا"""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption, "parse_mode": "HTML"}
    
    print(f"{Fore.YELLOW}[*] Uploading {file_path} to Telegram...")
    try:
        with open(file_path, "rb") as file:
            files = {"document": file}
            response = requests.post(url, data=data, files=files, timeout=30)
            if response.status_code == 200:
                print(f"{Fore.GREEN}[+] File sent successfully to Telegram!")
            else:
                print(f"{Fore.RED}[!] Telegram API Error: {response.text}")
    except Exception as e:
        print(f"{Fore.RED}[!] Failed to send document to Telegram: {e}")

# ==========================================
# 4. Live Command Runner
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
            print(f"{Fore.RED}[!] {tool_name} finished with exit code {process.returncode}")
            return False
        return True
    except Exception as e:
        print(f"{Fore.RED}[!] System Error while running {tool_name}: {e}")
        return False

# ==========================================
# 5. The Ultimate Hacking Workflow
# ==========================================
def start_scan(target_domain):
    print(f"\n{Fore.GREEN}{'='*50}")
    print(f"{Fore.GREEN}🎯 INITIATING FULL PIPELINE ON: {target_domain}")
    print(f"{Fore.GREEN}{'='*50}")
    
    send_telegram_alert(f"🔥 <b>ULTIMATE SCAN STARTED!</b>\n<b>Target:</b> <code>{html.escape(target_domain)}</code>\n<b>System:</b> 1000 CPUs Railway Pro")

    subdomains_file = f"subdomains_{target_domain}.txt"
    live_hosts_file = f"live_{target_domain}.txt"
    urls_file = f"urls_{target_domain}.txt"
    nuclei_output = f"nuclei_{target_domain}.json"
    dalfox_output = f"dalfox_{target_domain}.txt"

    # --- Step 1: Subfinder (Recon) ---
    run_tool(f"subfinder -d {target_domain} -all -o {subdomains_file}", "Subfinder")
    with open(subdomains_file, "a") as f:
        f.write(f"{target_domain}\n")
    # ٹیلیگرام پر سب ڈومینز کی فائل بھیجیں
    send_telegram_document(subdomains_file, f"🗂 <b>All Subdomains for {target_domain}</b>")

    # --- Step 2: Httpx (Live Check) ---
    if os.path.exists(subdomains_file) and os.path.getsize(subdomains_file) > 0:
        run_tool(f"httpx -l {subdomains_file} -threads 50 -rl 300 -timeout 10 -o {live_hosts_file}", "Httpx")
        # ٹیلیگرام پر لائیو ہوسٹس کی فائل بھیجیں
        send_telegram_document(live_hosts_file, f"🟢 <b>Live (Working) Hosts for {target_domain}</b>")
    else:
        return

    # --- Step 3: Nuclei (Server Bugs) ---
    if os.path.exists(live_hosts_file) and os.path.getsize(live_hosts_file) > 0:
        run_tool(f"nuclei -l {live_hosts_file} -t /root/nuclei-templates -c 50 -rl 300 -timeout 10 -mhe 3 -j -o {nuclei_output}", "Nuclei")
        # نیوکلی کی مکمل آؤٹ پٹ فائل (جس میں Info بگز بھی ہیں) بھیجیں
        send_telegram_document(nuclei_output, f"☢️ <b>Nuclei Full Scan Results for {target_domain}</b>")

    # --- Step 4: Katana (Deep Crawling) ---
    print(f"{Fore.YELLOW}[*] Deep Crawling for endpoints using Katana...")
    if os.path.exists(live_hosts_file) and os.path.getsize(live_hosts_file) > 0:
        run_tool(f"katana -list {live_hosts_file} -jc -d 3 -c 50 -rl 300 -timeout 10 -o {urls_file}", "Katana")
        send_telegram_document(urls_file, f"🕸️ <b>Crawled URLs & Parameters for {target_domain}</b>")

    # --- Step 5: DalFox (XSS Hunting) ---
    if os.path.exists(urls_file) and os.path.getsize(urls_file) > 0:
        print(f"{Fore.YELLOW}[*] Hunting for XSS using DalFox...")
        run_tool(f"dalfox file {urls_file} --skip-bav --worker 50 -o {dalfox_output}", "DalFox")
        send_telegram_document(dalfox_output, f"🦊 <b>DalFox XSS Results for {target_domain}</b>")

    # --- Step 6 & 7: Processing Important Alerts (High/Medium Bugs) ---
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

                    severity = finding.get("info", {}).get("severity", "info").upper()
                    # اب ہم صرف اہم بگز (Low, Medium, High, Critical) کے الرٹس بھیجیں گے
                    # کیونکہ Info بگز تو ویسے ہی فائل میں آ چکے ہیں
                    if severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
                        vuln_name = finding.get("info", {}).get("name", "Unknown Bug")
                        matched_url = finding.get("matched-at", "Unknown URL")
                        emoji = "🔴" if severity in ["CRITICAL", "HIGH"] else ("🟠" if severity == "MEDIUM" else "🟡")
                        msg = f"{emoji} <b>Important Bug Found!</b>\n\n📌 <b>Bug:</b> {html.escape(vuln_name)}\n⚠️ <b>Severity:</b> {severity}\n🔗 <b>URL:</b> <code>{html.escape(matched_url)}</code>"
                        send_telegram_alert(msg)
                except:
                    continue

    print(f"{Fore.GREEN}[+] Pipeline Complete for {target_domain}. Total Bugs: {bugs_found}")
    send_telegram_alert(f"✅ <b>Scan Completed for:</b> <code>{html.escape(target_domain)}</code>\n<b>Total Bugs Logged:</b> {bugs_found}")

    # --- Step 8: Clean up ---
    for f in [subdomains_file, live_hosts_file, urls_file, nuclei_output, dalfox_output]:
        if os.path.exists(f):
            os.remove(f)

# ==========================================
# 6. Target List & Execution
# ==========================================
if __name__ == "__main__":
    # یہاں میں نے کوما (,) اور لنکس کی غلطیاں درست کر دی ہیں
    targets = [
        # باؤنٹی دینے والی بڑی کمپنیاں ($$$)
        "51.89.99.105"
    ]
    
    print(f"{Fore.MAGENTA}[*] Total Targets loaded for Ultimate Hunt: {len(targets)}\n")
    
    for target in targets:
        start_scan(target)
        
    print(f"\n{Fore.GREEN}{'='*50}")
    print(f"{Fore.GREEN}🎉 ULTIMATE HUNT COMPLETED. ENGINE GOING TO SLEEP.")
    send_telegram_alert("🏁 <b>Ultimate Hunt completed successfully! Cyber Beast going to sleep.</b>")
