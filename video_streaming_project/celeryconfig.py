from kombu import Queue

# Broker settings
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

# 修復警告
broker_connection_retry_on_startup = True

# 任務設置
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Taipei'
enable_utc = True

# Worker 設置
worker_concurrency = 4  # 根據你的 CPU 核心數調整
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000

# 日誌設置
worker_redirect_stdouts = False
worker_redirect_stdouts_level = 'INFO'

# 任務佇列設置
task_queues = (
    Queue('default', routing_key='default'),
    Queue('video_tasks', routing_key='video.#'),
)

task_routes = {
    'streaming.tasks.start_stream': {'queue': 'video_tasks'},
    'streaming.tasks.stop_stream': {'queue': 'video_tasks'},
}