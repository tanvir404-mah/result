from django.contrib import admin
from django.urls import path
from django.conf import settings
from results import views



urlpatterns = [
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('', views.search_result, name='search_result'),
    path('admin/', admin.site.urls),
]
