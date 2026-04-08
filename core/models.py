from django.conf import settings
from django.db import models

class AnimalReport(models.Model):
    CATEGORY_CHOICES = [
        ("lost", "Lost"),
        ("adoption", "Adoption"),
        ("medical", "Medical"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
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
