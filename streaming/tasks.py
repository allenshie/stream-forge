from celery import shared_task
import subprocess
import signal
import os
import uuid
from django.conf import settings

@shared_task
def start_stream(video_id):
    """
    啟動影片串流任務
    使用 ffmpeg 將影片推送到 MediaMTX 服務器
    """
    from .models import VideoStream
    video = VideoStream.objects.get(id=video_id)
    
    # 生成串流 URL
    rtsp_url = video.get_rtsp_url()
    
    # 構建 ffmpeg 命令
    command = [
        'ffmpeg',
        '-re',                    # 以本地幀率讀取
        '-fflags', '+genpts',     # 生成顯示時間戳
        '-stream_loop', '-1',     # 循環播放
        '-i', video.file_path,    # 輸入文件
        '-c:v', 'copy',           # 視頻編碼複製
        '-c:a', 'copy',           # 音頻編碼複製
        '-bsf:v', 'h264_mp4toannexb',  # h264 bitstream 過濾
        '-f', 'rtsp',             # RTSP 格式輸出
        '-rtsp_transport', 'tcp', # 使用 TCP 傳輸
        rtsp_url
    ]
    
    # 啟動串流進程
    process = subprocess.Popen(command)
    
    # 保存進程 ID
    with open(f'/tmp/stream_{video_id}.pid', 'w') as f:
        f.write(str(process.pid))
    
    # 更新視頻狀態
    video.status = 'PLAYING'
    video.save()
    
    return True

@shared_task
def stop_stream(video_id):
    """
    停止影片串流任務
    關閉 ffmpeg 進程
    """
    from .models import VideoStream
    
    # 停止串流進程
    try:
        with open(f'/tmp/stream_{video_id}.pid', 'r') as f:
            pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)
            os.remove(f'/tmp/stream_{video_id}.pid')
    except (FileNotFoundError, ProcessLookupError):
        pass
    
    # 更新視頻狀態
    try:
        video = VideoStream.objects.get(id=video_id)
        video.status = 'STOPPED'
        video.save()
    except VideoStream.DoesNotExist:
        pass
    
    return True