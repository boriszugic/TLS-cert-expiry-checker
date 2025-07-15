import ssl
import socket
import yaml
import sys
import json
import concurrent.futures
from datetime import datetime
from collections import defaultdict

DEFAULT_TIMEOUT = 5

def get_cert_expiry(host, port, timeout):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                expiry_str = cert['notAfter']
                expiry_date = datetime.strptime(expiry_str, '%b %d %H:%M:%S %Y %Z')
                days_left = (expiry_date - datetime.utcnow()).days
                return {
                    "host": host,
                    "port": port,
                    "expiry_date": expiry_date.isoformat(),
                    "days_left": days_left,
                    "status": categorize(days_left)
                }
    except Exception as e:
        return {
            "host": host,
            "port": port,
            "error": str(e),
            "status": "UNREACHABLE"
        }

def categorize(days_left):
    if days_left <= 7:
        return "CRITICAL"
    elif days_left <= 30:
        return "WARNING"
    else:
        return "OK"

def load_config(path='endpoints.yaml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)['endpoints']

def print_report(results):
    grouped = defaultdict(list)
    for r in results:
        grouped[r['status']].append(r)

    print(f"Certificate Expiry Report - {datetime.utcnow().date()}")
    print("="*40)

    for status, emoji in [("CRITICAL", "🔴"), ("WARNING", "🟡"), ("OK", "🟢"), ("UNREACHABLE", "❌")]:
        if grouped[status]:
            print(f"{emoji} {status}:")
            for r in grouped[status]:
                if status == "UNREACHABLE":
                    print(f"  └─ {r['host']}:{r['port']} → Error: {r['error']}")
                else:
                    print(f"  └─ {r['host']}:{r['port']} → Expires in {r['days_left']} days ({r['expiry_date']})")
            print()

    print(f"SUMMARY: {len(grouped['CRITICAL'])} critical, {len(grouped['WARNING'])} warning, {len(grouped['OK'])} healthy, {len(grouped['UNREACHABLE'])} unreachable")
    return grouped

def exit_code(grouped):
    if grouped['CRITICAL']:
        return 2
    elif grouped['WARNING']:
        return 1
    else:
        return 0

def main():
    
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'endpoints.yaml'
    endpoints = load_config(config_file)
    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for ep in endpoints:
            host = ep['host']
            port = ep.get('port', 443)
            timeout = ep.get('timeout', DEFAULT_TIMEOUT)
            futures.append(executor.submit(get_cert_expiry, host, port, timeout))

        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    grouped = print_report(results)

    # JSON output
    with open('cert_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    sys.exit(exit_code(grouped))

if __name__ == '__main__':
    main()

