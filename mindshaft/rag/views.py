from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Document, IngestionStatus
from .serializers import DocumentSerializer
from .utils import ingest_documents
from langchain_chroma import Chroma
import os
from django.conf import settings
from django.core.files import File

CHROMA_DB_DIR = os.path.join(settings.BASE_DIR, 'rag', 'chroma_db')

class DocumentUploadView(APIView):
    """
    View to upload new documents.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Check if ingestion is in progress
        ingestion_status = IngestionStatus.get_status()
        if ingestion_status.is_ingesting:
            return Response({'error': 'Ingestion is in progress. Please wait until it completes.'}, status=status.HTTP_400_BAD_REQUEST)

        # Handle multiple files
        files = request.FILES.getlist('file')

        if not files:
            return Response({'error': 'No files provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Save documents
        documents = []
        for file in files:
            # Extract the title from the file name (without extension)
            title = os.path.splitext(file.name)[0]
            document = Document(title=title, file=file)
            document.save()
            documents.append(document)

        # Start the ingestion process
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


#//TODO Change the permissions to admin only


class ScanAndUploadFolderView(APIView):
    """
    View to scan a folder and its subfolders for PDF files and upload them as documents.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the parent folder path from the request
        parent_folder = request.data.get('folder_path')

        if not parent_folder:
            return Response({'error': 'Please provide the folder path.'}, status=status.HTTP_400_BAD_REQUEST)

        if not os.path.exists(parent_folder):
            return Response({'error': 'The specified folder does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        if not os.path.isdir(parent_folder):
            return Response({'error': 'The specified path is not a folder.'}, status=status.HTTP_400_BAD_REQUEST)

        # Scan the folder for PDF files
        pdf_files = self.get_pdf_files(parent_folder)

        if not pdf_files:
            return Response({'message': 'No PDF files found in the specified folder or its subfolders.'}, status=status.HTTP_200_OK)

        # Upload the files as documents
        documents = []
        for pdf_file in pdf_files:
            title = os.path.splitext(os.path.basename(pdf_file))[0]  # Extract title from file name
            with open(pdf_file, 'rb') as file:
                wrapped_file = File(file)
                # Use only the file name, not the full path
                wrapped_file.name = os.path.basename(pdf_file)
                document = Document(title=title, file=wrapped_file)
                document.save()
                documents.append(document)

        # Run the ingestion process
        ingest_documents()

        return Response({
            'message': 'PDF files uploaded and ingested successfully.',
            'uploaded_files': [doc.title for doc in documents]
        }, status=status.HTTP_201_CREATED)

    def get_pdf_files(self, folder_path):
        """
        Recursively find all PDF files in the specified folder and its subfolders.
        """
        pdf_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    full_path = os.path.join(root, file)
                    print(f"Found PDF file: {full_path}")
                    pdf_files.append(full_path)
        return pdf_files



class DocumentDeleteView(APIView):
    """
    View to delete a document.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        # Check if ingestion is in progress
        ingestion_status = IngestionStatus.get_status()
        if ingestion_status.is_ingesting:
            return Response({'error': 'Ingestion is in progress. Please wait until it completes.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            document = Document.objects.get(pk=pk)
            if not document:
                return Response({'error': 'Document not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Start ingestion in a new thread
            if not os.path.exists(CHROMA_DB_DIR):
                self.run_ingestion()

            vector_store = Chroma(
                collection_name='documents',
                persist_directory=CHROMA_DB_DIR
            )
            vector_store.delete([str(pk)])

            os.remove(document.file.path)
            document.delete()
            return Response({'message': 'Document deleted successfully. Ingestion completed.'}, status=status.HTTP_200_OK)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found.'}, status=status.HTTP_404_NOT_FOUND)

    def run_ingestion(self):
        ingestion_status = IngestionStatus.get_status()
        ingestion_status.is_ingesting = True
        ingestion_status.save()

        try:
            ingest_documents()
        finally:
            ingestion_status.is_ingesting = False
            ingestion_status.save()


class DocumentsListView(APIView):
    """
    View to list all documents.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)