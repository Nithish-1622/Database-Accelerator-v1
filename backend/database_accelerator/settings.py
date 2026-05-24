import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = 'django-insecure-development-key-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
    'rest_framework',
    'corsheaders',
    'database_accelerator.apps.api_gateway',
    'database_accelerator.apps.upload_module',
    'database_accelerator.apps.analysis_module',
    'database_accelerator.apps.preprocessing_module',
    'database_accelerator.apps.intelligence_module',
    'database_accelerator.apps.report_module',
    'database_accelerator.apps.export_module',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'database_accelerator.urls'

TEMPLATES = []

WSGI_APPLICATION = 'database_accelerator.wsgi.application'

# Filesystem-based storage - No database
DATABASES = {}

# No authentication - filesystem-based storage

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'UNAUTHENTICATED_USER': None,
    'UNAUTHENTICATED_TOKEN': None,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True

# Filesystem Storage Paths
BASE_UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
UPLOAD_RAW_DIR = os.path.join(BASE_UPLOAD_DIR, 'raw')
UPLOAD_PROCESSED_DIR = os.path.join(BASE_UPLOAD_DIR, 'processed')
UPLOAD_TEMP_DIR = os.path.join(BASE_UPLOAD_DIR, 'temp')
UPLOAD_FAILED_DIR = os.path.join(BASE_UPLOAD_DIR, 'failed')

EXPORT_DIR = os.path.join(BASE_DIR, 'exports')
EXPORT_CLEANED_CSV_DIR = os.path.join(EXPORT_DIR, 'cleaned_csv')
EXPORT_JSON_REPORTS_DIR = os.path.join(EXPORT_DIR, 'json_reports')
EXPORT_LOGS_DIR = os.path.join(EXPORT_DIR, 'logs')

REPORT_DIR = os.path.join(BASE_DIR, 'reports')
REPORT_HEALTH_DIR = os.path.join(REPORT_DIR, 'health_reports')
REPORT_CLEANING_DIR = os.path.join(REPORT_DIR, 'cleaning_reports')
REPORT_INTELLIGENCE_DIR = os.path.join(REPORT_DIR, 'intelligence_reports')

# Create directories if they don't exist
for directory in [
    UPLOAD_RAW_DIR, UPLOAD_PROCESSED_DIR, UPLOAD_TEMP_DIR, UPLOAD_FAILED_DIR,
    EXPORT_CLEANED_CSV_DIR, EXPORT_JSON_REPORTS_DIR, EXPORT_LOGS_DIR,
    REPORT_HEALTH_DIR, REPORT_CLEANING_DIR, REPORT_INTELLIGENCE_DIR
]:
    os.makedirs(directory, exist_ok=True)
