from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document
from config import settings
import logging
import os

logger = logging.getLogger(__name__)


class DocumentSearchEngine:
    """RAG-powered document search and Q&A system"""
    
    def __init__(self, use_openai_embeddings: bool = False):
        """Initialize the document search engine"""
        try:
            # Use HuggingFace embeddings (local, free)
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Initialize Chroma client
            os.makedirs(settings.chroma_persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
                length_function=len,
            )
            
            self.available = True
            logger.info("DocumentSearchEngine initialized successfully")
            
        except Exception as e:
            self.available = False
            self.embeddings = None
            self.collection = None
            logger.warning(f"DocumentSearchEngine: Not available - {e}")
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load a document from file"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension in ['.txt', '.md']:
                loader = TextLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            raise
    
    def add_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Add a document to the vector store"""
        # Load document
        documents = self.load_document(file_path)
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add metadata
        filename = os.path.basename(file_path)
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "filename": filename,
                "chunk_index": i,
                "source": file_path,
                **(metadata or {})
            })
        
        # Generate embeddings and add to collection
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [f"{filename}_{i}" for i in range(len(chunks))]
        
        # Get embeddings
        embeddings = self.embeddings.embed_documents(texts)
        
        # Add to Chroma
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(chunks)} chunks from {filename} to vector store")
        return len(chunks)
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        if top_k is None:
            top_k = settings.top_k_results
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Search in Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                score = 1 - results['distances'][0][i]  # Convert distance to similarity
                
                if score >= settings.similarity_threshold:
                    formatted_results.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i],
                        "score": score
                    })
        
        logger.info(f"Found {len(formatted_results)} relevant chunks for query: {query}")
        return formatted_results
    
    def summarize(self, query: str, style: str = "detailed") -> str:
        """Summarize document content based on query"""
        results = self.search(query, top_k=settings.top_k_results)
        
        if not results:
            return "No relevant information found."
        
        # Combine relevant passages
        context = "\n\n".join([r["content"] for r in results])
        
        # Create summary prompt based on style
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=settings.openai_api_key,
            temperature=0.3
        )
        
        style_prompts = {
            "short": "Provide a brief 2-3 sentence summary.",
            "detailed": "Provide a comprehensive summary with key points.",
            "bullet": "Provide a bullet-point summary of the main ideas."
        }
        
        prompt = f"""Based on the following context, {style_prompts.get(style, style_prompts['detailed'])}

Context:
{context}

Query: {query}

Summary:"""
        
        summary = llm.invoke(prompt).content
        return summary
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using RAG"""
        results = self.search(question)
        
        if not results:
            return {
                "answer": "I don't have enough information in the documents to answer this question.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Prepare context
        context = "\n\n".join([
            f"[Source: {r['metadata']['filename']}, Page: {r['metadata'].get('page', 'N/A')}]\n{r['content']}"
            for r in results
        ])
        
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_key=settings.openai_api_key,
            temperature=0.2
        )
        
        prompt = f"""Answer the following question based on the provided context. 
Be accurate and cite specific sources when possible.

Context:
{context}

Question: {question}

Answer:"""
        
        answer = llm.invoke(prompt).content
        
        sources = [
            {
                "filename": r["metadata"]["filename"],
                "page": r["metadata"].get("page"),
                "score": r["score"]
            }
            for r in results
        ]
        
        avg_score = sum(r["score"] for r in results) / len(results)
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": avg_score
        }
    
    def delete_document(self, filename: str) -> bool:
        """Delete all chunks of a document"""
        try:
            # Get all IDs for this filename
            results = self.collection.get(
                where={"filename": filename}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting document {filename}: {e}")
            return False
    
    def list_documents(self) -> List[str]:
        """List all documents in the vector store"""
        results = self.collection.get()
        filenames = set()
        
        if results['metadatas']:
            for metadata in results['metadatas']:
                filenames.add(metadata['filename'])
        
        return sorted(list(filenames))
