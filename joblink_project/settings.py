"""
Django settings for joblink_project.
"""

import os
from pathlib import Path
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api

# ----------------------------------------
# BASE DIRECTORY
# ----------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------
# SECURITY
# ----------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"
#DEBUG = True
ALLOWED_HOSTS = [
    'joblink-fdot.onrender.com',
    '127.0.0.1',
    'localhost'
]

# ----------------------------------------
# APPLICATIONS
# ----------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # App principale
    'core',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',
]

# ----------------------------------------
# MIDDLEWARE
# ----------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise pour Render
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Middleware perso
    'core.middleware.AbonnementMiddleware',
]

# ----------------------------------------
# URLS & WSGI
# ----------------------------------------
ROOT_URLCONF = 'joblink_project.urls'
WSGI_APPLICATION = 'joblink_project.wsgi.application'

# ----------------------------------------
# TEMPLATES
# ----------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Ajouter un dossier templates si nécessaire
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

# ----------------------------------------
# DATABASE (Render utilise DATABASE_URL automatiquement)
# ----------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",  
        conn_max_age=600,
        ssl_require=False
    )
}

# ----------------------------------------
# AUTHENTIFICATION
# ----------------------------------------
AUTH_USER_MODEL = 'core.User'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# ----------------------------------------
# PASSWORD VALIDATORS
# ----------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {"NAME": 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {"NAME": 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {"NAME": 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------------------
# INTERNATIONALIZATION
# ----------------------------------------
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

# ----------------------------------------
# STATIC FILES
# ----------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Cloudinary gère les fichiers statiques en production
STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'

# ----------------------------------------
# MEDIA FILES (gérés par Cloudinary)
# ----------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ----------------------------------------
# CLOUDINARY CONFIG
# ----------------------------------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


# ----------------------------------------
# DEFAULT AUTO FIELD
# ----------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
