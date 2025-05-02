from django.urls import path
from . import views

app_name = "app_user_keyword"

urlpatterns = [

    path('', views.home, name='home'),
    path('api_get_top_userkey/', views.api_get_top_userkey),

]
