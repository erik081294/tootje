from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='booking_list'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('<int:booking_id>/approve/', views.booking_approve, name='booking_approve'),
    path('<int:booking_id>/reject/', views.booking_reject, name='booking_reject'),
    path('calendar/<int:car_id>/', views.booking_calendar, name='booking_calendar'),
    path('api/availability/', views.get_availability, name='get_availability'),
    path('api/calculate-costs/', views.calculate_costs, name='calculate_costs'),
    path('my-bookings/', views.booking_list, name='my_bookings'),
] 