import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from django.conf import settings
from .models import Document  # Import your Django model
from langchain.schema import Document as LangChainDocument  # Rename to avoid conflicts
import tiktoken

# Directory to store Chroma DB
CHROMA_DB_DIR = os.path.join(settings.BASE_DIR, 'rag', 'chroma_db')

# Define the maximum tokens allowed per chunk
MAX_TOKENS = 1000  # Adjust as needed

def chunk_text_with_tiktoken(text, max_tokens=MAX_TOKENS, model='text-embedding-ada-002'):
    """
    Use tiktoken to split text into chunks of specified token size.
    """
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    # Split tokens into chunks of max_tokens
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i+max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        yield chunk_text

def process_document(doc):
    """Process a single document: extract text, split into pages, then chunk each page using tiktoken."""
    try:
        file_path = doc.file.path
        doc_id = str(doc.id)
        loader = PyPDFLoader(file_path)
        pages = loader.load()  # Load pages without pre-splitting

        processed_pages = []
        for page in pages:
            # page.page_content should have the text of the page
            page_text = page.page_content
            # Chunk the page text using tiktoken
            for chunk in chunk_text_with_tiktoken(page_text, max_tokens=MAX_TOKENS):
                # Create a new LangChainDocument with the chunk
                chunked_page = LangChainDocument(
                    page_content=chunk,
                    metadata={'id': doc_id, 'source_file': doc.file.name}
                )
                processed_pages.append(chunked_page)

        print(f"Processed document ID {doc_id} into {len(processed_pages)} chunked pages.")
        return processed_pages
    except Exception as e:
        print(f"Error processing document ID {doc.id}: {e}")
        return []

def ingest_documents(max_threads=4):
    """
    Process uploaded documents in parallel, extract text, chunk with tiktoken, 
    create embeddings, and store in Chroma DB immediately after each document is processed.
    """
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    all_documents = Document.objects.all()

    documents_added = False

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(process_document, doc): doc for doc in all_documents}

        for future in as_completed(futures):
            try:
                chunks = future.result()
                if chunks:
                    # As soon as we have chunks, add them to Chroma DB
                    add_documents_to_chroma(chunks)
                    print(f"Added {len(chunks)} chunks to Chroma DB.")
                    documents_added = True
            except Exception as e:
                doc = futures[future]
                print(f"Error processing document ID {doc.id}: {e}")

    if not documents_added:
        # If no documents were processed or no chunks created, clear the vector store
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
