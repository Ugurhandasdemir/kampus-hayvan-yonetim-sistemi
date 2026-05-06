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
]
