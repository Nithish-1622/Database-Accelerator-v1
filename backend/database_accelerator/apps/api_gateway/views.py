import os

from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from database_accelerator.apps.api_gateway.accelerator_engine import run_accelerator_pipeline
from database_accelerator.apps.api_gateway.serializers import AcceleratorPipelineSerializer


class RunAcceleratorPipelineView(APIView):
    def post(self, request, dataset_id, format=None):
        try:
            result = run_accelerator_pipeline(dataset_id)
            serializer = AcceleratorPipelineSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class AcceleratorArtifactDownloadView(APIView):
    def get(self, request, dataset_id, artifact_name, format=None):
        from django.conf import settings
        artifact_dir = os.path.join(settings.EXPORT_DIR, dataset_id)
        requested_path = os.path.join(artifact_dir, artifact_name)

        if not os.path.exists(requested_path):
            raise Http404('Artifact not found')

        return FileResponse(open(requested_path, 'rb'), as_attachment=True, filename=artifact_name)