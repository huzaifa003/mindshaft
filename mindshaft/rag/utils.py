import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from django.conf import settings
from .models import Document  # Import your Django model
from langchain.schema import Document as LangChainDocument  # Rename to avoid conflicts

# Directory to store Chroma DB
CHROMA_DB_DIR = os.path.join(settings.BASE_DIR, 'rag', 'chroma_db')

def process_document(doc):
    """Process a single document: extract text, split into pages, and add metadata."""
    try:
        file_path = doc.file.path
        doc_id = str(doc.id)
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()

        # Add the doc_id as metadata to each page
        for page in pages:
            if isinstance(page, dict):
                page['metadata'] = {'id': doc_id}
            elif hasattr(page, 'metadata'):
                page.metadata = {'id': doc_id}

        print(f"Processed document ID {doc_id} with {len(pages)} pages.")
        return pages
    except Exception as e:
        print(f"Error processing document ID {doc.id}: {e}")
        return []

def ingest_documents(batch_size=10, max_threads=4):
    """
    Process uploaded documents in parallel, extract text, split into chunks, create embeddings, and store in Chroma DB.
    """
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    all_documents = Document.objects.all()

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(process_document, doc): doc for doc in all_documents}
        processed_pages = []

        for future in as_completed(futures):
            try:
                pages = future.result()
                processed_pages.extend(pages)
            except Exception as e:
                doc = futures[future]
                print(f"Error processing document ID {doc.id}: {e}")

    if processed_pages:
        # Process in batches to limit memory usage
        for i in range(0, len(processed_pages), batch_size):
            batch = processed_pages[i:i + batch_size]
            add_documents_to_chroma(batch)
    else:
        # If no documents, clear the vector store
        clear_chroma_db()

def add_documents_to_chroma(documents):
    """
    Add documents to Chroma DB.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY, model='text-embedding-ada-002')
    vector_store = Chroma(
        collection_name='documents',
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embeddings
    )
    vector_store.add_documents(documents)

def clear_chroma_db():
    """
    Clear Chroma DB if no documents are available.
    """
    if os.path.exists(CHROMA_DB_DIR):
        shutil.rmtree(CHROMA_DB_DIR)
    print("No documents to ingest. Cleared Chroma DB.")



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
