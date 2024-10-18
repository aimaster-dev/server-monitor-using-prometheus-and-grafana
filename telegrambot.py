import requests
import time

PROMETHEUS_URL = "http://localhost:9090"
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""
CPU_THRESHOLD = 80
RAM_THRESHOLD = 80
DISK_THRESHOLD = 80
CHECK_INTERVAL = 1

def get_prometheus_targets():
    url = f'{PROMETHEUS_URL}/api/v1/targets'
    response = requests.get(url)
    data = response.json()
    active_targets = [t['discoveredLabels']['__address__'] for t in data['data']['activeTargets']]
    return active_targets

def query_prometheus(query):
    url = f'{PROMETHEUS_URL}/api/v1/query'
    params = {
        'query': query
    }
    response = requests.get(url, params=params)
    result = response.json()['data']['result']
    if result:
        return float(result[0]['value'][1])
    return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.get(url, params=params)
    return response.json()

def check_server_availability(target):
    try:
        response = requests.get(f'http://{target}/metrics', timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def check_metrics():
    targets = get_prometheus_targets()
    for target in targets:
        ip_address = target.split(':')[0]  # Extract the IP address
        if not check_server_availability(target):
            message = f"Alert: Server {ip_address} is down or unreachable!"
            send_telegram_message(message)
            continue

        try:
            cpu_query = f'server_cpu_usage{{instance="{target}"}}'
            ram_query = f'server_memory_usage{{instance="{target}"}}'
            disk_query = f'server_disk_usage{{instance="{target}"}}'

            cpu_usage = query_prometheus(cpu_query)
            ram_usage = query_prometheus(ram_query)
            disk_usage = query_prometheus(disk_query)

            message = f"Server {ip_address} Status:\n"
            if cpu_usage is not None:
                message += f"CPU usage: {cpu_usage:.2f}%\n"
            if ram_usage is not None:
                message += f"RAM usage: {ram_usage:.2f}%\n"
            if disk_usage is not None:
                message += f"Disk usage: {disk_usage:.2f}%\n"

            send_telegram_message(message)

        except Exception as e:
            print(f"Error: {e}")

while True:
    check_metrics()
    time.sleep(CHECK_INTERVAL)
