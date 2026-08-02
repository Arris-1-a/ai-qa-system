#!/usr/bin/env python3
"""
AI Question Answering System - Enterprise RAG Platform
Advanced knowledge-based Q&A with vector search, multi-turn conversation,
and LLM integration support.
Features: Document management, semantic search, conversation history, API service
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

# Import common utilities
try:
    from ai_tools.logging_utils import setup_logger, ColoredLogger
    from ai_tools.config_manager import ConfigLoader
    from ai_tools.performance import MetricCollector, timeit
    from ai_tools.exceptions import AIError, DataError, ValidationError
except ImportError:
    # Fallback to standard library
    import logging
    from logging.handlers import RotatingFileHandler

    def setup_logger(name, log_file=None, level=logging.INFO, console_output=True):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
            if log_file:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = RotatingFileHandler(log_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            if console_output:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)
        return logger

    class MetricCollector:
        def __init__(self, *args, **kwargs): pass
        def record(self, *args, **kwargs): pass
        def increment(self, *args, **kwargs): pass
        def get_stats(self, *args, **kwargs): return {}

    def timeit(func): return func
    AIError = Exception
    DataError = Exception
    ValidationError = Exception

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = setup_logger(
    "qa_system",
    log_file=str(LOG_DIR / "qa.log"),
    level=logging.INFO
)


# ==================== Data Models ====================

@dataclass
class QueryContext:
    """Represents a single turn in conversation."""
    question: str
    answer: str = ""
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    sources: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class DocumentChunk:
    """Chunk of text for vector storage."""
    id: str
    content: str
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    added_at: str = ""

    def __post_init__(self):
        if not self.added_at:
            self.added_at = datetime.now().isoformat()


@dataclass
class SearchResult:
    """Result from vector search."""
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    rank: int = 0


@dataclass
class ConversationState:
    """Full state of a conversation."""
    conversation_id: str
    questions: List[str] = field(default_factory=list)
    answers: List[str] = field(default_factory=list)
    contexts: List[List[Dict]] = field(default_factory=list)
    created_at: str = ""
    last_active: str = ""
    message_count: int = 0

    def __post_init__(self):
        now = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now
        self.last_active = now

    def add_turn(self, question: str, answer: str, sources: List[Dict], confidence: float):
        """Add a question-answer pair."""
        self.questions.append(question)
        self.answers.append(answer)
        self.contexts.append(sources)
        self.message_count += 1
        self.last_active = datetime.now().isoformat()

    def get_recent_context(self, n_turns: int = 3) -> str:
        """Get recent conversation context."""
        recent_q = self.questions[-n_turns:] if len(self.questions) >= n_turns else self.questions
        return "\n\n".join(f"Q{i+1}: {q}" for i, q in enumerate(recent_q))

    def to_dict(self) -> Dict:
        return {
            'conversation_id': self.conversation_id,
            'message_count': self.message_count,
            'created_at': self.created_at,
            'last_active': self.last_active,
            'recent_questions': self.questions[-5:]
        }


@dataclass
class AnswerResult:
    """Complete answer result with all metadata."""
    answer: str
    sources: List[Dict]
    confidence: float
    query_time_ms: int
    timestamp: str
    conversation_id: str = ""
    followup_suggestions: List[str] = field(default_factory=list)
    related_queries: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            'answer': self.answer,
            'confidence': round(self.confidence, 4),
            'query_time_ms': self.query_time_ms,
            'timestamp': self.timestamp,
            'conversation_id': self.conversation_id,
            'source_count': len(self.sources),
            'sources_preview': [{'id': s.get('id', ''), 'score': s.get('score', 0)} for s in self.sources[:3]],
            'followup_suggestions': self.followup_suggestions
        }


# ==================== Vector Store ====================

class VectorStore:
    """
    Lightweight vector store with hash-based embeddings.
    In production, replace with ChromaDB, Pinecone, or Weaviate.
    """

    def __init__(self, dimension: int = 128, index_type: str = "brute_force"):
        self.dimension = dimension
        self.index_type = index_type
        self.documents: List[DocumentChunk] = []
        self._id_to_idx: Dict[str, int] = {}
        self._stats = {'insertions': 0, 'searches': 0, 'deletions': 0}

    def add(self, texts: List[str], ids: Optional[List[str]] = None,
            metadatas: Optional[List[Dict]] = None) -> List[str]:
        """Add documents to the vector store."""
        doc_ids = ids or [f"doc_{int(time.time()*1000)}_{i}" for i in range(len(texts))]
        metadatas = metadatas or [{} for _ in range(len(texts))]

        added_ids = []
        for text, doc_id, meta in zip(texts, doc_ids, metadatas):
            embedding = self._embed(text)
            chunk = DocumentChunk(
                id=doc_id,
                content=text,
                embedding=embedding,
                metadata=meta
            )
            idx = len(self.documents)
            self.documents.append(chunk)
            self._id_to_idx[doc_id] = idx
            added_ids.append(doc_id)
            self._stats['insertions'] += 1

        logger.info(f"Added {len(added_ids)} documents (total: {len(self.documents)})")
        return added_ids

    def search(self, query: str, top_k: int = 5,
               filter_fn: Optional[Callable] = None) -> List[SearchResult]:
        """Search for similar documents."""
        query_vec = self._embed(query)
        self._stats['searches'] += 1

        if not self.documents:
            return []

        # Calculate similarities
        similarities = []
        for i, doc in enumerate(self.documents):
            sim = self._cosine_similarity(query_vec, doc.embedding)
            if filter_fn and not filter_fn(doc):
                continue
            similarities.append((sim, i))

        # Sort and return top-k
        similarities.sort(reverse=True, key=lambda x: x[0])
        results = []
        for rank, (sim, idx) in enumerate(similarities[:top_k], 1):
            doc = self.documents[idx]
            results.append(SearchResult(
                document_id=doc.id,
                content=doc.content,
                score=round(float(sim), 4),
                metadata=doc.metadata,
                rank=rank
            ))

        return results

    def delete(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        if doc_id in self._id_to_idx:
            idx = self._id_to_idx[doc_id]
            self.documents[idx] = None  # Mark as deleted
            del self._id_to_idx[doc_id]
            self._stats['deletions'] += 1
            return True
        return False

    def clear(self):
        """Remove all documents."""
        self.documents.clear()
        self._id_to_idx.clear()
        logger.info("Vector store cleared")

    def count(self) -> int:
        """Get number of active documents."""
        return len([d for d in self.documents if d is not None])

    def get_document(self, doc_id: str) -> Optional[DocumentChunk]:
        """Retrieve a document by ID."""
        idx = self._id_to_idx.get(doc_id)
        if idx is not None:
            return self.documents[idx]
        return None

    def _embed(self, text: str) -> List[float]:
        """Generate deterministic embedding from text content."""
        # Use text hashing to create reproducible embeddings
        words = text.lower().split()
        combined = hashlib.md5(text.encode()).hexdigest()

        values = []
        state = int(combined[:8], 16)
        for _ in range(self.dimension):
            state = (state * 1103515245 + 12345) & 0x7FFFFFFF
            values.append((state % 10000) / 5000.0 - 1.0)

        # Normalize
        norm = sum(v * v for v in values) ** 0.5
        if norm > 0:
            values = [v / norm for v in values]
        return values

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0

    def get_stats(self) -> Dict:
        """Get vector store statistics."""
        return {
            **self._stats,
            'dimension': self.dimension,
            'index_type': self.index_type,
            'active_documents': self.count()
        }


# ==================== Response Generator ====================

class ResponseGenerator:
    """Generates intelligent responses based on retrieved context."""

    SYSTEM_PROMPT = """You are an AI assistant with access to a knowledge base.
Answer questions based ONLY on the provided context. If the context doesn't
contain relevant information, say so honestly. Be concise but thorough.
Cite your sources when possible."""

    FOLLOWUP_TEMPLATES = {
        'technical': ["Can you explain this in more detail?", "What are the implementation steps?",
                      "Are there any best practices?"],
        'general': ["Tell me more about this.", "Can you provide examples?",
                    "What are the pros and cons?"],
        'comparison': ["How does this compare to alternatives?", "What are the trade-offs?",
                       "Which option is better for my use case?"]
    }

    def generate(self, context_docs: List[Dict], question: str,
                 conversation_context: str = "") -> AnswerResult:
        """Generate response based on context and question."""
        start_time = datetime.now()

        # Build context for response generation
        context_text = self._build_context_text(context_docs)

        # Generate response
        answer = self._generate_answer(question, context_text, conversation_context)

        # Calculate confidence
        confidence = self._calculate_confidence(context_docs, question, answer)

        # Generate follow-up suggestions
        followups = self._generate_followups(question, context_docs)

        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        return AnswerResult(
            answer=answer,
            sources=context_docs,
            confidence=float(confidence),
            query_time_ms=max(elapsed_ms, 1),
            timestamp=datetime.now().isoformat(),
            followup_suggestions=followups[:3]
        )

    def _build_context_text(self, docs: List[Dict]) -> str:
        """Build formatted context from search results."""
        if not docs:
            return "No relevant documents found in the knowledge base."

        parts = []
        for i, doc in enumerate(docs[:5], 1):
            content = doc.get('content', '')[:1500]
            score = doc.get('score', 0)
            parts.append(f"[Source {i} - relevance: {score:.2f}]\n{content}")

        return "\n\n---\n\n".join(parts)

    def _generate_answer(self, question: str, context: str, conv_context: str) -> str:
        """Generate answer using context-aware logic."""
        # Check if we have relevant context
        has_relevant_context = 'No relevant documents' not in context

        if not has_relevant_context:
            return self._handle_no_context(question)

        # Extract key information from context
        keywords = self._extract_keywords(question)
        relevant_snippets = self._find_relevant_snippets(context, keywords)

        if not relevant_snippets:
            return self._generate_general_answer(context, question)

        # Build answer from snippets
        answer_parts = [f"Based on the available documentation:"]
        for snippet in relevant_snippets[:3]:
            answer_parts.append(f"• {snippet}")

        answer = "\n\n".join(answer_parts)

        # Add citation
        answer += "\n\n💡 *Source documents are referenced in the query results.*"

        return answer

    def _handle_no_context(self, question: str) -> str:
        """Handle cases where no relevant context is found."""
        templates = [
            f"I couldn't find specific information about '{question}' in my knowledge base.",
            f"This topic isn't covered in the current documents. Could you rephrase your question",
            f"or provide more context? You can also add relevant documents to improve my answers.",
            "",
            "Try asking about:",
            "  • General topics covered in your documents",
            "  • Specific terms or names mentioned in your knowledge base",
            "  • Technical details or implementation guidance"
        ]
        return "\n".join(templates)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at',
                      'to', 'for', 'of', 'and', 'or', 'with', 'this', 'that', 'what',
                      'how', 'why', 'when', 'where', 'which', 'who', 'can', 'could'}
        words = re.findall(r'[a-zA-Z]+', text.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]

    def _find_relevant_snippets(self, context: str, keywords: List[str]) -> List[str]:
        """Find relevant text snippets based on keywords."""
        sentences = re.split(r'(?<=[.!?])\s+', context)
        scored = []

        for sent in sentences:
            if len(sent.strip()) < 20:
                continue
            score = sum(1 for kw in keywords if kw in sent.lower())
            if score > 0:
                scored.append((score, sent.strip()))

        scored.sort(reverse=True)
        return [s for _, s in scored[:3]]

    def _calculate_confidence(self, docs: List[Dict], question: str, answer: str) -> float:
        """Calculate confidence score for the answer."""
        if not docs:
            return 0.1

        # Base confidence from search scores
        avg_score = sum(d.get('score', 0.5) for d in docs) / len(docs)

        # Adjust based on answer length
        answer_length_factor = min(len(answer.split()) / 50, 1.0)

        # Adjust based on keyword overlap
        keywords = set(self._extract_keywords(question))
        answer_words = set(answer.lower().split())
        overlap = len(keywords & answer_words) / max(len(keywords), 1)

        confidence = (avg_score * 0.5 + answer_length_factor * 0.3 + overlap * 0.2)
        return min(max(confidence, 0.1), 1.0)

    def _generate_followups(self, question: str, docs: List[Dict]) -> List[str]:
        """Generate follow-up question suggestions."""
        suggestions = []
        keywords = self._extract_keywords(question)

        if keywords:
            suggestions.append(f"What are the details about {keywords[0]}?")
            suggestions.append(f"Can you explain how {keywords[0]} works?")

        if not suggestions:
            suggestions = ["Tell me more about this topic.",
                          "What are the key points?",
                          "Can you provide examples?"]

        return suggestions

    def get_suggestions(self, question: str) -> List[str]:
        """Get suggested questions based on current query."""
        return self._generate_followups(question, [])


# ==================== Conversation Manager ====================

class ConversationManager:
    """Manage multi-turn conversations with state persistence."""

    def __init__(self, max_history: int = 10, ttl_hours: int = 24):
        self.conversations: Dict[str, ConversationState] = {}
        self.max_history = max_history
        self.ttl_hours = ttl_hours
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = datetime.now()

    def create(self) -> str:
        """Create a new conversation."""
        conv_id = str(uuid.uuid4())
        self.conversations[conv_id] = ConversationState(conversation_id=conv_id)
        return conv_id

    def add_message(self, conv_id: str, question: str, answer: str,
                    sources: List[Dict], confidence: float) -> bool:
        """Add a message turn to conversation."""
        if conv_id not in self.conversations:
            self.conversations[conv_id] = ConversationState(conversation_id=conv_id)

        state = self.conversations[conv_id]
        state.add_turn(question, answer, sources, confidence)

        # Trim history if needed
        if len(state.questions) > self.max_history:
            state.questions = state.questions[-self.max_history:]
            state.answers = state.answers[-self.max_history:]
            state.contexts = state.contexts[-self.max_history:]

        return True

    def add_turn(self, conv_id: str, question: str, answer: str,
                 sources: Optional[List[Dict]] = None, confidence: float = 0.0) -> bool:
        """Add a question-answer turn to a conversation (convenience wrapper)."""
        return self.add_message(conv_id, question, answer, sources or [], confidence)

    def get_history(self, conv_id: str) -> List[str]:
        """Get question history for a conversation."""
        state = self.conversations.get(conv_id)
        return list(state.questions) if state else []

    def get_context(self, conv_id: str, n_turns: int = None) -> str:
        """Get conversation context for augmenting queries."""
        if conv_id not in self.conversations:
            return ""

        state = self.conversations[conv_id]
        turns = n_turns or min(3, len(state.questions))
        recent = state.questions[-turns:] if turns <= len(state.questions) else state.questions

        if not recent:
            return ""

        return "Previous conversation:\n" + "\n".join(f"Q: {q}\nA: {a}"
                                                      for q, a in zip(recent[:-1], state.answers[:-1]))

    def get_state(self, conv_id: str) -> Optional[ConversationState]:
        """Get conversation state."""
        return self.conversations.get(conv_id)

    def list_conversations(self, limit: int = 10) -> List[Dict]:
        """List recent conversations."""
        items = [s.to_dict() for s in self.conversations.values()]
        items.sort(key=lambda x: x['last_active'], reverse=True)
        return items[:limit]

    def clear(self, conv_id: str) -> bool:
        """Clear a conversation."""
        if conv_id in self.conversations:
            del self.conversations[conv_id]
            return True
        return False

    def cleanup_expired(self):
        """Remove expired conversations."""
        now = datetime.now()
        expired = []
        for conv_id, state in self.conversations.items():
            last_active = datetime.fromisoformat(state.last_active)
            if now - last_active > timedelta(hours=self.ttl_hours):
                expired.append(conv_id)

        for conv_id in expired:
            del self.conversations[conv_id]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired conversations")

    def get_stats(self) -> Dict:
        """Get conversation statistics."""
        self.cleanup_expired()
        return {
            'active_conversations': len(self.conversations),
            'max_history': self.max_history,
            'ttl_hours': self.ttl_hours
        }


# ==================== Main QA System ====================

class QASystem:
    """Main Question Answering system combining all components."""

    def __init__(self, config_path: Optional[str] = None):
        self.vector_store = VectorStore(dimension=128)
        self.generator = ResponseGenerator()
        self.conversation_manager = ConversationManager(max_history=10)
        self.is_initialized = False
        self.search_top_k = 5
        self.metrics = MetricCollector("qa_system")

        # Load configuration
        self.config = self._load_config(config_path)
        self._apply_config()

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or defaults."""
        defaults = {
            'search': {'top_k': 5, 'min_confidence': 0.3},
            'conversation': {'max_history': 10, 'ttl_hours': 24},
            'output': {'format': 'json', 'include_sources': True}
        }
        if config_path and Path(config_path).exists():
            import yaml
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f) or {}
            # Merge configs (simple merge, not recursive for this example)
            for section in defaults:
                if section in user_config:
                    defaults[section].update(user_config[section])
        return defaults

    def _apply_config(self):
        """Apply configuration to components."""
        self.search_top_k = self.config.get('search.top_k', 5)
        self.conversation_manager = ConversationManager(
            max_history=self.config.get('conversation.max_history', 10),
            ttl_hours=self.config.get('conversation.ttl_hours', 24)
        )

    async def initialize(self) -> None:
        """Initialize the system."""
        await asyncio.sleep(0)  # Placeholder for async initialization
        self.is_initialized = True
        logger.info("QA System initialized successfully")

    @timeit
    async def ask(self, question: str, conversation_id: Optional[str] = None,
                  force_new: bool = False) -> AnswerResult:
        """Process a question and return answer with sources."""
        if not self.is_initialized:
            await self.initialize()

        # Handle conversation
        if force_new or not conversation_id:
            conversation_id = self.conversation_manager.create()

        # Get conversation context
        conv_context = self.conversation_manager.get_context(conversation_id)
        full_query = f"{conv_context}\n\nCurrent question: {question}" if conv_context else question

        # Search knowledge base
        start_ms = int(datetime.now().timestamp() * 1000)
        search_results = self.vector_store.search(full_query, top_k=self.search_top_k)
        query_time = int(datetime.now().timestamp() * 1000) - start_ms

        # Generate response
        answer_result = self.generator.generate(search_results, question, conv_context)
        answer_result.query_time_ms += query_time
        answer_result.conversation_id = conversation_id

        # Update conversation
        self.conversation_manager.add_message(
            conversation_id, question, answer_result.answer,
            [{'id': s.document_id, 'score': s.score} for s in search_results],
            answer_result.confidence
        )

        # Log metrics
        self.metrics.increment("questions.answered")
        self.metrics.record("response_time_ms", answer_result.query_time_ms)
        self.metrics.record("confidence", answer_result.confidence)

        logger.info(f"Q: {question[:50]}... | Conf: {answer_result.confidence:.2%} | "
                   f"Time: {answer_result.query_time_ms}ms | Sources: {len(search_results)}")

        return answer_result

    def add_documents(self, texts: List[str], ids: Optional[List[str]] = None,
                      metadatas: Optional[List[Dict]] = None) -> List[str]:
        """Add documents to knowledge base."""
        return self.vector_store.add(texts, ids, metadatas)

    def remove_document(self, doc_id: str) -> bool:
        """Remove a document from knowledge base."""
        return self.vector_store.delete(doc_id)

    def get_stats(self) -> Dict:
        """Get system statistics."""
        return {
            'document_count': self.vector_store.count(),
            'initialized': self.is_initialized,
            'conversations': self.conversation_manager.get_stats(),
            'vector_store': self.vector_store.get_stats(),
            'metrics': self.metrics.get_stats()
        }

    def export_knowledge_base(self, output_path: str) -> str:
        """Export knowledge base to JSON file."""
        data = {
            'exported_at': datetime.now().isoformat(),
            'document_count': self.vector_store.count(),
            'documents': []
        }

        for doc in self.vector_store.documents:
            if doc:
                data['documents'].append({
                    'id': doc.id,
                    'content': doc.content[:500],  # Truncate for export
                    'metadata': doc.metadata,
                    'added_at': doc.added_at
                })

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Knowledge base exported to: {output_path}")
        return output_path

    def import_knowledge_base(self, input_path: str) -> int:
        """Import knowledge base from JSON file."""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        texts = [doc['content'] for doc in data.get('documents', [])]
        ids = [doc['id'] for doc in data.get('documents', [])]

        imported = self.add_documents(texts, ids)
        logger.info(f"Imported {len(imported)} documents from {input_path}")
        return len(imported)


# ==================== CLI Interface ====================

def interactive_mode(qa: QASystem):
    """Interactive command-line interface."""
    print("\n" + "=" * 60)
    print("🤖 AI Question Answering System (RAG Platform)")
    print("=" * 60)
    print("Commands:")
    print("  help          - Show this help")
    print("  quit/exit     - Exit the program")
    print("  add <file>    - Add document to knowledge base")
    print("  search <q>    - Search without starting conversation")
    print("  new           - Start new conversation")
    print("  history       - Show conversation history")
    print("  stats         - Show system statistics")
    print("  clear         - Clear current conversation")
    print("  export        - Export knowledge base")
    print("  import <file> - Import knowledge base")
    print("=" * 60 + "\n")

    conv_id = None

    while True:
        try:
            user_input = input("You> ").strip()
            if not user_input:
                continue

            # Command handling
            if user_input.lower() in ('quit', 'exit'):
                break

            elif user_input.lower() == 'help':
                print("""
Available Commands:
  help          Show this help
  quit/exit     Exit the program
  add <file>    Add document (TXT, MD, CSV, JSON) to knowledge base
  search <q>    Search knowledge base directly
  new           Start a new conversation
  history       Show recent conversation history
  stats         Show system statistics
  clear         Clear current conversation
  export        Export knowledge base to JSON
  import <file> Import knowledge base from JSON
""")
                continue

            elif user_input.lower() == 'clear':
                if conv_id:
                    qa.conversation_manager.clear(conv_id)
                    conv_id = None
                    print("✅ Conversation cleared\n")
                continue

            elif user_input.lower() == 'new':
                conv_id = qa.conversation_manager.create()
                print(f"✅ New conversation started\n")
                continue

            elif user_input.lower() == 'stats':
                stats = qa.get_stats()
                print(f"""
📊 System Statistics:
   Documents in KB:    {stats['document_count']}
   Active Conversations: {stats['conversations']['active_conversations']}
   Initialized:        {stats['initialized']}
""")
                continue

            elif user_input.lower() == 'history':
                if not conv_id:
                    print("No active conversation. Start one with 'new'\n")
                    continue
                state = qa.conversation_manager.get_state(conv_id)
                if state:
                    print(f"\n📝 Conversation History ({state.message_count} messages):")
                    for i, (q, a) in enumerate(zip(state.questions, state.answers)):
                        print(f"\n  Q{i+1}: {q[:80]}...")
                        print(f"  A{i+1}: {a[:100]}...")
                continue

            elif user_input.lower().startswith('add '):
                filepath = user_input[4:].strip()
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if content:
                        qa.add_documents([content])
                        print(f"✅ Added: {filepath}")
                    else:
                        print("⚠️ File is empty\n")
                except FileNotFoundError:
                    print(f"❌ File not found: {filepath}\n")
                continue

            elif user_input.lower().startswith('search '):
                query = user_input[7:].strip()
                results = qa.vector_store.search(query, top_k=3)
                if results:
                    print(f"\n🔍 Search results for '{query}':\n")
                    for i, r in enumerate(results, 1):
                        preview = r.content[:150].replace('\n', ' ')
                        print(f"  [{i}] Score: {r.score:.4f}")
                        print(f"      {preview}...")
                else:
                    print("\nNo results found. Add documents first with 'add <file>'\n")
                continue

            elif user_input.lower() == 'export':
                output = f"knowledge_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                qa.export_knowledge_base(output)
                print(f"✅ Exported to: {output}\n")
                continue

            elif user_input.lower().startswith('import '):
                filepath = user_input[7:].strip()
                try:
                    count = qa.import_knowledge_base(filepath)
                    print(f"✅ Imported {count} documents from {filepath}\n")
                except Exception as e:
                    print(f"❌ Import failed: {e}\n")
                continue

            # Normal question - process with conversation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(qa.ask(user_input, conv_id))
            loop.close()

            print(f"\nAI> {result.answer}")
            print(f"   💡 Confidence: {result.confidence:.2%} | "
                  f"Time: {result.query_time_ms}ms | "
                  f"Sources: {len(result.sources)}")
            if result.followup_suggestions:
                print(f"   🔍 Try asking:")
                for sug in result.followup_suggestions:
                    print(f"      • {sug}")
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            logger.error(f"Interactive error: {e}", exc_info=True)


def main():
    """Main entry point."""
    import sys

    qa = QASystem()

    # Check for API mode
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        print("🚀 Starting QA API Server...")
        print("   Run: uvicorn api.app:app --reload --port 8000")
        print("   Test: curl -X POST http://localhost:8000/ask -H 'Content-Type: application/json' -d '{\"question\": \"...\"}'")
        return

    # Initialize and start interactive mode
    asyncio.run(qa.initialize())
    interactive_mode(qa)


if __name__ == "__main__":
    main()


class KnowledgeManager:
    """Manage knowledge base operations."""
    
    def __init__(self, qa_system: QASystem):
        self.qa = qa_system
    
    def add_from_file(self, filepath: str) -> int:
        """Add documents from a file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            if content:
                self.qa.add_documents([content])
                return 1
        except Exception as e:
            logger.error(f"Failed to add {filepath}: {e}")
        return 0
    
    def add_from_directory(self, dirpath: str) -> int:
        """Add documents from a directory."""
        count = 0
        for ext in ['.txt', '.md', '.csv']:
            for file in Path(dirpath).glob(f"*{ext}"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if content:
                        self.qa.add_documents([content])
                        count += 1
                except Exception as e:
                    logger.warning(f"Skipped {file}: {e}")
        return count
    
    def get_document_count(self) -> int:
        """Get total number of documents."""
        return self.qa.vector_store.count()
    
    def list_documents(self, limit: int = 10) -> List[Dict]:
        """List recent documents."""
        docs = []
        for doc in self.qa.vector_store.documents[-limit:]:
            if doc:
                docs.append({
                    'id': doc.id,
                    'content_preview': doc.content[:100] + '...',
                    'added_at': doc.added_at
                })
        return docs


class AdvancedEvaluator:
    """Advanced evaluation metrics."""
    
    @staticmethod
    def calculate_diversity(recommendations: List[Tuple[str, float]]) -> float:
        """Calculate diversity of recommendations."""
        if len(recommendations) <= 1:
            return 1.0
        # Simple diversity based on score distribution
        scores = [s for _, s in recommendations]
        if len(scores) < 2:
            return 1.0
        variance = np.var(scores)
        return min(1.0, variance * 10)  # Normalize
    
    @staticmethod
    def calculate_coverage(
        all_recommendations: List[List[str]],
        all_items: set
    ) -> float:
        """Calculate catalog coverage."""
        recommended_items = set()
        for recs in all_recommendations:
            recommended_items.update(recs)
        return len(recommended_items) / len(all_items) if all_items else 0.0


class EmbeddingService:
    """Text embedding service for better semantic search."""
    
    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.embeddings: Dict[str, List[float]] = {}
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        import hashlib
        words = text.lower().split()
        combined = hashlib.md5(text.encode()).hexdigest()
        
        values = []
        state = int(combined[:8], 16)
        for _ in range(self.dimension):
            state = (state * 1103515245 + 12345) & 0x7FFFFFFF
            values.append((state % 10000) / 5000.0 - 1.0)
        
        # Normalize
        norm = sum(v * v for v in values) ** 0.5
        if norm > 0:
            values = [v / norm for v in values]
        
        self.embeddings[text[:50]] = values
        return values
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        vec1 = self.embed(text1)
        vec2 = self.embed(text2)
        
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        return dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0


class VideoAnalyzer:
    """Video analysis using frame extraction."""
    
    def __init__(self, recognizer: ImageRecognizer):
        self.recognizer = recognizer
        self.frame_interval = 30
    
    def analyze(self, video_path: str) -> List[Dict]:
        """Analyze video and return frame-by-frame results."""
        import cv2
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        results = []
        frame_count = 0
        analyzed_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % self.frame_interval == 0:
                result = self.recognizer.analyze_frame(frame)
                results.append({
                    'frame': frame_count,
                    'detections': len(result.detections),
                    'faces': result.face_count,
                    'classifications': result.classifications[:3]
                })
                analyzed_count += 1
        
        cap.release()
        logger.info(f"Video analysis: {analyzed_count} frames from {frame_count} total")
        return results
    
    def detect_faces_in_video(self, video_path: str) -> List[Dict]:
        """Detect faces in video frames."""
        import cv2
        cap = cv2.VideoCapture(video_path)
        
        faces_results = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % 10 == 0:
                faces = self.recognizer.face_detector.detect(frame)
                faces_results.append({
                    'frame': frame_count,
                    'face_count': len(faces),
                    'faces': [f.to_dict() for f in faces]
                })
        
        cap.release()
        return faces_results


class ReportGenerator:
    """Generate processing reports."""
    
    def __init__(self, processor: DocumentProcessor):
        self.processor = processor
    
    def generate_html_report(self, output_path: str) -> str:
        """Generate HTML report."""
        html = """<!DOCTYPE html>
<html>
<head><title>Document Processing Report</title></head>
<body>
<h1>AI Document Processing Report</h1>
"""
        for result in self.processor.results:
            html += f"""
<div class="result">
<h2>{result.filename}</h2>
<p>Type: {result.doc_type}</p>
<p>Words: {result.metadata.word_count}</p>
<p>Entities: {len(result.entities)}</p>
<p>Summary: {result.summary[:200]}...</p>
</div>
"""
        html += "</body></html>"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"HTML report saved to: {output_path}")
        return output_path
    
    def generate_statistics(self) -> Dict:
        """Generate processing statistics."""
        return {
            'total_documents': len(self.processor.results),
            'total_words': sum(r.metadata.word_count for r in self.processor.results),
            'total_entities': sum(len(r.entities) for r in self.processor.results),
            'avg_reading_time': sum(r.metadata.reading_time_minutes for r in self.processor.results) / max(1, len(self.processor.results))
        }


class ConversationHistory:
    """Manage conversation history with persistence."""
    
    def __init__(self, storage_dir: str = "conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, conversation_id: str, history: List[Dict]) -> bool:
        """Save conversation history to file."""
        filepath = self.storage_dir / f"{conversation_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'conversation_id': conversation_id,
                'history': history,
                'saved_at': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        return True
    
    def load(self, conversation_id: str) -> Optional[Dict]:
        """Load conversation history from file."""
        filepath = self.storage_dir / f"{conversation_id}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def list_conversations(self) -> List[str]:
        """List all saved conversation IDs."""
        return [f.stem for f in self.storage_dir.glob("*.json")]
    
    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        filepath = self.storage_dir / f"{conversation_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False
