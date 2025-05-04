from django.contrib import admin
from django.urls import include
from django.urls import path
from website_configs import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #  path('admin/', admin.site.urls), 用來管理資料庫的，課堂上沒有交到
    # 訪問 http://127.0.0.1:8000/ 僅可顯示初始網頁
    path('', views.index, name='index'),
    path('top_keyword/', include('app_top_keyword.urls')),
    path('top_person/', include('app_top_person.urls')),
    path('user_keyword/', include('app_user_keyword.urls')),
    path('top_voice/', include('app_top_voice.urls')),
    path('criminal_information/', include('app_Criminal_Information.urls')),
    path('userkeyword_assoc/', include('app_user_keyword_association.urls')),
    path('userkeyword_senti/', include('app_user_keyword_sentiment.urls')),
    path('taipei_mayor/', include('app_taipei_mayor.urls')),

    path('line_today/', include(('line_today.urls',
         'line_today'), namespace='line_today')),

]
# 讓開發期間可以讀取媒體檔案
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
