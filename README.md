# 🔐 TLS Certificate Expiry Checker

This is a lightweight CLI tool that checks the TLS certificate expiry dates of endpoints defined in a YAML config file. It helps you catch certificates before they expire.

---

## 🧠 Why?

TLS certificates are easy to forget - until they expire and everything breaks.

This tool connects to your configured endpoints, retrieves their certificates, and tells you how many days are left before they expire. It flags critical and warning thresholds, and outputs results in both human-readable and JSON formats. Perfect for cron jobs, pipelines, and CI alerts.

---

## 💻 How It Works

1. Create a config file (default: endpoints.yaml) listing all services you want to monitor. Here is an example config:
```yaml
endpoints:
  - name: "LinkedIn"
    host: "linkedin.com"
    port: 443
  - name: "Google"
    host: "google.com"
    port: 443
  - name: "Doesn't exist"
    host: "notexisting.com"
    port: 8443
    timeout: 10
````

2. Run the Tool: `python main.py [config.yaml]`
   
3. Get Output in Two Formats

**Human-readable console output:**
<img width="850" height="323" alt="image" src="https://github.com/user-attachments/assets/e23ed887-26d4-43bb-816b-5340338a58d5" />

**Structured JSON output (cert_report.json):**
<img width="562" height="656" alt="image" src="https://github.com/user-attachments/assets/c5d920dc-4fd8-4b41-8988-9df623346c24" />
---
