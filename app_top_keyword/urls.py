from django.urls import path
from . import views

app_name = 'app_top_keyword'

urlpatterns = [
    # 會呼叫 views.py 中的 index 方法
    path('', views.home, name='home'),
    path('api_get_cate_topword/', views.api_get_cate_topword, name='api_cate_topword')
]
