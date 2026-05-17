from django.conf import settings
from django.db import models


class AnimalReport(models.Model):
    CATEGORY_CHOICES = [
        ("lost", "Kayıp"),
        ("adoption", "Sahiplendirme"),
        ("medical", "Medikal Yardım"),
    ]

    STATUS_CHOICES = [
        ("pending", "Beklemede"),
        ("approved", "Onaylandı"),
        ("rejected", "Reddedildi"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    details = models.TextField(max_length=500)
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    photo = models.ImageField(upload_to="animal_reports/", blank=True, null=True)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="animal_reports",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.full_name}"

    class Meta:
        verbose_name = "Hayvan İlanı"
        verbose_name_plural = "Hayvan İlanları"


class VolunteerApplication(models.Model):
    STATUS_CHOICES = [
        ("pending", "Beklemede"),
        ("approved", "Onaylandı"),
        ("rejected", "Reddedildi"),
    ]

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    skills = models.TextField(max_length=500)
    availability = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Gönüllü Başvurusu"
        verbose_name_plural = "Gönüllü Başvuruları"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(max_length=300, blank=True, default="")

    def __str__(self):
        return f"Profile: {self.user.username}"

    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"


class FeedingStation(models.Model):
    STATUS_CHOICES = [
        ("active", "Aktif"),
        ("maintenance", "Bakımda"),
        ("inactive", "Pasif"),
    ]

    name = models.CharField(max_length=120)
    location_name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    food_level = models.PositiveIntegerField(default=100)
    water_level = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    last_updated = models.DateTimeField(auto_now=True)

    def is_critical(self):
        return self.food_level <= 25 or self.water_level <= 25

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Besleme İstasyonu"
        verbose_name_plural = "Besleme İstasyonları"