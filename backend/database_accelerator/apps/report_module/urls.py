from django.urls import path

from .views import DatasetReportView, ReportListView

urlpatterns = [
    path('list/', ReportListView.as_view(), name='report-list'),
    path('<str:dataset_id>/', DatasetReportView.as_view(), name='dataset-report'),
]