from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 影片列表頁面
    path('', views.VideoListView.as_view(), name='video_list'),
    
    # 註冊新影片
    path('register/', views.register_video, name='register_video'),
    
    # 影片控制（播放、停止、刪除）
    path('control/<int:video_id>/', views.control_video, name='control_video'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)