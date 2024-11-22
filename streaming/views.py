from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.contrib import messages
from .models import VideoStream
from .tasks import start_stream, stop_stream
import uuid
import magic
import ffmpeg

class VideoListView(ListView):
    """影片列表視圖"""
    model = VideoStream
    template_name = 'streaming/video_list.html'
    context_object_name = 'videos'
    ordering = ['-created_at']

def validate_video_file(file):
    """驗證上傳的文件"""
    # 檢查文件大小（例如限制為 2GB）
    if file.size > 2 * 1024 * 1024 * 1024:
        return False, "檔案大小不能超過 2GB"
    
    # 檢查文件類型
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # 重置文件指針
    
    allowed_types = [
        'video/mp4',
        'video/x-msvideo',  # AVI
        'video/x-matroska'  # MKV
    ]
    
    if mime not in allowed_types:
        return False, "只支援 MP4, AVI, MKV 格式的影片"
    
    # 驗證是否為有效的視頻文件
    try:
        # 將文件暫時保存到臨時目錄
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            temp_file.flush()
            
            try:
                probe = ffmpeg.probe(temp_file.name)
                if not any(stream['codec_type'] == 'video' for stream in probe['streams']):
                    return False, "無效的影片檔案"
            finally:
                # 清理臨時文件
                os.unlink(temp_file.name)
                # 重置文件指針，以便後續使用
                file.seek(0)
                
    except ffmpeg.Error:
        return False, "無法讀取影片檔案"
    
    return True, None

def register_video(request):
    """註冊新影片"""
    if request.method == 'POST':
        name = request.POST.get('name')
        video_file = request.FILES.get('video_file')
        
        if not name or not video_file:
            messages.error(request, '請填寫所有必要欄位')
            return redirect('register_video')
        
        # 驗證文件
        is_valid, error_message = validate_video_file(video_file)
        if not is_valid:
            messages.error(request, error_message)
            return redirect('register_video')
        
        try:
            # 生成唯一的串流路徑
            stream_path = str(uuid.uuid4())
            
            # 創建新的視頻記錄
            video = VideoStream(
                name=name,
                video_file=video_file,
                stream_path=stream_path,
                status='STOPPED'
            )
            video.save()
            
            messages.success(request, f'影片 {name} 註冊成功')
            return redirect('video_list')
            
        except Exception as e:
            messages.error(request, f'註冊失敗：{str(e)}')
            return redirect('register_video')
    
    return render(request, 'streaming/register.html')

def control_video(request, video_id):
    """控制影片串流"""
    video = get_object_or_404(VideoStream, id=video_id)
    action = request.POST.get('action')
    
    try:
        if action == 'play':
            if video.status != 'PLAYING':
                start_stream.delay(video_id)
                messages.success(request, f'開始播放 {video.name}')
        
        elif action == 'stop':
            if video.status == 'PLAYING':
                stop_stream.delay(video_id)
                messages.success(request, f'停止播放 {video.name}')
        
        elif action == 'delete':
            if video.status == 'PLAYING':
                stop_stream.delay(video_id)
            video_name = video.name
            video.delete()
            messages.success(request, f'已刪除 {video_name}')
        
        else:
            messages.error(request, '無效的操作')
            
    except Exception as e:
        messages.error(request, f'操作失敗：{str(e)}')
    
    return redirect('video_list')