# 要部署網站時，請從哪一個地方開始跑整個網站的應用程式 (Application)
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website_configs.settings')

application = get_wsgi_application()
