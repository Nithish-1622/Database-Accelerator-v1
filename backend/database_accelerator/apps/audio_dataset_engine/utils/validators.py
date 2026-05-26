from pathlib import Path

from django.conf import settings


def validate_audio_file(uploaded_file):
    name = getattr(uploaded_file, 'name', '') or ''
    suffix = Path(name).suffix.lower()
    if suffix not in settings.AUDIO_UPLOAD_ALLOWED_EXTENSIONS:
        return {
            'valid': False,
            'message': 'Unsupported audio format. Allowed formats are wav, mp3, flac, and m4a.',
        }

    size = int(getattr(uploaded_file, 'size', 0) or 0)
    if size <= 0:
        return {'valid': False, 'message': 'Audio file is empty.'}

    if size > settings.AUDIO_UPLOAD_MAX_SIZE_BYTES:
        return {
            'valid': False,
            'message': f'Audio file exceeds the maximum size of {settings.AUDIO_UPLOAD_MAX_SIZE_MB} MB.',
        }

    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if content_type and content_type not in settings.AUDIO_UPLOAD_ALLOWED_CONTENT_TYPES:
        return {
            'valid': False,
            'message': f'Unsupported content type: {content_type}.',
        }

    return {'valid': True, 'message': 'ok'}