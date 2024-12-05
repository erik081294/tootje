from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='registration/logged_out.html',
        next_page='home'
    ), name='logout'),
]