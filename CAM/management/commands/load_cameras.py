import os
from django.core.management.base import BaseCommand
from django.conf import settings
from CAM.models import CameraFeed

class Command(BaseCommand):
    help = 'Scans media/camera_feeds and adds videos to the database'

    def handle(self, *args, **kwargs):
        # 1. Path to your videos
        feed_dir = os.path.join(settings.MEDIA_ROOT, 'camera_feeds')
        
        # Check if folder exists
        if not os.path.exists(feed_dir):
            self.stdout.write(self.style.ERROR(f"Folder not found: {feed_dir}"))
            return

        # 2. List all video files
        valid_extensions = ('.mp4', '.avi', '.mov', '.webm', '.mkv')
        files = [f for f in os.listdir(feed_dir) if f.lower().endswith(valid_extensions)]

        if not files:
            self.stdout.write(self.style.WARNING("No video files found in media/camera_feeds"))
            return

        # 3. Add to Database
        count = 0
        for filename in files:
            # Use filename as camera name (e.g., "cam1.mp4" -> "Cam 1")
            cam_name = filename.split('.')[0].replace('_', ' ').title()
            
            # The path Django expects relative to MEDIA_ROOT
            relative_path = os.path.join('camera_feeds', filename)

            # Create only if it doesn't exist
            obj, created = CameraFeed.objects.get_or_create(
                camera_name=cam_name,
                defaults={'video_file': relative_path}
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Added new camera: {cam_name}"))
                count += 1
            else:
                self.stdout.write(f"Skipped existing: {cam_name}")

        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully registered {count} new cameras!"))