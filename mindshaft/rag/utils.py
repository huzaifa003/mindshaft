import os
from django.conf import settings
from .models import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

# Directory to store Chroma DB
CHROMA_DB_DIR = os.path.join(settings.BASE_DIR, 'rag', 'chroma_db')


def ingest_documents():
    """
    Process uploaded documents, extract text, split into chunks, associate titles, create embeddings, and store in Chroma DB.
    """
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    documents = []

    for doc in Document.objects.all():
        file_path = doc.file.path
        id = str(doc.id)  # Retrieve the id from the database
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()

        # Add the id as metadata to each page
        for page in pages:
            if isinstance(page, dict):
                page['metadata'] = {'id': id}
            elif hasattr(page, 'metadata'):
                page.metadata = {'id': id}

        documents.extend(pages)

    if documents:
        # Initialize embeddings and Chroma vector store
        embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY, model='text-embedding-ada-002')
        vector_store = Chroma(
            collection_name='documents',
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embeddings
        )
        # Add documents with titles to the vector store
        vector_store.add_documents(documents)
    else:
        # If no documents, clear the vector store
        if os.path.exists(CHROMA_DB_DIR):
            import shutil
            shutil.rmtree(CHROMA_DB_DIR)
        print("No documents to ingest.")



def get_relevant_context(query):
    """
    Retrieve relevant context from Chroma DB based on the user's message.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY, model='text-embedding-ada-002')
    vector_store = Chroma(
        collection_name='documents',
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )
    docs = vector_store.similarity_search(query, k=3)
    context = "\n".join([doc.page_content for doc in docs])
    return context
