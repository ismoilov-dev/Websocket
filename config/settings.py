"""
Django settings for Real-Time Chat project (Educational).
Loyiha: Django REST Framework + SimpleJWT + Django Channels + Daphne.
"""

from pathlib import Path
from datetime import timedelta

# Loyihaning asosiy ildiz yo'li
BASE_DIR = Path(__file__).resolve().parent.parent

# Xavfsizlik kaliti (Development maqsadida)
SECRET_KEY = 'django-insecure-educational-websocket-chat-project-key'

# Debug rejimi (Development uchun True)
DEBUG = True

ALLOWED_HOSTS = ['*']

# ==============================================================================
# INSTALLED APPS KONFIGURATSIYASI
# DIQQAT: Daphne eng birinchi turishi shart, shunda u 'runserver' komandasini
# o'z zimmasiga oladi va ASGI/WebSocket ulanishlarini to'g'ri boshqaradi.
# ==============================================================================
INSTALLED_APPS = [
    'daphne',  # ASGI va WebSocket server integratsiyasi (eng yuqorida bo'lishi shart!)

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Uchinchi tomon kutubxonalari
    'rest_framework',        # Django REST Framework
    'drf_spectacular',       # OpenAPI / Swagger dokumentatsiyasi
    
    # Bizning ilovamiz
    'websocket',             # Chat, WebSocket va REST API logikasi
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'websocket' / 'templates'],
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

# WSGI va ASGI konfiguratsiyasi
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ==============================================================================
# DATABASE (SQLite - Development uchun)
# ==============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Parol tekshiruvlari
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Til va vaqt mintaqasi
LANGUAGE_CODE = 'uz-uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# Statik fayllar
STATIC_URL = 'static/'
STATICFILES_DIRS = []

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# DJANGO REST FRAMEWORK SOZLAMALARI
# ==============================================================================
REST_FRAMEWORK = {
    # Standart autentifikatsiya sifatida SimpleJWT ishlatiladi
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Swagger/OpenAPI generatsiyasi uchun drf-spectacular AutoSchema
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ==============================================================================
# SIMPLE JWT SOZLAMALARI
# ==============================================================================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),      # Development uchun qulay muddat
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ==============================================================================
# CHANNELS CHANNEL_LAYERS (Birinchi bosqichda InMemoryChannelLayer)
# ==============================================================================
# Eslatma: InMemoryChannelLayer ma'lumotlarni xotirada (RAM) saqlaydi.
# Bu faqat bitta jarayonli development uchun mos. Keyinchalik Redis'ga o'tish
# uchun faqat shu yerdagi BACKEND va CONFIG o'zgartiriladi.
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# ==============================================================================
# DRF SPECTACULAR (SWAGGER / OPENAPI) SOZLAMALARI
# ==============================================================================
SPECTACULAR_SETTINGS = {
    "TITLE": "Real-Time Chat API",
    "DESCRIPTION": "Educational Django REST Framework + JWT + WebSocket project",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}
