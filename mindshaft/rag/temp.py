import os
import json
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import islice
from .models import Document
from langchain.schema import Document


# Directory paths and constants
CHROMA_DB_DIR = os.path.join(settings.BASE_DIR, 'rag', 'chroma_db')
PROCESSED_DOCS_DIR = os.path.join(settings.BASE_DIR, 'rag', 'processed_docs')
MAX_BATCH_SIZE = 20000  # Chroma's maximum allowed batch size
THREAD_POOL_SIZE = 10   # Number of threads to use

# Ensure directories exist
os.makedirs(PROCESSED_DOCS_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

def chunk_data(iterable, batch_size):
    """Yield successive batches of data."""
    iterator = iter(iterable)
    while batch := list(islice(iterator, batch_size)):
        yield batch

def save_processed_document(doc_id, pages):
    """Save processed document pages with metadata to a JSON file."""
    try:
        file_path = os.path.join(PROCESSED_DOCS_DIR, f"{doc_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([page.dict() if hasattr(page, "dict") else page for page in pages], f)
        print(f"Document {doc_id} saved successfully.")
    except Exception as e:
        print(f"Error saving document {doc_id}: {e}")


def load_processed_documents():
    """Load all processed documents from JSON files and convert them to LangChain Document objects."""
    documents = []
    for file_name in os.listdir(PROCESSED_DOCS_DIR):
        file_path = os.path.join(PROCESSED_DOCS_DIR, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            pages = json.load(f)
            for page in pages:
                # Convert each dictionary into a LangChain Document object
                documents.append(Document(page_content=page.get("page_content", ""), metadata=page.get("metadata", {})))
    print(f"Loaded {len(documents)} pages from processed documents.")
    return documents


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

        save_processed_document(doc_id, pages)
        print(f"Processed document ID {doc_id} with {len(pages)} pages.")
        return pages
    except Exception as e:
        print(f"Error processing document ID {doc.id}: {e}")
        return []

def ingest_documents():
    """
    Check if processed documents exist. If they do, skip processing and move directly to embeddings.
    If not, process documents, save them, and proceed to embeddings.
    """
    # Check if processed documents exist
    # if os.listdir(PROCESSED_DOCS_DIR):
    #     print("Processed documents found. Skipping document processing.")
    # else:
    print("No processed documents found. Processing documents...")
    # Process all documents using multithreading
    with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
        future_to_doc = {executor.submit(process_document, doc): doc for doc in Document.objects.all()}

        for future in as_completed(future_to_doc):
            try:
                future.result()
            except Exception as e:
                print(f"Error in document processing thread: {e}")

    # Load processed documents
    documents = load_processed_documents()

    if documents:
        # Initialize embeddings and Chroma vector store
        embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY, model='text-embedding-ada-002')
        vector_store = Chroma(
            collection_name='documents',
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embeddings
        )

        for chunk in chunk_data(documents, MAX_BATCH_SIZE):
            vector_store.add_documents(chunk)
            print(f"Ingested {len(chunk)} documents into Chroma DB.")
        print("All documents successfully ingested into Chroma DB.")
    else:
        # If no documents, clear the vector store
        if os.path.exists(CHROMA_DB_DIR):
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
