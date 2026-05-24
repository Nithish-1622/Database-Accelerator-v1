from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from database_accelerator.apps.report_module.report_engine import get_combined_report, list_report_ids
from database_accelerator.apps.report_module.serializers import CombinedReportSerializer, ReportListSerializer


class DatasetReportView(APIView):
    def get(self, request, dataset_id, format=None):
        report = get_combined_report(dataset_id)

        if not report['analysis_report'] and not report['cleaning_report']:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CombinedReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportListView(APIView):
    def get(self, request, format=None):
        report_ids = list_report_ids()
        serializer = ReportListSerializer({'report_ids': report_ids})
        return Response(serializer.data, status=status.HTTP_200_OK)