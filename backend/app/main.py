from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import chromadb
from chromadb.config import Settings
import os
import pandas as pd
from pathlib import Path
import ollama
from app.ollama_embeddings import OllamaEmbeddingFunction

app = FastAPI(title="LLM-4-VC Backend", version="1.0.0")

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://llm-4-vc.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# Initialize ChromaDB client
chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
chroma_client = chromadb.PersistentClient(
    path=chroma_db_path,
    settings=Settings(anonymized_telemetry=False)
)

# Create embedding function
ollama_ef = OllamaEmbeddingFunction(
    model_name=OLLAMA_EMBEDDING_MODEL,
    ollama_base_url=OLLAMA_BASE_URL
)

# Create or get a collection with Ollama embeddings
collection_name = "welcome_collection"
collection = chroma_client.get_or_create_collection(
    name=collection_name,
    embedding_function=ollama_ef
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Docker Backend with ChromaDB!",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/chroma/info")
async def chroma_info():
    """Get ChromaDB collection information"""
    count = collection.count()
    return {
        "collection_name": collection_name,
        "document_count": count,
        "chroma_version": chromadb.__version__
    }


@app.post("/chroma/add")
async def add_documents(documents: list[str], ids: list[str], metadatas: list[dict] = None):
    """Add documents to ChromaDB collection"""
    try:
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        return {
            "status": "success",
            "message": f"Added {len(documents)} documents to collection",
            "collection_name": collection_name
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/chroma/query")
async def query_documents(query_text: str, n_results: int = 5):
    """Query documents from ChromaDB collection"""
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return {
            "status": "success",
            "query": query_text,
            "results": results
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.delete("/chroma/clear")
async def clear_collection():
    """Clear all documents from the collection"""
    try:
        # Delete and recreate the collection
        chroma_client.delete_collection(name=collection_name)
        global collection
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=ollama_ef
        )
        return {
            "status": "success",
            "message": "Collection cleared successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.post("/chroma/load-csv")
async def load_csv(
    filename: str,
    text_column: str = None,
    id_column: str = None
):
    """
    Load a CSV file into ChromaDB collection

    Args:
        filename: Name of the CSV file in the /app/data directory
        text_column: Column to use as document text (if None, combines all columns)
        id_column: Column to use as document ID (if None, generates sequential IDs)
    """
    try:
        # Construct file path
        data_dir = Path("/app/data")
        file_path = data_dir / filename

        # Check if file exists
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"CSV file '{filename}' not found in /app/data directory"
            )

        # Read CSV file
        df = pd.read_csv(file_path)

        if df.empty:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty"
            )

        # Prepare documents
        documents = []
        ids = []
        metadatas = []

        for idx, row in df.iterrows():
            # Generate document text
            if text_column and text_column in df.columns:
                doc_text = str(row[text_column])
            else:
                # Combine all columns into a text representation
                doc_text = " | ".join([f"{col}: {val}" for col, val in row.items()])

            documents.append(doc_text)

            # Generate ID
            if id_column and id_column in df.columns:
                doc_id = str(row[id_column])
            else:
                doc_id = f"doc_{idx}"

            ids.append(doc_id)

            # Store all row data as metadata
            metadata = {col: str(val) for col, val in row.items()}
            metadatas.append(metadata)

        # Add to ChromaDB collection
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

        return {
            "status": "success",
            "message": f"Loaded {len(documents)} documents from {filename}",
            "collection_name": collection_name,
            "document_count": len(documents),
            "columns": list(df.columns)
        }

    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/data/list")
async def list_csv_files():
    """List all CSV files in the data directory"""
    try:
        data_dir = Path("/app/data")
        csv_files = [f.name for f in data_dir.glob("*.csv")]
        return {
            "status": "success",
            "files": csv_files,
            "count": len(csv_files)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/ollama/status")
async def ollama_status():
    """Check Ollama service health and available models"""
    try:
        client = ollama.Client(host=OLLAMA_BASE_URL)
        models = client.list()
        return {
            "status": "healthy",
            "base_url": OLLAMA_BASE_URL,
            "embedding_model": OLLAMA_EMBEDDING_MODEL,
            "available_models": [m['name'] for m in models.get('models', [])]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "base_url": OLLAMA_BASE_URL
        }
