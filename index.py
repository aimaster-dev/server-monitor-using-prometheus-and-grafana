from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

PROMETHEUS_URL = "http://localhost:9090"

def get_prometheus_targets():
    url = f'{PROMETHEUS_URL}/api/v1/targets'
    response = requests.get(url)
    data = response.json()
    active_targets = [t['discoveredLabels']['__address__'] for t in data['data']['activeTargets']]
    return active_targets

def query_prometheus(query):
    url = f"{PROMETHEUS_URL}/api/v1/query"
    params = {
        'query': query
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

@app.route('/api/status/cpu', methods=['GET'])
def get_cpu_status():
    data = []
    targets = get_prometheus_targets()
    for target in targets:
        query = f'server_cpu_usage{{instance="{target}"}}'
        result = query_prometheus(query)
        if result['data']['result']:
            value = result['data']['result'][0]['value'][1]
            data.append({target: float(value)})
    return jsonify(data)

@app.route('/api/status/ram', methods=['GET'])
def get_ram_status():
    data = []
    targets = get_prometheus_targets()
    for target in targets:
        query = f'server_memory_usage{{instance="{target}"}}'
        result = query_prometheus(query)
        if result['data']['result']:
            value = result['data']['result'][0]['value'][1]
            data.append({target: float(value)})
    return jsonify(data)

@app.route('/api/status/disk', methods=['GET'])
def get_disk_status():
    data = []
    targets = get_prometheus_targets()
    for target in targets:
        query = f'server_disk_usage{{instance="{target}"}}'
        result = query_prometheus(query)
        if result['data']['result']:
            value = result['data']['result'][0]['value'][1]
            data.append({target: float(value)})
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
