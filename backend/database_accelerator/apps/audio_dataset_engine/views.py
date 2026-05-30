from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AudioUploadCreateSerializer, AudioUploadSerializer, TranscriptRequestSerializer, TranscriptSerializer
from .services.upload_service import AudioUploadService
from .services.transcription_service import TranscriptionService
from .services.keyword_service import KeywordService
from .serializers import KeywordSerializer, FrequencySerializer
from .services.frequency_service import FrequencyService
from .services.clustering_service import ClusteringService
from .serializers import ClusterSerializer, ClusterMemberSerializer
from .exports import exporter
from django.http import FileResponse, HttpResponse
import io


class AudioUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        serializer = AudioUploadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = AudioUploadService.register_upload(serializer.validated_data['audio_file'])
        if not result['success']:
            return Response({'error': result['message']}, status=status.HTTP_400_BAD_REQUEST)

        return Response(AudioUploadSerializer(result['record']).data, status=status.HTTP_201_CREATED)


class AudioUploadStatusView(APIView):
    def get(self, request, audio_id, format=None):
        record = AudioUploadService.get_upload(audio_id)
        if not record:
            return Response({'error': 'Audio upload not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AudioUploadSerializer(record).data)


class AudioTranscriptView(APIView):
    def get(self, request, format=None):
        audio_id = request.query_params.get('audio_id')
        if not audio_id:
            return Response({'error': 'audio_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        transcripts = TranscriptionService.list_transcripts(audio_id=audio_id)
        return Response({
            'count': transcripts.count(),
            'results': TranscriptSerializer(transcripts, many=True).data,
        })

    def post(self, request, format=None):
        serializer = TranscriptRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = TranscriptionService.transcribe_audio(
            audio_id=serializer.validated_data['audio_id'],
            transcript_override=serializer.validated_data.get('transcript_override'),
            model_name=serializer.validated_data.get('model_name', 'whisper-small'),
        )

        if not result['success']:
            return Response({'error': result['message']}, status=status.HTTP_404_NOT_FOUND)

        return Response(TranscriptSerializer(result['transcript']).data, status=status.HTTP_201_CREATED)


class AudioKeywordView(APIView):
    def post(self, request, format=None):
        audio_id = request.data.get('audio_id')
        text = request.data.get('text')
        if not audio_id or text is None:
            return Response({'error': 'audio_id and text are required'}, status=status.HTTP_400_BAD_REQUEST)

        result = KeywordService.extract_and_store(audio_id, text)
        if not result['success']:
            return Response({'error': result.get('message', 'failed')}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'keywords': result['keywords']}, status=status.HTTP_201_CREATED)


class AudioFrequenciesView(APIView):
    def get(self, request, format=None):
        audio_id = request.query_params.get('audio_id')
        freqs = KeywordService.list_frequencies(audio_id=audio_id)
        return Response({'count': freqs.count(), 'results': FrequencySerializer(freqs, many=True).data})


class AudioKeywordsListView(APIView):
    def get(self, request, format=None):
        audio_id = request.query_params.get('audio_id')
        kws = KeywordService.list_keywords(audio_id=audio_id)
        return Response({'count': kws.count(), 'results': KeywordSerializer(kws, many=True).data})


class AudioFrequenciesComputeView(APIView):
    def get(self, request, format=None):
        audio_id = request.query_params.get('audio_id')
        top_k = int(request.query_params.get('top_k', 50))
        top = FrequencyService.compute_top_k(audio_id, top_k)
        hist = FrequencyService.compute_term_histogram(audio_id)
        co = FrequencyService.compute_cooccurrence(audio_id)
        return Response({'top': top, 'histogram': hist, 'cooccurrence_count': len(co)})


class AudioClusterView(APIView):
    def post(self, request, format=None):
        audio_id = request.data.get('audio_id')
        n_clusters = int(request.data.get('n_clusters', ClusteringService.DEFAULT_N_CLUSTERS))
        algorithm = request.data.get('algorithm', 'kmeans')
        eps = float(request.data.get('eps', 0.5))
        min_samples = int(request.data.get('min_samples', 2))
        if not audio_id:
            return Response({'error': 'audio_id required'}, status=status.HTTP_400_BAD_REQUEST)
        res = ClusteringService.cluster_keywords(
            audio_id,
            n_clusters=n_clusters,
            algorithm=algorithm,
            eps=eps,
            min_samples=min_samples,
        )
        if not res.get('success'):
            return Response({'error': res.get('message', 'failed')}, status=status.HTTP_400_BAD_REQUEST)
        return Response(res, status=status.HTTP_201_CREATED)


class AudioExportView(APIView):
    def get(self, request, audio_id, dataset_type, fmt, format=None):
        try:
            data_bytes, content_type, filename = exporter.build_export(audio_id, dataset_type, fmt)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if fmt == 'json':
            return HttpResponse(data_bytes, content_type=content_type)

        return FileResponse(io.BytesIO(data_bytes), filename=filename, content_type=content_type)

