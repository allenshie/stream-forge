# streaming/management/commands/stopservices.py
from django.core.management.base import BaseCommand
import subprocess
import os

class Command(BaseCommand):
    help = 'Stops all project services'

    def handle(self, *args, **options):
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        stop_script = os.path.join(project_dir, 'scripts', 'stop_servers.sh')

        # 使用 sh 執行腳本
        try:
            subprocess.run(['sh', stop_script], check=True)
            self.stdout.write(self.style.SUCCESS('Successfully stopped all services'))
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Error stopping services: {e}'))