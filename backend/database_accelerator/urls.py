from django.urls import path, include

urlpatterns = [
    path('api/accelerator/', include('database_accelerator.apps.api_gateway.urls')),
    path('api/upload/', include('database_accelerator.apps.upload_module.urls')),
    path('api/analyze/', include('database_accelerator.apps.analysis_module.urls')),
    path('api/preprocess/', include('database_accelerator.apps.preprocessing_module.urls')),
    path('api/intelligence/', include('database_accelerator.apps.intelligence_module.urls')),
    path('api/reports/', include('database_accelerator.apps.report_module.urls')),
    path('api/export/', include('database_accelerator.apps.export_module.urls')),
]

