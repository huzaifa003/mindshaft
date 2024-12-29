from django.urls import path
from .views import DocumentUploadView, ScanAndUploadFolderView, DocumentDeleteView, DocumentsListView

urlpatterns = [
    path('documents/view/', DocumentsListView.as_view(), name='document-view'),
    path('documents/upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('documents/<int:pk>/delete/', DocumentDeleteView.as_view(), name='document-delete'),
    path('documents/scan-upload/', ScanAndUploadFolderView.as_view(), name='scan-upload'),

]