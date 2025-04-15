import psutil
import time
import csv
import sys
from datetime import datetime

if len(sys.argv) < 2:
    print("Usage: python external_logger.py <PID>")
    sys.exit(1)

pid = int(sys.argv[1])
process = psutil.Process(pid)

output_file = f"resource_usage_{pid}.csv"
interval = 0.1  # 100ms

with open(output_file, mode="w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "memory_MB", "cpu_percent"])

    try:
        while True:
            timestamp = datetime.now().isoformat()
            mem = process.memory_info().rss / 1024 / 1024
            cpu = process.cpu_percent(interval=interval)
            writer.writerow([timestamp, f"{mem:.2f}", f"{cpu:.2f}"])
    except (KeyboardInterrupt, psutil.NoSuchProcess):
        print("Monitoring stopped or target process exited.")
