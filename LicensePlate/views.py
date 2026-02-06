from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .utils.LicensePlate import detect_license_plates
from django.db.models import Sum
from .models import Vehicle

def home(request):
    return render(request, "LicensePlate/home.html")



def license_plate_detection(request):
    context = {}

    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        fs = FileSystemStorage(location="media/images")
        filename = fs.save(image.name, image)
        image_path = fs.path(filename)

        # 1️⃣ Detect license plates from image
        detected_plates = detect_license_plates(image_path)

        vehicles_data = []


        # 2️⃣ Fetch DB data for each plate
        for plate in detected_plates:
            try:
                plate_text = plate["text"].strip().upper()

                vehicle = Vehicle.objects.select_related(
                    "owner",
                    "owner__drivinglicense",
                    "insurance"
                ).get(license_plate=plate_text)

                # 🔽 DEFINE THESE FIRST
                all_violations = vehicle.violation_set.all()
                unpaid_violations = all_violations.filter(is_paid=False)

                total_fine = unpaid_violations.aggregate(
                    Sum("fine_amount")
                )["fine_amount__sum"] or 0

                has_violation = unpaid_violations.exists()

                # 🔽 NOW USE THEM
                vehicles_data.append({
                    "plate": plate_text,
                    "vehicle": vehicle,
                    "owner": vehicle.owner,
                    "license": vehicle.owner.drivinglicense,
                    "insurance": vehicle.insurance,
                    "violations": all_violations,
                    "active_violations": unpaid_violations,
                    "has_violation": has_violation,
                    "total_fine": total_fine,
                })

            except Vehicle.DoesNotExist:
                vehicles_data.append({
                    "plate": plate_text,
                    "not_found": True
                })

            except KeyError:
                # Handle case where detection didn't return a 'text' key
                continue

        # 3️⃣ Send data to template
        context["uploaded_image"] = fs.url(filename)
        context["vehicles_data"] = vehicles_data

    return render(request, "LicensePlate/upload.html", context)
