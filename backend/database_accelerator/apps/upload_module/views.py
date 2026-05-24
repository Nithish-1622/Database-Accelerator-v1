from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import DatasetSerializer, DatasetUploadSerializer
from .models import dataset_manager


class DatasetUploadView(APIView):
    """
    API endpoint for dataset upload
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        """
        Upload a dataset file
        POST /api/upload/upload/
        """
        serializer = DatasetUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            result = serializer.save()
            
            if result.get('success'):
                return Response(
                    result['dataset'],
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'error': result.get('message', 'Unknown error')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class DatasetMetadataView(APIView):
    """
    Get dataset metadata by ID
    """
    
    def get(self, request, dataset_id, format=None):
        """
        GET /api/upload/{id}/metadata/
        """
        metadata = dataset_manager.get(dataset_id)
        
        if metadata:
            serializer = DatasetSerializer(metadata)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Dataset not found'},
            status=status.HTTP_404_NOT_FOUND
        )


class DatasetListView(APIView):
    """
    List all datasets
    """
    
    def get(self, request, format=None):
        """
        GET /api/upload/list_datasets/
        """
        datasets = dataset_manager.list_all()
        
        return Response({
            'count': len(datasets),
            'datasets': datasets
        })

