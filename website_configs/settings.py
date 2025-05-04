from pathlib import Path
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6*3x9$prukwn9a89us8l85-5j-r4+%^i-kra#9uy$wt4zgz*m-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#  允許哪些主機 ip 位址/ 網域連入
ALLOWED_HOSTS = []

STATIC_URL = '/static/'

# 建立資料庫
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 若你想開發中自動找到 static 檔案
STATICFILES_DIRS = [
    BASE_DIR / 'app_top_keyword' / 'static',
]

# 已安裝的 Django 應用 (App)
INSTALLED_APPS = [
    'django.contrib.admin',          #
    'django.contrib.auth',           #
    'django.contrib.contenttypes',   #
    'django.contrib.sessions',       #
    'django.contrib.messages',       #
    'django.contrib.staticfiles',    #
    'app_top_keyword',     # 關鍵字 app 名稱
    'app_top_person',
    'app_user_keyword',
    'app_top_voice',
    'app_Criminal_Information',
    'app_user_keyword_association',
    'line_today',
    'app_user_keyword_sentiment',
    'app_taipei_mayor',
]

# 　每次請求前後需經過哪些保全或過濾機制 / 中介軟體 (Middleware)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#  網站路由與應用程式接口設定
ROOT_URLCONF = 'website_configs.urls'

TEMPLATES = [
    {   # Django 自帶的 HTML 模板語法
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 當 view.py 讀取到 render(request, "index.html")
        # Django 會去 templates 資料夾尋找 index.html 檔案
        # 如果沒有找到，則會去 app 的資料夾尋找 index.html 檔案，'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 真正 Django 網站的應用程式 (Application) 是從這裡開始的
# 告訴 Django 從 website_configs/wsgi.py 中的 application 變數開始跑整個網站
WSGI_APPLICATION = 'website_configs.wsgi.application'

# 告訴 Django 使用哪一種資料庫，資料要儲存在哪裡
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 使用者在註冊或修改密碼時須符合哪些條件
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "line_today_local",
    }
}

# 網站預設語言
LANGUAGE_CODE = 'zh-hant'

# 網站預設語言的時區
TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

{
    "css.lint.unknownAtRules": "ignore"
}
