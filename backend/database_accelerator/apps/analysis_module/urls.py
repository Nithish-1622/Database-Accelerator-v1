from django.urls import path

from .views import DatasetAnalysisReportView, DatasetAnalysisView

urlpatterns = [
    path('<str:dataset_id>/', DatasetAnalysisView.as_view(), name='dataset-analysis'),
    path('<str:dataset_id>/report/', DatasetAnalysisReportView.as_view(), name='dataset-analysis-report'),
]