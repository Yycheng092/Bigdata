from django.urls import path
from . import views

urlpatterns = [
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('upload-success/', lambda request: render(request,
         'upload_success.html'), name='upload_success'),
]
