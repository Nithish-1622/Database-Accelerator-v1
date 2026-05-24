from django.urls import path
from .views import DatasetUploadView, DatasetMetadataView, DatasetListView

urlpatterns = [
    path('upload/', DatasetUploadView.as_view(), name='dataset-upload'),
    path('<str:dataset_id>/metadata/', DatasetMetadataView.as_view(), name='dataset-metadata'),
    path('list_datasets/', DatasetListView.as_view(), name='dataset-list'),
]

