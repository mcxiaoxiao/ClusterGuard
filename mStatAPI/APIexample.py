import requests
import time

# This is an example of accessing the mStatAPI, which can be deployed on your pc/web/dashboard/... for monitoring purposes.

def get_server_stats(ip):
    url = f"http://{ip}:8899/stats"
    try:
        client_send_time = time.time()
        response = requests.get(url, timeout=5)  # Set timeout to 5 seconds
        response.raise_for_status()
        client_receive_time = time.time()
        stats = response.json()
        server_receive_time = stats.get('server_receive_time', client_send_time)
        
        # Calculate latency
        latency = int((server_receive_time - client_send_time) * 1000)  # Convert to milliseconds and remove decimals

        # Return statistics
        return {
            "cpu_load": stats.get('cpu_load', 'N/A'),
            "memory_usage": stats.get('memory_usage', 'N/A'),
            "latency": latency,
            "status": "active"
        }
    except requests.exceptions.Timeout:
        return {
            "status": "inactive"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": str(e)
        }

if __name__ == "__main__":
    ip_address = "206.237.30.47"
    stats = get_server_stats(ip_address)
    print(stats)
