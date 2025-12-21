import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_PASSWORD_VALIDATORS = []
# -------------------------
# Sécurité
# -------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"
#DEBUG = True
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
    'joblink-1-b65k.onrender.com',                 # accepte tous les sous-domaines Render
    'joblink-fdot.onrender.com',     # ton lien actuel
]


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
#DEFAULT_FROM_EMAIL = 'JobLink <joblinkngolo@gmail.com>'
#EMAIL_HOST_PASSWORD= ''
#EMAIL_HOST_USER = 'joblinkngolo@gmail.com'

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = os.environ.get(
    'DEFAULT_FROM_EMAIL',
    'JobLink <joblinkngolo@gmail.com>'
)
# -------------------------
# Applications
# -------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "cloudinary",
    "cloudinary_storage",

    "core",
    "pwa",
]

# -------------------------
# Middleware
# -------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "joblink_project.urls"
WSGI_APPLICATION = "joblink_project.wsgi.application"

# -------------------------
# Templates
# -------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# -------------------------
# Database
# -------------------------
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",
        conn_max_age=600,
        ssl_require=False,
    )
}

# -------------------------
# Auth
# -------------------------
AUTH_USER_MODEL = "core.User"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"
LOGIN_URL = "login"

# -------------------------
# Static Files (gérés par WhiteNoise)
# -------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------
# Media Files (Cloudinary)
# -------------------------
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Cloudinary configuration automatique via CLOUDINARY_URL
#import cloudinary
#cloudinary.config(
    #cloudinary_url=os.getenv("CLOUDINARY_URL")
#)

import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
  api_key = os.getenv("CLOUDINARY_API_KEY"),
  api_secret = os.getenv("CLOUDINARY_API_SECRET"),
  secure = True
)

# -------------------------
# Internationalization
# -------------------------
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"



#DEFAULT_FROM_EMAIL = "JobLink <9d4f8c001@smtp-brevo.com>"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

PWA_APP_NAME = 'JobLink'
PWA_APP_SHORT_NAME = 'JobLink'
PWA_APP_DESCRIPTION = "Plateforme de prestation et de services."
PWA_APP_THEME_COLOR = '#0a7cff'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = '#0a7cff'
PWA_APP_ICONS = [
    {
        'src': '/static/icons/icon-512.png',
        'sizes': '512x512'
    }
]


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"  # ou Path(BASE_DIR, "staticfiles") selon ta version
