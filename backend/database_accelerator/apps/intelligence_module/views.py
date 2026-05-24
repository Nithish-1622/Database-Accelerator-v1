import json
import os

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from database_accelerator.apps.intelligence_module.intelligence_engine import build_intelligence_report
from database_accelerator.apps.intelligence_module.serializers import IntelligenceReportSerializer


class DatasetIntelligenceView(APIView):
    def post(self, request, dataset_id, format=None):
        try:
            report = build_intelligence_report(dataset_id)
            serializer = IntelligenceReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class DatasetIntelligenceReportView(APIView):
    def get(self, request, dataset_id, format=None):
        report_path = os.path.join(settings.REPORT_INTELLIGENCE_DIR, f'{dataset_id}.json')

        if not os.path.exists(report_path):
            return Response({'error': 'Intelligence report not found'}, status=status.HTTP_404_NOT_FOUND)

        with open(report_path, 'r', encoding='utf-8') as report_file:
            report = json.load(report_file)

        serializer = IntelligenceReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)