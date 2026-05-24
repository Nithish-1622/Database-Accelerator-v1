import json
import os

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from database_accelerator.apps.export_module.export_engine import export_cleaned_dataset
from database_accelerator.apps.export_module.serializers import ExportReportSerializer


class DatasetExportView(APIView):
    def post(self, request, dataset_id, format=None):
        try:
            export_report = export_cleaned_dataset(dataset_id)
            serializer = ExportReportSerializer(export_report)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class DatasetExportReportView(APIView):
    def get(self, request, dataset_id, format=None):
        report_path = os.path.join(settings.EXPORT_JSON_REPORTS_DIR, f'{dataset_id}.json')

        if not os.path.exists(report_path):
            return Response({'error': 'Export report not found'}, status=status.HTTP_404_NOT_FOUND)

        with open(report_path, 'r', encoding='utf-8') as report_file:
            export_report = json.load(report_file)

        serializer = ExportReportSerializer(export_report)
        return Response(serializer.data, status=status.HTTP_200_OK)