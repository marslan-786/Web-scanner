# ہائی پرفارمنس کے لیے گولینگ کا لیٹسٹ ورژن (1.25)
FROM golang:1.25-bullseye

# 1. تمام ضروری سسٹم ٹولز اور لینگویجز انسٹال کرنا
RUN apt-get update && apt-get install -y \
    python3 python3-pip git curl wget nmap masscan \
    libpcap-dev jq chromium-driver ruby-full \
    dirb gobuster dnsutils \
    && rm -rf /var/lib/apt/lists/*

# 2. ورڈپریس اسکینر (WPScan)
RUN gem install wpscan

# 3. --- PROJECT DISCOVERY TOOLS (The Gold Standard) ---
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
RUN go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
RUN go install -v github.com/projectdiscovery/katana/cmd/katana@latest
RUN go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

# 4. --- ADVANCED EXPLOITATION & RECON TOOLS ---
RUN go install -v github.com/OWASP/Amass/v3/...@master
RUN go install -v github.com/ffuf/ffuf/v2@latest
RUN go install -v github.com/tomnomnom/waybackurls@latest
RUN go install -v github.com/tomnomnom/assetfinder@latest
RUN go install -v github.com/lc/gau/v2/cmd/gau@latest
RUN go install -v github.com/hahwul/dalfox/v2@latest

# 5. --- PYTHON HACKING LIBRARIES (SQLMap, TruffleHog, Arjun) ---
RUN git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap
RUN pip3 install trufflehog arjun

# 6. --- THE MISSING GEMS (XSStrike, SecretFinder, CORScanner) ---
# XSStrike
RUN git clone https://github.com/s0md3v/XSStrike.git /opt/XSStrike && \
    cd /opt/XSStrike && pip3 install -r requirements.txt
# SecretFinder
RUN git clone https://github.com/m4ll0k/SecretFinder.git /opt/SecretFinder && \
    cd /opt/SecretFinder && pip3 install -r requirements.txt
# CORScanner
RUN pip3 install corscanner

# 7. Nuclei کی تمام 5000+ ٹیمپلیٹس اپڈیٹ کرنا
RUN nuclei -update-templates

# ورکنگ ڈائریکٹری سیٹ کرنا
# (ڈوکر فائل کا باقی اوپر والا حصہ ویسا ہی رہے گا...)

# ورکنگ ڈائریکٹری سیٹ کرنا
WORKDIR /app

# 8. پائتھن کی ضروری لائبریریز انسٹال کرنا (requirements.txt کے ذریعے)
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# آپ کا ماسٹر کنٹرولر یہاں کاپی ہوگا
COPY . .

# جب کنٹینر چلے گا تو یہ کمانڈ رن ہوگی
CMD ["python3", "master_controller.py"]