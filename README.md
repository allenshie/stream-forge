# Stream Forge Project

# Video Streaming Service

這是一個基於 Django 的視頻串流服務系統，允許用戶上傳視頻文件並通過 RTSP 協議進行串流播放。

## 功能特點

- 視頻文件管理和上傳
- RTSP 串流服務
- 支持視頻串流的開始/停止控制
- 自動生成唯一的串流路徑
- 視頻狀態監控
- 支持多種視頻格式（MP4、AVI、MKV）

## 系統要求

- Python 3.12+
- Docker
- FFmpeg
- Redis (Docker)
- MediaMTX (Docker)

## 安裝步驟

1. 克隆專案
```bash
git clone https://github.com/your-username/stream-forge.git
cd stream-forge
```

2. 創建並啟動 Conda 環境
```bash
conda create -n streaming python=3.12
conda activate streaming
```

3. 安裝依賴
```bash
pip install -r requirements.txt
```

4. 執行數據庫遷移
```bash
python manage.py makemigrations
python manage.py migrate
```

## 啟動服務

1. 啟動主服務（包含 Redis、MediaMTX 和 Django）
```bash
python manage.py runserver_with_services
```
這個命令會：
- 啟動 Redis 容器
- 啟動 MediaMTX 容器
- 啟動 Django 開發服務器

當你按下 `Ctrl+C` 關閉 Django 服務器時，系統會：
- 自動停止 Redis 容器
- 自動停止 MediaMTX 容器

2. 啟動 Celery Worker（在獨立的終端中）
```bash
celery -A video_streaming_project worker -l info
```

## 使用說明

管理串流
- 訪問 `http://localhost:8000/streaming/`
- 可以查看所有已上傳的視頻
- 使用控制按鈕開始/停止串流
- 查看 RTSP URL

## 目錄結構
```
├── db.sqlite3
├── manage.py
├── media
│   └── videos
├── README.md
├── requirements.txt
├── scripts
│   ├── start_servers.sh
│   └── stop_servers.sh
├── streaming
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── management
│   │   ├── commands
│   │   │   ├── __init__.py
│   │   │   ├── runserver_with_services.py
│   │   │   └── stopservices.py
│   │   └── __init__.py
│   ├── migrations
│   │   └── __init__.py  
│   ├── models.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates
│   ├── base.html
│   └── streaming
│       ├── register.html
│       └── video_list.html
└── video_streaming_project
    ├── asgi.py
    ├── celeryconfig.py
    ├── celery.py
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py

```

## 停止服務

1. 停止主服務
   - 在運行 Django 服務器的終端中按 `Ctrl+C`
   - 這將自動停止 Redis 和 MediaMTX 容器

2. 停止 Celery Worker
   - 在運行 Celery 的終端中按 `Ctrl+C`
   - 或使用命令：`pkill -f "celery worker"`

## 常見問題

1. Redis 連接問題
   - 確保 Docker 服務正在運行
   - 檢查端口 6379 是否可用

2. 串流無法播放
   - 確保 MediaMTX 服務正在運行
   - 檢查防火牆設置
   - 確認 RTSP URL 是否正確

3. Celery 任務問題排查
   - 觀察 Celery 終端輸出，正常啟動時會顯示：
     ```
     [tasks]
       . streaming.tasks.start_stream
       . streaming.tasks.stop_stream
     ...
     celery@hostname ready.
     ```
   - 當任務被觸發時，終端會顯示任務執行狀態和結果
   - 如果出現錯誤，錯誤信息會直接顯示在終端中
   - 確保 Redis 連接正常（終端會顯示 "Connected to redis://localhost:6379/0"）

## 技術棧

- Django
- Celery
- Redis (Docker)
- Docker
- MediaMTX (Docker)
- FFmpeg

## 注意事項

- 確保系統已安裝 FFmpeg
- 確保 Docker 服務正在運行
- 確保所需的端口（8000, 6379, 8554）未被占用
- 生產環境部署時建議配置 SSL/TLS
- 注意視頻文件的存儲空間管理

