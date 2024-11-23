from django.urls import path
from .views import DocumentUploadView, DocumentDeleteView

urlpatterns = [
    path('documents/upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('documents/<int:pk>/delete/', DocumentDeleteView.as_view(), name='document-delete'),
]