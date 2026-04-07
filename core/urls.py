from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('animal-details/', views.animal_details_view, name='animal_details'),
    path('new-animal/', views.new_animal_view, name='new_animal'),
]
