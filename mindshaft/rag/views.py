from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .models import Document, IngestionStatus
from .serializers import DocumentSerializer
from .utils import ingest_documents

class DocumentUploadView(APIView):
    """
    View to upload new documents.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        # Check if ingestion is in progress
        ingestion_status = IngestionStatus.get_status()
        if ingestion_status.is_ingesting:
            return Response({'error': 'Ingestion is in progress. Please wait until it completes.'}, status=status.HTTP_400_BAD_REQUEST)

        # Handle multiple files
        files = request.FILES.getlist('file')
        titles = request.data.getlist('title')

        if not files or not titles:
            return Response({'error': 'No files or titles provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(files) != len(titles):
            return Response({'error': 'The number of files and titles must match.'}, status=status.HTTP_400_BAD_REQUEST)

        # Save documents
        documents = []
        for file, title in zip(files, titles):
            document = Document(title=title, file=file)
            document.save()
            documents.append(document)

        self.run_ingestion()

        return Response({'message': 'Documents uploaded successfully. Ingestion completed.'}, status=status.HTTP_201_CREATED)

    def run_ingestion(self):
        ingestion_status = IngestionStatus.get_status()
        ingestion_status.is_ingesting = True
        ingestion_status.save()

        try:
            ingest_documents()
        finally:
            ingestion_status.is_ingesting = False
            ingestion_status.save()

class DocumentDeleteView(APIView):
    """
    View to delete a document.
    """
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        # Check if ingestion is in progress
        ingestion_status = IngestionStatus.get_status()
        if ingestion_status.is_ingesting:
            return Response({'error': 'Ingestion is in progress. Please wait until it completes.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            document = Document.objects.get(pk=pk)
            document.delete()

            # Start ingestion in a new thread
            ingest_documents()
            return Response({'message': 'Document deleted successfully. Ingestion completed.'}, status=status.HTTP_200_OK)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found.'}, status=status.HTTP_404_NOT_FOUND)

    def run_ingestion(self):
        ingestion_status = IngestionStatus.get_status()
        ingestion_status.is_ingesting = True
        ingestion_status.save()

        try:
            from .utils import ingest_documents
            ingest_documents()
        finally:
            ingestion_status.is_ingesting = False
            ingestion_status.save()
