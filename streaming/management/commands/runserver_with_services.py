# streaming/management/commands/runserver_with_services.py
from django.core.management.commands.runserver import Command as RunserverCommand
from django.core.management import call_command
import subprocess
import os
import signal
import atexit
import sys

class Command(RunserverCommand):
    help = 'Runs the server with all required services'

    def handle(self, *args, **options):
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        start_script = os.path.join(project_dir, 'scripts', 'start_servers.sh')
        stop_script = os.path.join(project_dir, 'scripts', 'stop_servers.sh')

        # 使用 sh 執行腳本，不需要更改執行權限
        print("Starting required services...")
        try:
            subprocess.run(['sh', start_script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error starting services: {e}")
            sys.exit(1)

        # 註冊關閉時的清理函數
        def cleanup():
            print("\nStopping all services...")
            try:
                subprocess.run(['sh', stop_script], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error stopping services: {e}")

        atexit.register(cleanup)
        signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
        signal.signal(signal.SIGTERM, lambda sig, frame: sys.exit(0))

        # 運行 Django 服務器
        super().handle(*args, **options)