from django.contrib import admin

from .models import AnimalReport, FeedingStation, VolunteerApplication


@admin.register(AnimalReport)
class AnimalReportAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "status", "full_name", "phone", "created_at")
    list_filter = ("category", "status", "created_at")
    search_fields = ("full_name", "phone", "details")
    ordering = ("-created_at",)


@admin.register(VolunteerApplication)
class VolunteerApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "phone", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "phone", "skills")
    ordering = ("-created_at",)


@admin.register(FeedingStation)
class FeedingStationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "location_name",
        "food_level",
        "water_level",
        "status",
        "last_updated",
    )
    list_filter = ("status", "last_updated")
    search_fields = ("name", "location_name")
    ordering = ("name",)