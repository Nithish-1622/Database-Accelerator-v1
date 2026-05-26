import os
import sys
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database_accelerator.settings')
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import django
django.setup()

from database_accelerator.apps.audio_dataset_engine.services.keyword_service import KeywordService
from database_accelerator.apps.audio_dataset_engine.services.clustering_service import ClusteringService
from database_accelerator.apps.audio_dataset_engine.services.upload_service import AudioUploadService


def main():
    from django.core.files.uploadedfile import SimpleUploadedFile
    sample = SimpleUploadedFile('s.wav', b'RIFF' + b'\x00' * 256, content_type='audio/wav')
    res = AudioUploadService.register_upload(sample)
    audio = res['record']
    text = 'cat dog cat mouse dog elephant cat'
    KeywordService.extract_and_store(audio.id, text)

    res = ClusteringService.cluster_keywords(audio.id, n_clusters=2)
    if not res.get('success'):
        raise SystemExit('Clustering failed: %s' % res.get('message'))
    print('VALIDATION_OK')
    print('cluster_id=', res.get('cluster_id'))
    print('labels=', res.get('labels'))

    # cleanup
    from database_accelerator.apps.audio_dataset_engine.models import ClusterModel, ClusterMember
    ClusterMember.objects.filter(cluster__audio=audio).delete()
    ClusterModel.objects.filter(audio=audio).delete()
    from database_accelerator.apps.audio_dataset_engine.models import KeywordModel, FrequencyModel
    KeywordModel.objects.filter(audio=audio).delete()
    FrequencyModel.objects.filter(audio=audio).delete()
    audio.delete()


if __name__ == '__main__':
    main()
