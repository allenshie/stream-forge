# scripts/start_servers.sh
#!/bin/bash

# 啟動 Redis Docker container
echo "Starting Redis container..."
docker run -d \
    --rm \
    -p 6379:6379 \
    redis:latest

# 啟動 MediaMTX Docker container
echo "Starting MediaMTX container..."
docker run -d \
    --rm \
    --network=host \
    bluenviron/mediamtx:latest

echo "All servers started successfully!"