"""
Django settings for joblink_project project.
"""

from pathlib import Path
import os
import dj_database_url

# ----------------------------------------
#  BASE DIRECTORY
# ----------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------
#  SECURITY
# ----------------------------------------
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"
# En local, pour Render et localhost
ALLOWED_HOSTS = ['joblink-fdot.onrender.com', '127.0.0.1', 'localhost']


# ----------------------------------------
#  APPLICATIONS
# ----------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Votre app
    'core',
    'cloudinary',
    'cloudinary_storage',

]

# ----------------------------------------
#  MIDDLEWARE
# ----------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Votre middleware
    'core.middleware.AbonnementMiddleware',
]

# ----------------------------------------
#  URLS & WSGI
# ----------------------------------------
ROOT_URLCONF = 'joblink_project.urls'
WSGI_APPLICATION = 'joblink_project.wsgi.application'

# ----------------------------------------
#  TEMPLATES
# ----------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # mettre un dossier templates ici si besoin
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
#  DATABASE
# ----------------------------------------
#DATABASES = {
    #"default": dj_database_url.config(
    #    default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
  #  )
#}
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",
        conn_max_age=600,
        ssl_require=False
    )
}


# ----------------------------------------
#  AUTHENTIFICATION
# ----------------------------------------
AUTH_USER_MODEL = 'core.User'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'

# ----------------------------------------
#  PASSWORD VALIDATION
# ----------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {"NAME": 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {"NAME": 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {"NAME": 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------------------
#  INTERNATIONALIZATION
# ----------------------------------------
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

# ----------------------------------------
#  STATIC FILES
# ----------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]  # fichiers locaux
STATIC_ROOT = BASE_DIR / "staticfiles"    # pour collectstatic

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ----------------------------------------
#  MEDIA FILES
# ----------------------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ----------------------------------------
#  DEFAULT PRIMARY KEY FIELD
# ----------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CLOUDINARY_URL=cloudinary://<your_api_key>:<your_api_secret>@dxndciemg
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'


import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
