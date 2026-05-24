from django.urls import path

from .views import AcceleratorArtifactDownloadView, RunAcceleratorPipelineView

urlpatterns = [
    path('run/<str:dataset_id>/', RunAcceleratorPipelineView.as_view(), name='accelerator-run'),
    path('artifact/<str:dataset_id>/<str:artifact_name>/', AcceleratorArtifactDownloadView.as_view(), name='accelerator-artifact'),
]