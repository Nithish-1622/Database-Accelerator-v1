import json
import os

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from database_accelerator.apps.analysis_module.analysis_engine import analyze_dataset, save_analysis_report
from database_accelerator.apps.analysis_module.serializers import AnalysisReportSerializer
from database_accelerator.apps.upload_module.models import dataset_manager
from django.conf import settings


class DatasetAnalysisView(APIView):
    def post(self, request, dataset_id, format=None):
        metadata = dataset_manager.get(dataset_id)

        if not metadata:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            dataset_manager.update_status(dataset_id, 'processing')
            report = analyze_dataset(metadata)
            save_analysis_report(report)
            dataset_manager.update_status(dataset_id, 'analyzed')

            serializer = AnalysisReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            dataset_manager.update_status(dataset_id, 'error', str(exc))
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class DatasetAnalysisReportView(APIView):
    def get(self, request, dataset_id, format=None):
        report_path = os.path.join(settings.REPORT_HEALTH_DIR, f'{dataset_id}.json')

        if not os.path.exists(report_path):
            return Response({'error': 'Analysis report not found'}, status=status.HTTP_404_NOT_FOUND)

        with open(report_path, 'r', encoding='utf-8') as report_file:
            report = json.load(report_file)

        serializer = AnalysisReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)