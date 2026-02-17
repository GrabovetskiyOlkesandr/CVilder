from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home_page, name='home'),
    path('comparison/', views.comparison, name='comparison'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)