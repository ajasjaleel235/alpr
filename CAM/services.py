import os
import random
import pandas as pd
from django.conf import settings
from .models import CameraFeed, TrafficLog
from alpr.core.algorithm import LicensePlateDetector

def process_random_camera_feeds():
    detector = LicensePlateDetector(
        model_path_yolo='yolov8n.pt', 
        model_path_plate='license_plate_detector.pt'
    )

    # Get all 5 camera feeds
    feeds = list(CameraFeed.objects.all())
    
    # Randomly shuffle them if you want 'random' processing order
    random.shuffle(feeds)

    for feed in feeds:
        # Define path for this specific camera's output
        raw_csv = os.path.join(settings.MEDIA_ROOT, 'csvs', f'{feed.camera_name}_results.csv')
        
        # 1. Run detection
        # This uses the process_video method from your algorithm.py
        detector.process_video(feed.video_file.path, raw_csv)

        # 2. Read results and log them to the database
        if os.path.exists(raw_csv):
            df = pd.read_csv(raw_csv)
            df = df[df['license_number'] != '0'] # Filter out non-detections
            
            for car_id in df['car_id'].unique():
                car_group = df[df['car_id'] == car_id]
                # Get the best read based on confidence score
                best_row = car_group.sort_values('license_number_score', ascending=False).iloc[0]

                TrafficLog.objects.create(
                    camera=feed, # Stores which camera (Cam1, Cam2, etc.)
                    car_id=int(car_id),
                    license_plate=str(best_row['license_number']).strip().upper(),
                    confidence=float(best_row['license_number_score'])
                )