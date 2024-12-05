from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('cars/', include('cars.urls', namespace='cars')),
    path('', views.home, name='home'),
]