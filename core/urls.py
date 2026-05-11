from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('animal-details/', views.latest_animal_details_view, name='latest_animal_details'),
    path('animal-details/<int:report_id>/', views.animal_details_view, name='animal_details'),
    path('new-animal/', views.new_animal_view, name='new_animal'),
    path('map/', views.map_view, name='map'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-settings/', views.admin_settings_view, name='admin_settings'),

    path('admin-panel/', views.custom_admin_dashboard, name='custom_admin_dashboard'),

    path('admin-panel/reports/', views.custom_admin_reports, name='custom_admin_reports'),
    path('admin-panel/reports/<int:report_id>/approve/', views.custom_admin_report_approve, name='custom_admin_report_approve'),
    path('admin-panel/reports/<int:report_id>/reject/', views.custom_admin_report_reject, name='custom_admin_report_reject'),
    path('admin-panel/reports/<int:report_id>/delete/', views.custom_admin_report_delete, name='custom_admin_report_delete'),

    path('admin-panel/volunteers/', views.custom_admin_volunteers, name='custom_admin_volunteers'),
    path('admin-panel/volunteers/<int:volunteer_id>/approve/', views.custom_admin_volunteer_approve, name='custom_admin_volunteer_approve'),
    path('admin-panel/volunteers/<int:volunteer_id>/reject/', views.custom_admin_volunteer_reject, name='custom_admin_volunteer_reject'),
    path('admin-panel/volunteers/<int:volunteer_id>/delete/', views.custom_admin_volunteer_delete, name='custom_admin_volunteer_delete'),

    path('admin-panel/stations/', views.custom_admin_stations, name='custom_admin_stations'),
    path('admin-panel/stations/<int:station_id>/update/', views.custom_admin_station_update, name='custom_admin_station_update'),
    path('admin-panel/stations/<int:station_id>/delete/', views.custom_admin_station_delete, name='custom_admin_station_delete'),
]
