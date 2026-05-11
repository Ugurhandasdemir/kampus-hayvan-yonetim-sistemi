from decimal import Decimal, InvalidOperation

from io import BytesIO

from pathlib import Path

from uuid import uuid4

import json



from django.contrib import messages

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import User

from django.contrib.auth.password_validation import validate_password

from django.core.exceptions import ValidationError

from django.core.files.uploadedfile import InMemoryUploadedFile

from django.shortcuts import get_object_or_404, redirect, render

from django.utils.http import url_has_allowed_host_and_scheme



from django.contrib.auth.decorators import login_required



from PIL import Image, ImageOps, UnidentifiedImageError



from .models import AnimalReport, FeedingStation, VolunteerApplication





PHOTO_TARGET_SIZE = (800, 1000)  # 4:5, matches the form card ratio

DEFAULT_LATITUDE = Decimal("41.008200")

DEFAULT_LONGITUDE = Decimal("28.978400")





def _resize_report_photo(uploaded_file):

    try:

        with Image.open(uploaded_file) as image:

            image = ImageOps.exif_transpose(image)

            fitted = ImageOps.fit(

                image.convert("RGB"),

                PHOTO_TARGET_SIZE,

                method=Image.Resampling.LANCZOS,

                centering=(0.5, 0.5),

            )

    except (UnidentifiedImageError, OSError, ValueError) as exc:

        raise ValueError("Yuklenen dosya gecerli bir gorsel degil.") from exc



    output = BytesIO()

    fitted.save(output, format="JPEG", quality=88, optimize=True)

    output.seek(0)



    base_name = Path(uploaded_file.name).stem or "animal-report"

    file_name = f"{base_name}-{uuid4().hex[:8]}.jpg"



    return InMemoryUploadedFile(

        file=output,

        field_name=uploaded_file.field_name,

        name=file_name,

        content_type="image/jpeg",

        size=output.getbuffer().nbytes,

        charset=None,

    )





def home(request):

    return render(request, 'home.html')





def login_view(request):

    if request.user.is_authenticated:

        return redirect('home')



    if request.method == 'POST':

        email = request.POST.get('email', '').strip().lower()

        password = request.POST.get('password', '')



        if not email or not password:

            messages.error(request, 'E-posta ve sifre alanlarini doldurun.')

        else:

            user = authenticate(request, username=email, password=password)

            if user is None:

                messages.error(request, 'E-posta veya sifre hatali.')

            else:

                login(request, user)

                messages.success(request, 'Basariyla giris yaptin.')

                next_url = request.POST.get('next') or request.GET.get('next')

                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):

                    return redirect(next_url)

                return redirect('home')



    return render(request, 'login.html')





def register_view(request):

    if request.user.is_authenticated:

        return redirect('home')



    if request.method == 'POST':

        full_name = request.POST.get('full_name', '').strip()

        email = request.POST.get('email', '').strip().lower()

        password = request.POST.get('password', '')

        terms_accepted = request.POST.get('terms') == 'on'



        if not full_name or not email or not password:

            messages.error(request, 'Lutfen zorunlu alanlari doldur.')

        elif not terms_accepted:

            messages.error(request, 'Devam etmek icin sartlari kabul etmelisin.')

        elif User.objects.filter(username=email).exists() or User.objects.filter(email__iexact=email).exists():

            messages.error(request, 'Bu e-posta ile kayitli bir hesap var.')

        else:

            new_user = User(username=email, email=email, first_name=full_name)



            try:

                validate_password(password, user=new_user)

            except ValidationError as exc:

                for error_text in exc.messages:

                    messages.error(request, error_text)

            else:

                new_user.set_password(password)

                new_user.save()

                login(request, new_user)

                messages.success(request, 'Hesabin olusturuldu. Hos geldin!')

                return redirect('home')



    return render(request, 'register.html')





def logout_view(request):

    if request.method == 'POST':

        logout(request)

        messages.success(request, 'Cikis yaptin.')

    return redirect('login')





def latest_animal_details_view(request):

    latest_report = AnimalReport.objects.order_by("-created_at").first()

    if latest_report is None:

        messages.info(request, "Henuz rapor eklenmedi. Ilk raporu olusturabilirsin.")

        return redirect("new_animal")

    return redirect("animal_details", report_id=latest_report.id)





def animal_details_view(request, report_id):

    report = get_object_or_404(AnimalReport, id=report_id)

    latitude = report.latitude if report.latitude is not None else DEFAULT_LATITUDE

    longitude = report.longitude if report.longitude is not None else DEFAULT_LONGITUDE

    context = {

        "report": report,

        "report_latitude": f"{latitude:.6f}",

        "report_longitude": f"{longitude:.6f}",

    }

    return render(request, "animal_details.html", context)





def new_animal_view(request):

    if request.method == "POST":

        category = request.POST.get("category", "").strip()

        details = request.POST.get("details", "").strip()

        full_name = request.POST.get("full_name", "").strip()

        phone = request.POST.get("phone", "").strip()

        latitude_raw = request.POST.get("latitude", "").strip()

        longitude_raw = request.POST.get("longitude", "").strip()

        photo = request.FILES.get("photo")



        valid_categories = {key for key, _ in AnimalReport.CATEGORY_CHOICES}



        if category not in valid_categories:

            messages.error(request, "Gecerli bir kategori sec.")

        elif not details or not full_name or not phone:

            messages.error(request, "Lutfen zorunlu alanlari doldur.")

        elif len(details) > 500:

            messages.error(request, "Aciklama en fazla 500 karakter olabilir.")

        elif not latitude_raw or not longitude_raw:

            messages.error(request, "Lutfen haritadan bir konum sec.")

        else:

            try:

                latitude = Decimal(latitude_raw)

                longitude = Decimal(longitude_raw)

            except InvalidOperation:

                messages.error(request, "Konum bilgisi gecersiz.")

            else:

                if not (Decimal("-90") <= latitude <= Decimal("90")):

                    messages.error(request, "Enlem degeri gecersiz.")

                elif not (Decimal("-180") <= longitude <= Decimal("180")):

                    messages.error(request, "Boylam degeri gecersiz.")

                else:

                    resized_photo = photo

                    if photo:

                        try:

                            resized_photo = _resize_report_photo(photo)

                        except ValueError as exc:

                            messages.error(request, str(exc))

                            return render(request, "new_animal.html")



                    created_report = AnimalReport.objects.create(

                        category=category,

                        details=details,

                        full_name=full_name,

                        phone=phone,

                        latitude=latitude,

                        longitude=longitude,

                        photo=resized_photo,

                        reporter=request.user if request.user.is_authenticated else None,

                    )

                    messages.success(request, "Rapor basariyla yayimlandi.")

                    return redirect("animal_details", report_id=created_report.id)



    return render(request, "new_animal.html")







def map_view(request):

    reports = AnimalReport.objects.all().order_by("-created_at")

    category = request.GET.get("category", "")

    if category in ["lost", "adoption", "medical"]:

        reports = reports.filter(category=category)

    

    reports_data = []

    for r in reports:

        reports_data.append({

            "id": r.id,

            "category": r.category,

            "full_name": r.full_name,

            "details": r.details[:100],

            "latitude": str(r.latitude) if r.latitude else "41.008200",

            "longitude": str(r.longitude) if r.longitude else "28.978400",

            "photo_url": r.photo.url if r.photo and r.photo.name else "",

            "created_at": r.created_at.strftime("%d %b %Y"),

        })

    

    counts = {

        "lost": AnimalReport.objects.filter(category="lost").count(),

        "adoption": AnimalReport.objects.filter(category="adoption").count(),

        "medical": AnimalReport.objects.filter(category="medical").count(),

    }

    

    context = {

        "reports_json": json.dumps(reports_data),

        "counts": counts,

        "active_category": category,

    }

    return render(request, "map.html", context)





@login_required

def profile_view(request):

    user_reports = AnimalReport.objects.filter(reporter=request.user).order_by("-created_at")

    

    if request.method == "POST":

        report_id = request.POST.get("delete_id")

        if report_id:

            report = get_object_or_404(AnimalReport, id=report_id, reporter=request.user)

            report.delete()

            messages.success(request, "İlan silindi.")

            return redirect("profile")

    

    context = {"user_reports": user_reports}

    return render(request, "profile.html", context)





@login_required

def admin_settings_view(request):

    if not request.user.is_staff:

        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")

        return redirect("map")

    

    if request.method == "POST":

        first_name = request.POST.get("first_name", "").strip()

        if first_name:

            request.user.first_name = first_name

            request.user.save()

            messages.success(request, "Bilgiler güncellendi.")

            return redirect("admin_settings")

    

    return render(request, "admin_settings.html")


def _is_custom_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
def custom_admin_dashboard(request):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu sayfaya erisim yetkiniz yok.")
        return redirect("home")

    total_reports = AnimalReport.objects.count()
    pending_reports = AnimalReport.objects.filter(status="pending").count()
    approved_reports = AnimalReport.objects.filter(status="approved").count()
    rejected_reports = AnimalReport.objects.filter(status="rejected").count()

    total_volunteers = VolunteerApplication.objects.count()
    pending_volunteers = VolunteerApplication.objects.filter(status="pending").count()

    total_stations = FeedingStation.objects.count()
    critical_stations = [
        station for station in FeedingStation.objects.all()
        if station.is_critical()
    ]

    latest_reports = AnimalReport.objects.order_by("-created_at")[:5]

    context = {
        "total_reports": total_reports,
        "pending_reports": pending_reports,
        "approved_reports": approved_reports,
        "rejected_reports": rejected_reports,
        "total_volunteers": total_volunteers,
        "pending_volunteers": pending_volunteers,
        "total_stations": total_stations,
        "critical_stations_count": len(critical_stations),
        "latest_reports": latest_reports,
    }

    return render(request, "admin_panel/dashboard.html", context)


@login_required
def custom_admin_reports(request):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu sayfaya erisim yetkiniz yok.")
        return redirect("home")

    reports = AnimalReport.objects.all().order_by("-created_at")

    status = request.GET.get("status", "").strip()
    category = request.GET.get("category", "").strip()
    search = request.GET.get("search", "").strip()

    if status in ["pending", "approved", "rejected"]:
        reports = reports.filter(status=status)

    if category in ["lost", "adoption", "medical"]:
        reports = reports.filter(category=category)

    if search:
        reports = reports.filter(full_name__icontains=search)

    context = {
        "reports": reports,
        "active_status": status,
        "active_category": category,
        "search": search,
    }

    return render(request, "admin_panel/reports.html", context)


@login_required
def custom_admin_report_approve(request, report_id):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu i�lem i�in yetkiniz yok.")
        return redirect("home")

    report = get_object_or_404(AnimalReport, id=report_id)
    report.status = "approved"
    report.save()
    messages.success(request, "Ilan onaylandi.")
    return redirect("custom_admin_reports")


@login_required
def custom_admin_report_reject(request, report_id):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu i�lem i�in yetkiniz yok.")
        return redirect("home")

    report = get_object_or_404(AnimalReport, id=report_id)
    report.status = "rejected"
    report.save()
    messages.success(request, "Ilan reddedildi.")
    return redirect("custom_admin_reports")


@login_required
def custom_admin_report_delete(request, report_id):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu i�lem i�in yetkiniz yok.")
        return redirect("home")

    report = get_object_or_404(AnimalReport, id=report_id)
    report.delete()
    messages.success(request, "Ilan silindi.")
    return redirect("custom_admin_reports")


@login_required
def custom_admin_volunteers(request):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu sayfaya erisim yetkiniz yok.")
        return redirect("home")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        skills = request.POST.get("skills", "").strip()
        availability = request.POST.get("availability", "").strip()

        if not full_name or not email or not phone or not skills or not availability:
            messages.error(request, "Lutfen t�m g�n�ll� alanlar�n� doldurun.")
        else:
            VolunteerApplication.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                skills=skills,
                availability=availability,
            )
            messages.success(request, "Gonullu basvurusu eklendi.")
            return redirect("custom_admin_volunteers")

    volunteers = VolunteerApplication.objects.all().order_by("-created_at")
    status = request.GET.get("status", "").strip()

    if status in ["pending", "approved", "rejected"]:
        volunteers = volunteers.filter(status=status)

    return render(request, "admin_panel/volunteers.html", {
        "volunteers": volunteers,
        "active_status": status,
    })


@login_required
def custom_admin_volunteer_approve(request, volunteer_id):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu i�lem i�in yetkiniz yok.")
        return redirect("home")

    volunteer = get_object_or_404(VolunteerApplication, id=volunteer_id)
    volunteer.status = "approved"
    volunteer.save()
    messages.success(request, "Gonullu basvurusu onaylandi.")
    return redirect("custom_admin_volunteers")


@login_required
def custom_admin_volunteer_reject(request, volunteer_id):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu i�lem i�in yetkiniz yok.")
        return redirect("home")

    volunteer = get_object_or_404(VolunteerApplication, id=volunteer_id)
    volunteer.status = "rejected"
    volunteer.save()
    messages.success(request, "Gonullu basvurusu reddedildi.")
    return redirect("custom_admin_volunteers")


@login_required
def custom_admin_volunteer_delete(request, volunteer_id):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu i�lem i�in yetkiniz yok.")
        return redirect("home")

    volunteer = get_object_or_404(VolunteerApplication, id=volunteer_id)
    volunteer.delete()
    messages.success(request, "Gonullu basvurusu silindi.")
    return redirect("custom_admin_volunteers")


@login_required
def custom_admin_stations(request):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu sayfaya erisim yetkiniz yok.")
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        location_name = request.POST.get("location_name", "").strip()
        latitude = request.POST.get("latitude", "").strip() or None
        longitude = request.POST.get("longitude", "").strip() or None
        food_level = request.POST.get("food_level", "100").strip()
        water_level = request.POST.get("water_level", "100").strip()
        status = request.POST.get("status", "active").strip()

        if not name or not location_name:
            messages.error(request, "�stasyon ad� ve konum ad� zorunludur.")
        else:
            FeedingStation.objects.create(
                name=name,
                location_name=location_name,
                latitude=latitude,
                longitude=longitude,
                food_level=food_level,
                water_level=water_level,
                status=status,
            )
            messages.success(request, "Besleme istasyonu eklendi.")
            return redirect("custom_admin_stations")

    stations = FeedingStation.objects.all().order_by("name")

    return render(request, "admin_panel/stations.html", {
        "stations": stations,
    })


@login_required
def custom_admin_station_delete(request, station_id):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu i�lem i�in yetkiniz yok.")
        return redirect("home")

    station = get_object_or_404(FeedingStation, id=station_id)
    station.delete()
    messages.success(request, "Besleme istasyonu silindi.")
    return redirect("custom_admin_stations")


@login_required
def custom_admin_station_update(request, station_id):
    if not _is_custom_admin(request.user):
        messages.error(request, "Bu i�lem i�in yetkiniz yok.")
        return redirect("home")

    station = get_object_or_404(FeedingStation, id=station_id)

    if request.method == "POST":
        station.food_level = request.POST.get("food_level", station.food_level)
        station.water_level = request.POST.get("water_level", station.water_level)
        station.status = request.POST.get("status", station.status)
        station.save()
        messages.success(request, "Besleme istasyonu guncellendi.")

    return redirect("custom_admin_stations")

