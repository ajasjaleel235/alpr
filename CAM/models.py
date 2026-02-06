from django.db import models

class CameraFeed(models.Model):
    camera_name = models.CharField(max_length=50, unique=True) # e.g., "Cam1", "Cam2"
    video_file = models.FileField(upload_to='camera_feeds/')
    last_processed = models.DateTimeField(auto_now=True)

class TrafficLog(models.Model):
    camera = models.ForeignKey(CameraFeed, on_delete=models.CASCADE)
    license_plate = models.CharField(max_length=20)
    car_id = models.IntegerField() # Tracker ID from SORT
    timestamp = models.DateTimeField(auto_now_add=True)
    confidence = models.FloatField()

    def __str__(self):
        return f"{self.license_plate} detected by {self.camera.camera_name}"