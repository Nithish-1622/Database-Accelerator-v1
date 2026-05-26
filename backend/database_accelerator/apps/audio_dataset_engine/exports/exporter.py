import io
import csv
import json
from datetime import datetime
from django.utils import timezone

from ..models import KeywordModel, FrequencyModel, ClusterModel, ClusterMember


def _keywords_rows(audio_id):
    qs = KeywordModel.objects.filter(audio_id=audio_id).order_by('-frequency')
    for k in qs:
        yield {'keyword': k.keyword, 'frequency': k.frequency, 'timestamps': k.timestamps, 'created_at': k.created_at.isoformat()}


def _frequencies_rows(audio_id):
    qs = FrequencyModel.objects.filter(audio_id=audio_id).order_by('-count')
    for f in qs:
        yield {'keyword': f.keyword, 'count': f.count, 'created_at': f.created_at.isoformat()}


def _clusters_rows(audio_id):
    clusters = ClusterModel.objects.filter(audio_id=audio_id).order_by('created_at')
    for c in clusters:
        members = c.members.all()
        for m in members:
            yield {'cluster_id': str(c.id), 'algorithm': c.algorithm, 'keyword': m.keyword_text or (m.keyword.keyword if m.keyword else ''), 'weight': m.weight}


def _to_csv_bytes(rows, fieldnames):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return buf.getvalue().encode('utf-8')


def _to_json_bytes(rows):
    return json.dumps(list(rows), default=str, ensure_ascii=False).encode('utf-8')


def _to_xlsx_bytes(rows, fieldnames):
    try:
        import openpyxl
        from openpyxl.utils import get_column_letter
    except Exception:
        raise RuntimeError('XLSX export requires openpyxl installed')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(fieldnames)
    for r in rows:
        ws.append([r.get(f, '') for f in fieldnames])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def build_export(audio_id, dataset_type, fmt):
    dataset_type = dataset_type.lower()
    fmt = fmt.lower()

    if dataset_type == 'keywords':
        rows = list(_keywords_rows(audio_id))
        fieldnames = ['keyword', 'frequency', 'timestamps', 'created_at']
        base = 'keywords'
    elif dataset_type == 'frequencies':
        rows = list(_frequencies_rows(audio_id))
        fieldnames = ['keyword', 'count', 'created_at']
        base = 'frequencies'
    elif dataset_type == 'clusters':
        rows = list(_clusters_rows(audio_id))
        fieldnames = ['cluster_id', 'algorithm', 'keyword', 'weight']
        base = 'clusters'
    else:
        raise ValueError('dataset_type must be one of keywords, frequencies, clusters')

    ts = timezone.now().strftime('%Y%m%d%H%M%S')
    filename_base = f'{base}_{audio_id}_{ts}'

    if fmt == 'csv':
        data = _to_csv_bytes(rows, fieldnames)
        return data, 'text/csv', f'{filename_base}.csv'
    if fmt == 'json':
        data = _to_json_bytes(rows)
        return data, 'application/json', f'{filename_base}.json'
    if fmt == 'xlsx':
        data = _to_xlsx_bytes(rows, fieldnames)
        return data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', f'{filename_base}.xlsx'

    raise ValueError('fmt must be csv, json, or xlsx')
