from django.db import models
from django.conf import settings
import os
from datetime import datetime

def video_upload_path(instance, filename):
    """生成上傳文件的保存路徑"""
    # 根據日期生成子目錄
    today = datetime.now().strftime('%Y%m%d')
    # 生成文件保存路徑: MEDIA_ROOT/videos/YYYYMMDD/filename
    return os.path.join('videos', today, filename)

class VideoStream(models.Model):
    STATUS_CHOICES = [
        ('STOPPED', '已停止'),
        ('PLAYING', '播放中'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='影片名稱')
    video_file = models.FileField(
        upload_to=video_upload_path,
        verbose_name='影片檔案',
        help_text='支援的格式：MP4, AVI, MKV',
    )
    file_path = models.CharField(
        max_length=255, 
        verbose_name='檔案路徑',
        editable=False  # 不允許直接編輯
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES,
        default='STOPPED',
        verbose_name='狀態'
    )
    stream_path = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name='串流路徑'
    )
    rtsp_url = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name='串流網址'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='建立時間'
    )
    file_size = models.BigIntegerField(
        verbose_name='檔案大小(bytes)',
        editable=False,
        null=True
    )
    duration = models.FloatField(
        verbose_name='影片長度(秒)',
        editable=False,
        null=True
    )
    def save(self, *args, **kwargs):
        if self.video_file:
            # 先調用 super().save() 確保文件被保存
            super().save(*args, **kwargs)
            
            # 獲取實際的檔案路徑
            file_path = os.path.join(settings.MEDIA_ROOT, self.video_file.name)
            self.file_path = file_path
            
            # 如果是新文件，獲取文件大小
            if not self.file_size:
                self.file_size = self.video_file.size
                
            # 如果是新文件，獲取視頻時長
            if not self.duration and os.path.exists(file_path):
                self.duration = self.get_video_duration()
            
            # 再次保存以更新 file_path
            super().save(update_fields=['file_path', 'file_size', 'duration'])
        else:
            super().save(*args, **kwargs)

    def get_video_duration(self):
        """獲取視頻時長"""
        try:
            import ffmpeg
            probe = ffmpeg.probe(self.file_path)  # 使用完整路徑
            duration = float(probe['streams'][0]['duration'])
            return duration
        except Exception as e:
            print(f"Error getting duration: {e}")
            return None
    def delete(self, *args, **kwargs):
        try:
            # 先嘗試刪除媒體文件
            if self.video_file:
                # 檢查文件是否存在
                if os.path.exists(self.file_path):
                    os.remove(self.file_path)
                    
                # 檢查並刪除空的日期目錄
                directory = os.path.dirname(self.file_path)
                if os.path.exists(directory) and not os.listdir(directory):
                    os.rmdir(directory)
                    
            # 如果有 PID 文件，也需要清理
            pid_file = f'/tmp/stream_{self.id}.pid'
            if os.path.exists(pid_file):
                os.remove(pid_file)
                
        except Exception as e:
            print(f"Error deleting files: {e}")
            
        # 最後刪除數據庫記錄
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = '影片串流'
        verbose_name_plural = '影片串流'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_rtsp_url(self):
        """獲取完整的 RTSP URL"""
        from django.conf import settings
        if not self.rtsp_url:
            self.rtsp_url = f"rtsp://{settings.MEDIAMTX_HOST}:{settings.MEDIAMTX_PORT}/{self.stream_path}"
            self.save()
        return self.rtsp_url