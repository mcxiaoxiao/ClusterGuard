from fastapi import FastAPI, Request
import psutil
import time

app = FastAPI()

@app.get("/stats")
async def get_stats(request: Request):
    server_receive_time = time.time()
    cpu_load = psutil.cpu_percent(interval=0.5)
    memory_info = psutil.virtual_memory()

    return {
        "cpu_load": cpu_load,
        "memory_usage": memory_info.percent,
        "server_receive_time": server_receive_time
    }
