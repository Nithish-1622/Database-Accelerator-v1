from django.urls import path

from .views import DatasetPreprocessReportView, DatasetPreprocessView

urlpatterns = [
    path('<str:dataset_id>/', DatasetPreprocessView.as_view(), name='dataset-preprocess'),
    path('<str:dataset_id>/report/', DatasetPreprocessReportView.as_view(), name='dataset-preprocess-report'),
]