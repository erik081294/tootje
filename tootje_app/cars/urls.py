from django.urls import path
from . import views

app_name = 'cars'  # Dit is belangrijk voor de namespace

urlpatterns = [
    path('', views.car_list, name='car_list'),
    path('<int:car_id>/', views.car_detail, name='car_detail'),
    path('create/', views.car_create, name='car_create'),
    path('<int:car_id>/edit/', views.car_edit, name='car_edit'),
    path('<int:car_id>/delete/', views.car_delete, name='car_delete'),
] 