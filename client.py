from prometheus_client import start_http_server, Gauge, Counter
import psutil
import time

cpu_usage = Gauge('server_cpu_usage', 'CPU usage in percentage')
memory_usage = Gauge('server_memory_usage', 'Memory usage in percentage')
disk_usage = Gauge('server_disk_usage', 'Disk usage in percentage')
network_sent = Counter('server_network_sent_bytes', 'Total bytes sent over network')
network_received = Counter('server_network_received_bytes', 'Total bytes received over network')

def collect_metrics():
    cpu_usage.set(psutil.cpu_percent(interval=1))
    memory = psutil.virtual_memory()
    memory_usage.set(memory.percent)
    disk = psutil.disk_usage('/')
    disk_usage.set(disk.percent)

if __name__ == '__main__':
    start_http_server(7000)
    print("Serving metrics on http://localhost:7000")

    while(True):
        collect_metrics()
        time.sleep(5)