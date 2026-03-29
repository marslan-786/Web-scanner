import os
import sys
import subprocess
import requests
import html
from datetime import datetime
from colorama import Fore, Style, init

# Colorama Initialization
init(autoreset=True)

print(f"{Fore.CYAN}{'='*50}")
print(f"{Fore.CYAN}🎯 CYBER SNIPER (PTaaS Edition - Client Target)...")
print(f"{Fore.CYAN}{'='*50}\n")

# ==========================================
# 1. Configuration 
# ==========================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
    print(f"{Fore.RED}[!] ERROR: Telegram Environment Variables are missing!")
    sys.exit(1)

# ==========================================
# 2. Telegram HTML Notifier & File Sender
# ==========================================
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"{Fore.RED}[!] Failed to send Telegram message: {e}")

def send_telegram_document(file_path, caption=""):
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
                print(f"{Fore.GREEN}[+] File sent successfully!")
            else:
                print(f"{Fore.RED}[!] Telegram Error: {response.text}")
    except Exception as e:
        print(f"{Fore.RED}[!] Failed to send document: {e}")

# ==========================================
# 3. Live Command Runner
# ==========================================
def run_tool(command, tool_name):
    print(f"\n{Fore.CYAN}{'-'*50}")
    print(f"{Fore.MAGENTA}[*] STARTING: {tool_name.upper()}")
    print(f"{Fore.YELLOW}[>] Command: {command}")
    print(f"{Fore.CYAN}{'-'*50}")
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(f"{Fore.LIGHTBLACK_EX}[{tool_name}] {line.strip()}")
        process.wait() 
        return True
    except Exception as e:
        print(f"{Fore.RED}[!] System Error: {e}")
        return False

# ==========================================
# 4. The Sniper Workflow (For Specific Client URLs)
# ==========================================
def start_sniper_scan(target_url):
    # ٹارگٹ کے نام سے فائلز بنانے کے لیے نام کو صاف کریں
    safe_name = target_url.replace("http://", "").replace("https://", "").replace("/", "_").strip("_")
    
    print(f"\n{Fore.GREEN}{'='*50}")
    print(f"{Fore.GREEN}🎯 SNIPER LOCKED ON: {target_url}")
    print(f"{Fore.GREEN}{'='*50}")
    
    send_telegram_alert(f"🔫 <b>SNIPER SCAN STARTED!</b>\n<b>Target:</b> <code>{html.escape(target_url)}</code>\n<b>Mode:</b> Deep Client Audit")

    urls_file = f"crawled_links_{safe_name}.txt"
    nuclei_output = f"nuclei_report_{safe_name}.txt"
    dalfox_output = f"dalfox_xss_{safe_name}.txt"

    # --- Step 1: Katana (Deep Crawling the specific folder/app) ---
    print(f"{Fore.YELLOW}[*] Deep Crawling inside the specific application...")
    # -u کا مطلب ہے سیدھا URL کو ٹارگٹ کرو
    run_tool(f"katana -u {target_url} -jc -d 4 -c 50 -rl 300 -timeout 10 -o {urls_file}", "Katana")
    send_telegram_document(urls_file, f"🕸️ <b>All internal links found in {target_url}</b>")

    # --- Step 2: Nuclei (Server & Misconfig Bugs - TEXT OUTPUT) ---
    print(f"{Fore.YELLOW}[*] Running complete security audit...")
    # -u استعمال کیا ہے تاکہ سیدھا لنک ہٹ ہو، اور -o میں .txt فائل دی ہے
    run_tool(f"nuclei -u {target_url} -t /root/nuclei-templates -c 50 -rl 300 -timeout 10 -o {nuclei_output}", "Nuclei")
    send_telegram_document(nuclei_output, f"☢️ <b>Nuclei Full Audit Report (TXT) for {target_url}</b>\n\nاس فائل میں تمام بگز کی تفصیل اور شدت (Severity) درج ہے۔")

    # --- Step 3: DalFox (XSS Hunting on the crawled links) ---
    if os.path.exists(urls_file) and os.path.getsize(urls_file) > 0:
        print(f"{Fore.YELLOW}[*] Hunting for XSS using DalFox...")
        run_tool(f"dalfox file {urls_file} --skip-bav --worker 50 -o {dalfox_output}", "DalFox")
        send_telegram_document(dalfox_output, f"🦊 <b>DalFox XSS Vulnerabilities for {target_url}</b>")

    # --- Step 4: Quick Summary Alert (Reading from TXT) ---
    bugs_count = 0
    if os.path.exists(nuclei_output):
        with open(nuclei_output, 'r') as file:
            for line in file:
                if "[critical]" in line or "[high]" in line or "[medium]" in line or "[low]" in line:
                    bugs_count += 1
                    send_telegram_alert(f"⚠️ <b>Bug Found!</b>\n<code>{html.escape(line.strip())}</code>")

    print(f"{Fore.GREEN}[+] Sniper Scan Complete. Total Issues: {bugs_count}")
    send_telegram_alert(f"✅ <b>Sniper Audit Completed!</b>\n<b>Target:</b> <code>{html.escape(target_url)}</code>\n<b>Important Issues Found:</b> {bugs_count}\n\n<i>پوری تفصیل کے لیے اوپر دی گئی .txt فائلز ڈاؤن لوڈ کریں۔</i>")

    # --- Step 5: Clean up ---
    for f in [urls_file, nuclei_output, dalfox_output]:
        if os.path.exists(f):
            os.remove(f)

# ==========================================
# 5. Execution
# ==========================================
if __name__ == "__main__":
    # یہاں آپ کلائنٹ کا دیا ہوا پورا لنک ڈالیں گے
    client_targets = [
        "http://51.89.99.105/NumberPanel/",
        # "https://example-client.com/login/"
    ]
    
    for target in client_targets:
        start_sniper_scan(target)
        
    print(f"\n{Fore.GREEN}🎉 ALL CLIENT AUDITS COMPLETED.")
