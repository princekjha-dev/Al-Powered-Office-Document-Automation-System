"""
Document Chat/Q&A service using RAG (Retrieval Augmented Generation).
Allows users to ask questions about documents and get contextual answers.
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DocumentChat:
    """
    RAG-based service for document question-answering.
    Uses embedding-based retrieval to ground answers in document content.
    """

    def __init__(self, data_dir: str = "data/chat_sessions"):
        """
        Initialize document chat service.
        
        Args:
            data_dir: Directory to store chat sessions
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Try to import sentence-transformers for embeddings
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embeddings_available = True
        except ImportError:
            logger.warning("sentence-transformers not installed. Using keyword matching instead.")
            self.embeddings_available = False
            self.model = None
        except (TypeError, Exception) as e:
            logger.warning(f"Failed to load SentenceTransformer model: {e}. Using keyword matching instead.")
            self.embeddings_available = False
            self.model = None

    def chunk_document(self, text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
        """
        Split document into overlapping chunks for better retrieval.
        
        Args:
            text: Document text
            chunk_size: Characters per chunk
            overlap: Overlap between chunks
        
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks if chunks else [text]

    def create_session(self, document_text: str, user_id: int) -> str:
        """
        Create a new chat session for a document.
        
        Args:
            document_text: The document content
            user_id: User ID
        
        Returns:
            Session ID
        """
        session_id = f"{user_id}_{int(datetime.now().timestamp())}"
        chunks = self.chunk_document(document_text)
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "document_text": document_text[:15000],  # Store full text for broad questions
            "document_chunks": chunks,
            "chat_history": [],
            "embeddings": []
        }
        
        # Create embeddings if available
        if self.embeddings_available and self.model:
            try:
                session_data["embeddings"] = [
                    self.model.encode(chunk).tolist() for chunk in chunks
                ]
            except Exception as e:
                logger.error(f"Embedding error: {e}")
        
        # Save session
        session_file = os.path.join(self.data_dir, f"{session_id}.json")
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        return session_id

    def retrieve_context(self, session_id: str, question: str, top_k: int = 5) -> List[str]:
        """
        Retrieve relevant chunks from document based on question.
        
        Args:
            session_id: Session ID
            question: User question
            top_k: Number of top chunks to return
        
        Returns:
            List of relevant chunks
        """
        session_file = os.path.join(self.data_dir, f"{session_id}.json")
        
        if not os.path.exists(session_file):
            return []
        
        with open(session_file, 'r') as f:
            session = json.load(f)
        
        chunks = session.get("document_chunks", [])
        
        # Use embedding-based retrieval if available
        if self.embeddings_available and self.model and session.get("embeddings"):
            try:
                query_embedding = self.model.encode(question)
                embeddings = session["embeddings"]
                
                # Calculate similarity scores (cosine similarity)
                import numpy as np
                similarities = []
                for chunk_embedding in embeddings:
                    # Simple dot product (embeddings are normalized)
                    score = float(np.dot(query_embedding, chunk_embedding))
                    similarities.append(score)
                
                # Get top-k indices
                top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]
                return [chunks[i] for i in sorted(top_indices)]
            except Exception as e:
                logger.error(f"Retrieval error: {e}")
        
        # Fallback: keyword matching
        question_words = set(question.lower().split())
        scored_chunks = []
        
        for i, chunk in enumerate(chunks):
            chunk_words = set(chunk.lower().split())
            overlap = len(question_words & chunk_words)
            if overlap > 0:
                scored_chunks.append((i, chunk, overlap))
        
        # Sort by match count
        scored_chunks.sort(key=lambda x: x[2], reverse=True)
        
        # If very few keyword matches, return first chunks as fallback
        if len(scored_chunks) < 2:
            return chunks[:top_k]
        
        return [chunk for _, chunk, _ in scored_chunks[:top_k]]

    def answer_question(self, session_id: str, question: str, ai_service) -> str:
        """
        Answer a question about the document.
        
        Args:
            session_id: Session ID
            question: User question
            ai_service: AI service for generating answers
        
        Returns:
            Answer string
        """
        # Load session to get full document text
        session_file = os.path.join(self.data_dir, f"{session_id}.json")
        full_text = ""
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            full_text = session_data.get("document_text", "")

        # Retrieve context chunks (specific relevant parts)
        context_chunks = self.retrieve_context(session_id, question, top_k=5)

        # Build context: use retrieved chunks + beginning of document for broad context
        if context_chunks:
            combined_context = "\n\n".join(context_chunks)
        elif full_text:
            combined_context = full_text[:4000]
        else:
            return "No document content found. Please upload a document first."
        
        # For broad questions (roadmap, plan, summary, etc.), include more document text
        broad_keywords = ["roadmap", "plan", "create", "make", "build", "suggest", "recommend",
                          "summarize", "summary", "overview", "list", "all", "everything",
                          "based on", "from this", "from my", "using this"]
        is_broad = any(kw in question.lower() for kw in broad_keywords)
        
        if is_broad and full_text:
            # Give the AI more document context for broad/creative questions
            combined_context = full_text[:6000]
        
        # Create prompt
        prompt = (
            f"You have access to the following document content:\n\n"
            f"{combined_context}\n\n"
            f"User's request: {question}\n\n"
            f"Use the document content as your primary reference. "
            f"Answer thoroughly and helpfully based on the document. "
            f"If the user asks you to create, generate, or build something "
            f"(like a roadmap, plan, or summary), do it using the information in the document. "
            f"Respond in plain text. No emojis. No decorative formatting."
        )
        
        try:
            response = ai_service.call_ai(
                prompt,
                system_role=(
                    "You are a document assistant. The user has uploaded a document and is asking "
                    "questions about it. Use the document content to answer. When the user asks you "
                    "to create something (a roadmap, plan, list, summary, etc.), use the document "
                    "as your source material and produce the requested output. "
                    "Never refuse to help if there is document content available. "
                    "Write in plain text. Never use emojis."
                ),
                max_tokens=1500,
            )
            
            # Store in chat history
            if os.path.exists(session_file):
                with open(session_file, 'r') as f:
                    session = json.load(f)
                
                session["chat_history"].append({
                    "question": question,
                    "answer": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                with open(session_file, 'w') as f:
                    json.dump(session, f)
            
            return response
        except Exception as e:
            logger.error(f"Answer generation error: {e}")
            return f"Error generating answer: {str(e)}"

    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session."""
        session_file = os.path.join(self.data_dir, f"{session_id}.json")
        
        if not os.path.exists(session_file):
            return []
        
        with open(session_file, 'r') as f:
            session = json.load(f)
        
        return session.get("chat_history", [])

    def cleanup_session(self, session_id: str) -> None:
        """Delete a chat session."""
        session_file = os.path.join(self.data_dir, f"{session_id}.json")
        if os.path.exists(session_file):
            os.remove(session_file)
