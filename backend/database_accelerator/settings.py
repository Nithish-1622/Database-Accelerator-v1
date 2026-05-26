import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV_PATHS = [
    BASE_DIR / 'backend' / '.env',
    BASE_DIR / '.env',
]

for env_path in ENV_PATHS:
    if env_path.exists():
        load_dotenv(env_path, override=False)
        break

SECRET_KEY = 'django-insecure-development-key-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

INSTALLED_APPS = [
    'rest_framework',
    'corsheaders',
    'database_accelerator.apps.api_gateway',
    'database_accelerator.apps.upload_module',
    'database_accelerator.apps.audio_dataset_engine.apps.AudioDatasetEngineConfig',
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

def _database_config_from_env():
    engine = os.getenv('DB_ENGINE', 'django.db.backends.postgresql')
    name = os.getenv('DB_NAME', 'database_accelerator')
    user = os.getenv('DB_USER', 'database_accelerator')
    password = os.getenv('DB_PASSWORD', 'database_accelerator')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')

    return {
        'default': {
            'ENGINE': engine,
            'NAME': name,
            'USER': user,
            'PASSWORD': password,
            'HOST': host,
            'PORT': port,
            'CONN_MAX_AGE': 60,
            'OPTIONS': {
                'sslmode': os.getenv('DB_SSLMODE', 'prefer'),
            },
        }
    }


DATABASES = _database_config_from_env()

# Metadata and operational state are stored in PostgreSQL; large dataset files remain on disk.

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AUDIO_UPLOAD_MAX_SIZE_MB = int(os.getenv('AUDIO_UPLOAD_MAX_SIZE_MB', '100'))
AUDIO_UPLOAD_MAX_SIZE_BYTES = AUDIO_UPLOAD_MAX_SIZE_MB * 1024 * 1024
AUDIO_UPLOAD_ALLOWED_EXTENSIONS = {'.wav', '.mp3', '.flac', '.m4a'}
AUDIO_UPLOAD_ALLOWED_CONTENT_TYPES = {
    'audio/wav',
    'audio/x-wav',
    'audio/mpeg',
    'audio/mp3',
    'audio/flac',
    'audio/x-flac',
    'audio/mp4',
    'audio/x-m4a',
    'audio/m4a',
}

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
    REPORT_HEALTH_DIR, REPORT_CLEANING_DIR, REPORT_INTELLIGENCE_DIR,
    MEDIA_ROOT,
    os.path.join(MEDIA_ROOT, 'audio'),
]:
    os.makedirs(directory, exist_ok=True)
