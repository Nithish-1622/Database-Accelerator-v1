from django.urls import path

from .views import DatasetIntelligenceReportView, DatasetIntelligenceView

urlpatterns = [
    path('<str:dataset_id>/', DatasetIntelligenceView.as_view(), name='dataset-intelligence'),
    path('<str:dataset_id>/report/', DatasetIntelligenceReportView.as_view(), name='dataset-intelligence-report'),
]