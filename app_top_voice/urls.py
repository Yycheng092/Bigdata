from django.urls import path
from . import views

app_name = 'app_top_voice'

urlpatterns = [
    path('', views.home, name='home'),
    path('api_cate_topvoice/', views.api_cate_topvoice, name='api_cate_topvoice'),
    path('api_news_volume_data/', views.api_news_volume_data,
         name='api_news_volume_data'),  # 👈 加這行
]
