# mStatAPI

`mStatAPI` is a simple application that provides system statistics such as CPU load and memory usage. It uses the `psutil` library to gather system information.

## Features

- Retrieve CPU load percentage
- Retrieve memory usage percentage
- Record server request receive time

## Installation

1. **Download the latest release:**

    Use the following command to download the main.py file:

    ```bash
    mkdir mStatAPI
    cd mStatAPI
    wget https://github.com/mcxiaoxiao/mStatAPI/releases/download/serverkit/main.py
    ```

3. **Install required packages:**

   Make sure you have Python 3.7+ installed. Then, install the necessary packages using pip:

   ```bash
    pip install fastapi uvicorn psutil
   ```

## Running the Application

To start the FastAPI application, run:

```bash
uvicorn main:app --host 0.0.0.0 --port 8899
```

This will start the server on `http://localhost:8899`.

## Setting Up Auto-Start

To ensure the application starts automatically on boot, you can create a systemd service:

1. **Create a systemd service file:**

   ```bash
   sudo nano /etc/systemd/system/mstatapi.service
   ```

2. **Add the following content:**

   ```ini
   [Unit]
   Description=mStatAPI Service
   After=network.target

   [Service]
   ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8899
   WorkingDirectory=/mStatAPI
   Restart=always
   User=root
   Group=root

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service:**

   ```bash
   sudo systemctl enable mstatapi
   sudo systemctl start mstatapi
   ```

## Checking the Status

To check the status of your FastAPI application, use:

```bash
sudo systemctl status mstatapi
```

## Firewall Configuration

To allow external access to the API, ensure the firewall allows traffic on port 8899:

ufw：
```bash
sudo ufw allow 8899
```
firewalld：
```bash
sudo firewall-cmd --permanent --add-port=8899/tcp
sudo firewall-cmd --reload
```
iptables：
```bash
sudo iptables -A INPUT -p tcp --dport 8899 -j ACCEPT
```

## API Endpoint

- **GET /stats**: Returns CPU load, memory usage, and server receive time.

Example response:

```json
{
  "cpu_load": 23.5,
  "memory_usage": 57.8,
  "server_receive_time": 1634567890.123
}
```
