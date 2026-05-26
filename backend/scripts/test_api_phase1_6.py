import os
import sys
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'database_accelerator.settings')
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import django
django.setup()

from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from database_accelerator.apps.audio_dataset_engine.models import AudioUpload, KeywordModel, FrequencyModel, ClusterModel, ClusterMember, TranscriptModel


def main():
    client = Client()

    # Phase 1: Upload
    sample_bytes = b'RIFF' + b'\x00' * 1024
    audio_file = SimpleUploadedFile('test.wav', sample_bytes, content_type='audio/wav')
    resp = client.post('/api/audio/upload/', {'audio_file': audio_file})
    assert resp.status_code in (200, 201), f'upload failed: {resp.status_code} {resp.content}'
    audio_data = resp.json()
    audio_id = audio_data.get('id')
    print('uploaded', audio_id)

    # Phase 1.5: Status
    resp = client.get(f'/api/audio/status/{audio_id}/')
    assert resp.status_code == 200, f'status failed: {resp.status_code}'

    # Phase 3: Transcription (use override)
    transcript_text = 'hello world this is a test transcript about database and AI and testing'
    resp = client.post('/api/audio/transcript/', {'audio_id': audio_id, 'transcript_override': transcript_text})
    assert resp.status_code in (200, 201), f'transcript failed: {resp.status_code} {resp.content}'
    tr = resp.json()
    print('transcript created', tr.get('id'))

    # Phase 4: Keyword extraction via endpoint
    resp = client.post('/api/audio/keywords/', {'audio_id': audio_id, 'text': transcript_text})
    assert resp.status_code in (200, 201), f'keyword extract failed: {resp.status_code} {resp.content}'
    kw_res = resp.json()
    print('keywords extracted count=', len(kw_res.get('keywords', [])))

    # Phase 5: Frequencies list and compute
    resp = client.get(f'/api/audio/frequencies/?audio_id={audio_id}')
    assert resp.status_code == 200, f'frequencies list failed: {resp.status_code}'
    resp = client.get(f'/api/audio/frequencies/compute/?audio_id={audio_id}&top_k=10')
    assert resp.status_code == 200, f'frequencies compute failed: {resp.status_code}'
    print('frequencies compute OK')

    # Phase 6: Clustering
    resp = client.post('/api/audio/clusters/', {'audio_id': audio_id, 'n_clusters': 2})
    assert resp.status_code in (200, 201), f'clustering failed: {resp.status_code} {resp.content}'
    cl = resp.json()
    print('cluster created', cl.get('cluster_id'))

    # verify DB entries exist
    assert AudioUpload.objects.filter(id=audio_id).exists()
    assert TranscriptModel.objects.filter(audio_id=audio_id).exists()
    assert KeywordModel.objects.filter(audio_id=audio_id).exists()
    assert FrequencyModel.objects.filter(audio_id=audio_id).exists()
    assert ClusterModel.objects.filter(audio_id=audio_id).exists()

    print('ALL_PHASES_VALIDATION_OK')

    # cleanup
    ClusterMember.objects.filter(cluster__audio_id=audio_id).delete()
    ClusterModel.objects.filter(audio_id=audio_id).delete()
    KeywordModel.objects.filter(audio_id=audio_id).delete()
    FrequencyModel.objects.filter(audio_id=audio_id).delete()
    TranscriptModel.objects.filter(audio_id=audio_id).delete()
    AudioUpload.objects.filter(id=audio_id).delete()


if __name__ == '__main__':
    main()
