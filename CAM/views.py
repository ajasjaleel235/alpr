from django.shortcuts import render, redirect
from django.contrib import messages
from .models import TrafficLog, CameraFeed
from .services import process_random_camera_feeds 
import threading

# --- CONFIGURATION: CAMERA LOCATIONS ---
# (Latitude, Longitude) for your 5 cameras
# You can change these coordinates to any location you want.
CAMERA_LOCATIONS = {
    # Adjust keys ('Cam 1') to match your actual video filenames/camera names
    'Cam 1': {'lat': 25.1972, 'lng': 55.2744, 'address': 'Downtown Dubai'}, 
    'Cam 2': {'lat': 25.0773, 'lng': 55.1404, 'address': 'Dubai Marina'},
    'Cam 3': {'lat': 25.2048, 'lng': 55.2708, 'address': 'Sheikh Zayed Rd'},
    'Cam 4': {'lat': 25.1181, 'lng': 55.2006, 'address': 'Al Barsha'},
    'Cam 5': {'lat': 25.2769, 'lng': 55.2963, 'address': 'Deira City Center'},
}

def unified_dashboard(request):
    """
    Handles Dashboard, Search, and Map generation.
    """
    # 1. SIDEBAR DATA
    cameras = CameraFeed.objects.all()
    stats_data = []
    for cam in cameras:
        count = TrafficLog.objects.filter(camera=cam).count()
        stats_data.append({'name': cam.camera_name, 'total_vehicles': count})

    # 2. SEARCH & MAP LOGIC
    query = request.GET.get('q')
    detections = []
    
    if query:
        # SEARCH MODE: Find specific plate
        table_title = f"Tracking Results for: {query}"
        
        # Get logs and join with Camera data
        raw_detections = TrafficLog.objects.filter(license_plate__icontains=query).select_related('camera').order_by('-timestamp')
        
        # Attach Location Data to each detection manually
        for log in raw_detections:
            cam_name = log.camera.camera_name
            # Default to Dubai (0,0) if camera name doesn't match dictionary
            loc = CAMERA_LOCATIONS.get(cam_name, {'lat': 25.2048, 'lng': 55.2708, 'address': 'Unknown Location'})
            
            # We add new attributes to the log object on the fly
            log.lat = loc['lat']
            log.lng = loc['lng']
            log.location_name = loc['address']
            detections.append(log)
            
    else:
        # LIVE MODE: Show recent logs (No map needed usually)
        table_title = "Real-Time Detection Log"
        detections = TrafficLog.objects.select_related('camera').order_by('-timestamp')[:20]

    return render(request, 'cam/dashboard.html', {
        'stats': stats_data,
        'detections': detections,
        'table_title': table_title,
        'query': query or ""
    })

def trigger_processing(request):
    thread = threading.Thread(target=process_random_camera_feeds)
    thread.start()
    messages.success(request, "SYSTEM SCAN INITIATED: Processing feeds...")
    return redirect('dashboard')