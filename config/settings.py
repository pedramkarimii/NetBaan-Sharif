import os
from pathlib import Path
from datetime import timedelta
from decouple import config  # noqa

USE_TZ = True
USE_I18N = True
LANGUAGE_CODE = "en-us"
ROOT_URLCONF = "config.urls"
AUTH_USER_MODEL = 'account.User'
WSGI_APPLICATION = "config.wsgi.application"
TIME_ZONE = config("TIME_ZONE", default="UTC")
DEBUG = config("DEBUG", cast=bool, default=True)
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "apps"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SECRET_KEY = config("SECRET_KEY", default="secret-key-!!!")
ALLOWED_HOSTS = (
    ["*"]
    if DEBUG
    else config(
        "ALLOWED_HOSTS", cast=lambda host: [h.strip() for h in host.split(",") if h]
    )
)
# Applications
APPLICATIONS = ["account", "core", "book"]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# THROTTLE_CONFIG
THROTTLE_CONFIG = {
    'default': {
        'rate': '5/m',  # 5 requests per 5 minutes
    },
    'admin': {
        'rate': '20/m',  # 20 requests per 5 minutes
    },
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework.simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework.simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework.simplejwt.serializers.TokenRefreshSlidingSerializer",
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        # 'apps.account.users_auth.authenticate.JWTAuthentication',
    ],
    'DEFAULT_THROTTLING_CLASSES': [
        'apps.account.throttling.CustomThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'default': '5/m',
        'admin': '20/m',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
SPECTACULAR_SETTINGS = {
    'TITLE': 'NetBaan',
    'DESCRIPTION': 'Book Recommendation System',
    'VERSION': '1.0.0',
}
# Serving
STATIC_URL = "storage/static/"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "storage/media"

# TOKEN Handling
# JWT_AUTH_ACCESS_TOKEN_LIFETIME = timedelta(minutes=5)
# JWT_AUTH_REFRESH_TOKEN_LIFETIME = timedelta(days=1)
# JWT_AUTH_ENCRYPT_KEY = b'32 bytes'
# JWT_AUTH_GET_USER_BY_ACCESS_TOKEN = True
# JWT_AUTH_CACHE_USING = True


# Logging
LOG_FILE_PATH = config("LOG_FILE_PATH")

# Mode Handling:
if DEBUG:

    INSTALLED_APPS = [
        "jazzmin",  # Third-party
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # Third-party
        "rest_framework",
        "rest_framework.authtoken",
        "drf_spectacular",
        # Application
        *list(map(lambda app: f"apps.{app}", APPLICATIONS)),
    ]
    # STATICFILES_DIRS = [BASE_DIR / "storage/static"]

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": config("DB_PORT"),
        }
    }

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": BASE_DIR / "utility/cache",
        }
    }

    EMAIL_BACKEND = config("DEBUG_EMAIL_BACKEND")
    EMAIL_USE_TLS = config("DEBUG_EMAIL_USE_TLS", cast=bool, default=True)
    EMAIL_USE_SSL = config("DEBUG_EMAIL_USE_SSL", cast=bool, default=False)
    EMAIL_HOST = config("DEBUG_EMAIL_HOST")
    EMAIL_PORT = config("DEBUG_EMAIL_PORT")
    EMAIL_HOST_USER = config("DEBUG_EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = config("DEBUG_EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = config("DEBUG_DEFAULT_FROM_EMAIL")
else:

    CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS")
    STATIC_ROOT = BASE_DIR / "storage/static/"
    INSTALLED_APPS = [
        "jazzmin",  # Third-party
        "django.contrib.auth",
        "django.contrib.contenttypes",
        # Third-party
        "rest_framework",
        "rest_framework",
        "rest_framework.authtoken",
        "drf_spectacular",
        # Application
        *list(map(lambda app: f"apps.{app}", APPLICATIONS)),
    ]
    REDIS_URL = f"redis://{config('REDIS_HOST')}:{config('REDIS_PORT')}"

    # CACHES = {
    #     "default": {
    #         "BACKEND": "django.core.cache.backends.redis.RedisCache",
    #         "LOCATION": REDIS_URL,
    #     }
    # }
    SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

    EMAIL_BACKEND = config("EMAIL_BACKEND")
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
    EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
    EMAIL_HOST = config("EMAIL_HOST")
    EMAIL_PORT = config("EMAIL_PORT")
    EMAIL_HOST_USER = config("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

    # AWS S3 Configuration
    DEFAULT_FILE_STORAGE = config('DEFAULT_FILE_STORAGE')
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_FILE_OVERWRITE = config('AWS_S3_FILE_OVERWRITE', cast=bool, default=False)
    AWS_SERVICE_NAME = config('AWS_SERVICE_NAME', default='s3')
    AWS_LOCAL_STORAGE = f"{BASE_DIR}/storage/aws/"
