# scripts/stop_servers.sh
#!/bin/bash

# 停止 MediaMTX Docker container
echo "Stopping MediaMTX container..."
docker stop $(docker ps -q --filter ancestor=bluenviron/mediamtx:latest)

# 停止 Redis Docker container
echo "Stopping Redis container..."
docker stop $(docker ps -q --filter ancestor=redis:latest)

echo "All servers stopped successfully!"