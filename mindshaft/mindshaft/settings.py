"""
Django settings for mindshaft project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
from decouple import config
from pathlib import Path
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False



# CORS settings
ALLOWED_HOSTS = ['api.mindhush.ai', 'www.api.mindhush.ai', '145.223.101.34', 'localhost', 'localhost:5173', '127.0.0.1']
# CORS_ALLOWED_ORIGINS = ['api.mindhush.ai', 'www.api.mindhush.ai', '145.223.101.34', 'localhost', 'localhost:5173', '127.0.0.1']

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True  # Allows cookies and headers like Authorization


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "mindshaft",
    "users",
    "chats",
    "rag",
    "billing",
    "blogs",
    
]
import os
# Define the list of apps for which dynamic loggers should be created
APP_LOGGERS = ['users', 'chats', 'billing', 'rag']

# Base logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Dynamically add a logger and file handler for each app
for app in APP_LOGGERS:
    log_file = os.path.join('logs', f'{app}.log')  # Dynamic log file path
    os.makedirs(os.path.dirname(log_file), exist_ok=True)  # Ensure the directory exists

    # Add a file handler for the app
    LOGGING['handlers'][f'file_{app}'] = {
        'level': 'DEBUG',
        'class': 'logging.FileHandler',
        'filename': log_file,
        'formatter': 'verbose',
    }

    # Add the app's logger
    LOGGING['loggers'][app] = {
        'handlers': ['console', f'file_{app}'],
        'level': 'DEBUG',
        'propagate': False,
    }


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "users.middleware.ResetDailyLimitMiddleware",
    "users.middleware.DebugMiddleware",
]

ROOT_URLCONF = "mindshaft.urls"

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

# Update the JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=6),  # Access token valid for 6 hours
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Refresh token valid for 7 days
    'ROTATE_REFRESH_TOKENS': True,               # Issue a new refresh token with each use
    'BLACKLIST_AFTER_ROTATION': True,            # Blacklist old refresh tokens after use
    'AUTH_HEADER_TYPES': ('Bearer',),            # Use "Bearer" instead of "JWT"
}

WSGI_APPLICATION = "mindshaft.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_USER_MODEL = "users.CustomUser"  # Ensure the app name and model are correct


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

required_env_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'OPENAI_API_KEY', 'STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY', 'STRIPE_WEBHOOK_SECRET', 'STRIPE_SUCCESS_URL', 'STRIPE_FAILURE_URL', 'STRIPE_CANCEL_URL']
for var in required_env_vars:
    print(f"Checking for environment variable: {var}")
    print(f"Value: {config(var)}")
    if not config(var):  # Or os.environ.get(var)
        raise EnvironmentError(f"Missing required environment variable: {var}")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),         # No default, must be set in the environment
        'USER': config('DB_USER'),         # No default, must be set in the environment
        'PASSWORD': config('DB_PASSWORD'), # No default, must be set in the environment
        'HOST': config('DB_HOST'),         # No default, must be set in the environment
        'PORT': config('DB_PORT'),         # No default, must be set in the environment
    }
}

OPENAI_API_KEY = config('OPENAI_API_KEY')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET')
STRIPE_SUCCESS_URL = config('STRIPE_SUCCESS_URL')
STRIPE_FAILURE_URL = config('STRIPE_FAILURE_URL')
STRIPE_CANCEL_URL = config('STRIPE_CANCEL_URL')

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = str(config("EMAIL_HOST", default="smtp.gmail.com"))
EMAIL_PORT = int(config("EMAIL_PORT", default=587))
EMAIL_USE_TLS = bool(config("EMAIL_USE_TLS", default=True))
EMAIL_HOST_USER = str(config("EMAIL_HOST_USER"))
EMAIL_HOST_PASSWORD = str(config("EMAIL_HOST_PASSWORD"))
DEFAULT_FROM_EMAIL = str(
    config("DEFAULT_FROM_EMAIL", default="Your App <your-email@gmail.com>")
)

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/staticfiles/"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
