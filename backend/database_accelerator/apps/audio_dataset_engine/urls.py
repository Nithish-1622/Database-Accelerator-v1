from django.urls import path

from .views import (
    AudioTranscriptView,
    AudioUploadStatusView,
    AudioUploadView,
    AudioKeywordView,
    AudioKeywordsListView,
    AudioFrequenciesView,
    AudioFrequenciesComputeView,
    AudioClusterView,
    AudioExportView,
)


urlpatterns = [
    path('upload/', AudioUploadView.as_view(), name='audio-upload'),
    path('status/<uuid:audio_id>/', AudioUploadStatusView.as_view(), name='audio-status'),
    path('transcript/', AudioTranscriptView.as_view(), name='audio-transcript'),
    path('keywords/', AudioKeywordView.as_view(), name='audio-keyword-extract'),
    path('keywords/list/', AudioKeywordsListView.as_view(), name='audio-keyword-list'),
    path('frequencies/', AudioFrequenciesView.as_view(), name='audio-frequencies'),
    path('frequencies/compute/', AudioFrequenciesComputeView.as_view(), name='audio-frequencies-compute'),
    path('clusters/', AudioClusterView.as_view(), name='audio-cluster'),
    path('export/<uuid:audio_id>/<str:dataset_type>/<str:fmt>/', AudioExportView.as_view(), name='audio-export'),
]
