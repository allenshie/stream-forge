from django.contrib import admin
from .models import VideoStream

@admin.register(VideoStream)
class VideoStreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'rtsp_url', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'file_path')
    readonly_fields = ('created_at',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編輯時
            return self.readonly_fields + ('stream_path',)
        return self.readonly_fields