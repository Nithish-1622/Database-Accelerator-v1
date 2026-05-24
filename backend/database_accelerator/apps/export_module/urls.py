from django.urls import path

from .views import DatasetExportReportView, DatasetExportView

urlpatterns = [
    path('<str:dataset_id>/', DatasetExportView.as_view(), name='dataset-export'),
    path('<str:dataset_id>/report/', DatasetExportReportView.as_view(), name='dataset-export-report'),
]