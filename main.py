#!/usr/bin/env python3
"""
AI Question Answering System - Knowledge-based Q&A engine
Supports vector search, multi-turn conversation, and REST API
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler(LOG_DIR / "qa.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


@dataclass
class QueryContext:
    question: str
    history: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class AnswerResult:
    answer: str
    source_documents: List[Dict]
    confidence: float
    query_time_ms: int
    timestamp: str
    conversation_id: str = ""


class VectorStore:
    """Lightweight vector store using hash-based embeddings."""

    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.documents: List[Dict] = []
        self.vectors: List[List[float]] = []

    def add(self, texts: List[str], ids: Optional[List[str]] = None) -> List[str]:
        doc_ids = ids or [f"doc_{i}" for i in range(len(texts))]
        for text, did in zip(texts, doc_ids):
            embedding = self._embed(text)
            self.documents.append({'id': did, 'text': text, 'embedding': embedding})
            self.vectors.append(embedding)
        return doc_ids

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_vec = self._embed(query)
        if not self.documents:
            return []

        similarities = []
        for i, doc_vec in enumerate(self.vectors):
            sim = self._cosine_similarity(query_vec, doc_vec)
            similarities.append((sim, i))

        similarities.sort(key=lambda x: x[0], reverse=True)
        results = []
        for sim, idx in similarities[:top_k]:
            doc = self.documents[idx]
            results.append({
                'id': doc['id'],
                'content': doc['text'],
                'score': round(float(sim), 4)
            })
        return results

    def _embed(self, text: str) -> List[float]:
        """Generate deterministic embedding from text content."""
        import hashlib
        words = text.lower().split()
        h = hashlib.md5(text.encode()).hexdigest()
        values = []
        seed = int(h[:8], 16)
        state = seed
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
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0

    def clear(self) -> None:
        self.documents.clear()
        self.vectors.clear()

    def count(self) -> int:
        return len(self.documents)


class ResponseGenerator:
    """Generates natural language responses based on retrieved context."""

    FALLBACK_ANSWER = (
        "I'm sorry, I don't have enough information to answer this question. "
        "Please try rephrasing your question or consult the relevant documentation."
    )

    def generate(self, context_docs: List[Dict], question: str) -> AnswerResult:
        context_text = "\n\n".join([
            f"[Source {i+1}] {doc['content'][:2000]}"
            for i, doc in enumerate(context_docs)
        ])

        answer = self._generate_response(question, context_text)

        avg_confidence = sum(d.get('score', 0.5) for d in context_docs) / len(context_docs) if context_docs else 0.3
        avg_confidence = min(1.0, max(0.0, avg_confidence))

        return AnswerResult(
            answer=answer,
            source_documents=context_docs,
            confidence=float(avg_confidence),
            query_time_ms=0,
            timestamp=datetime.now().isoformat()
        )

    def _generate_response(self, question: str, context: str) -> str:
        """Generate a context-aware response."""
        keywords = [kw for kw in question.lower().split() if len(kw) > 2]
        relevant_paras = []

        for kw in keywords:
            matches = [p.strip() for p in context.replace('\n\n', '. ').split('. ')
                       if kw in p.lower() and len(p.strip()) > 20]
            relevant_paras.extend(matches[:2])

        unique_relevant = list(dict.fromkeys(relevant_paras))[:3]

        if unique_relevant:
            return (
                "Based on the available documents:\n\n"
                + "\n\n".join(f"- {p}" for p in unique_relevant)
                + "\n\nFor more details, please refer to the source documents."
            )

        return (
            f"I couldn't find specific information about '{question}' "
            f"in the current knowledge base. Try asking about topics that might be covered "
            f"in your documents, or add more relevant content to the knowledge base."
        )


class ConversationManager:
    """Manages multi-turn conversation state."""

    def __init__(self, max_history: int = 5):
        self.conversations: Dict[str, List[QueryContext]] = {}
        self.max_history = max_history

    def create(self) -> str:
        conv_id = str(uuid.uuid4())
        self.conversations[conv_id] = []
        return conv_id

    def add_turn(self, conv_id: str, question: str, bot_answer: str = "") -> None:
        if conv_id not in self.conversations:
            self.conversations[conv_id] = []
        self.conversations[conv_id].append(QueryContext(question=question))
        if bot_answer:
            self.conversations[conv_id].append(QueryContext(question=bot_answer))
        # Keep only last N rounds (each round = 2 entries)
        max_entries = self.max_history * 2
        if len(self.conversations[conv_id]) > max_entries:
            self.conversations[conv_id] = self.conversations[conv_id][-max_entries:]

    def get_history(self, conv_id: str) -> List[str]:
        if conv_id not in self.conversations:
            return []
        return [entry.question for entry in self.conversations[conv_id]]

    def get_context_for_question(self, conv_id: str, current_q: str) -> str:
        history = self.get_history(conv_id)
        if not history:
            return current_q
        recent = history[-4:]
        return "\n\nPrevious conversation:\n" + "\n".join(f"Q: {h}" for h in recent[:-1:2]) + \
               f"\n\nCurrent question: {current_q}"

    def clear(self, conv_id: str) -> bool:
        if conv_id in self.conversations:
            del self.conversations[conv_id]
            return True
        return False

    def get_conversation_count(self) -> int:
        return len(self.conversations)


class QASystem:
    """Main QA system combining search, generation, and conversation."""

    def __init__(self):
        self.vector_store = VectorStore()
        self.generator = ResponseGenerator()
        self.conversation_manager = ConversationManager(max_history=5)
        self.is_initialized = False
        self.search_top_k = 5

    async def initialize(self) -> None:
        self.is_initialized = True
        logger.info("QA System initialized")

    async def ask(self, question: str, conversation_id: Optional[str] = None) -> AnswerResult:
        if not self.is_initialized:
            await self.initialize()

        if not conversation_id:
            conversation_id = self.conversation_manager.create()

        start_ms = int(datetime.now().timestamp() * 1000)
        full_question = self.conversation_manager.get_context_for_question(
            conversation_id, question
        )

        docs = self.vector_store.search(full_question, top_k=self.search_top_k)

        result = self.generator.generate(docs, full_question)
        result.conversation_id = conversation_id
        result.query_time_ms = int(datetime.now().timestamp() * 1000) - start_ms

        self.conversation_manager.add_turn(conversation_id, question, result.answer)
        logger.info(f"Q: {question[:60]}... | Confidence: {result.confidence:.2%}")
        return result

    def add_documents(self, texts: List[str]) -> List[str]:
        ids = self.vector_store.add(texts)
        logger.info(f"Added {len(texts)} documents to knowledge base (total: {self.vector_store.count()})")
        return ids

    def get_stats(self) -> Dict:
        return {
            'document_count': self.vector_store.count(),
            'initialized': self.is_initialized,
            'active_conversations': self.conversation_manager.get_conversation_count()
        }


def interactive_mode(qa: QASystem) -> None:
    print("\n" + "=" * 55)
    print("AI Question Answering System")
    print("=" * 55)
    print("Type 'help' for commands, 'quit' to exit\n")

    conv_id = None

    while True:
        try:
            user_input = input("You> ").strip()
            if not user_input:
                continue

            if user_input.lower() in ('quit', 'exit'):
                break

            if user_input.lower() == 'help':
                print("""
Commands:
  help         Show this help
  quit         Exit the program
  add <file>   Add document from file to knowledge base
  clear        Clear current conversation
  new          Start a new conversation
  stats        Show system statistics
  list-docs    List all documents in knowledge base
""")
                continue

            if user_input.lower() == 'clear':
                if conv_id:
                    qa.conversation_manager.clear(conv_id)
                    conv_id = None
                    print("Conversation cleared\n")
                continue

            if user_input.lower() == 'new':
                conv_id = qa.conversation_manager.create()
                print(f"New conversation started\n")
                continue

            if user_input.lower() == 'stats':
                stats = qa.get_stats()
                print(f"\nStats: docs={stats['document_count']}, "
                      f"conversations={stats['active_conversations']}\n")
                continue

            if user_input.lower() == 'list-docs':
                count = qa.vector_store.count()
                if count == 0:
                    print("\nNo documents in knowledge base. Use 'add <file>' to add one.\n")
                else:
                    print(f"\n{count} document(s) in knowledge base:\n")
                    for i, doc in enumerate(qa.vector_store.documents[:10]):
                        preview = doc['text'][:80].replace('\n', ' ')
                        print(f"  [{i+1}] {doc['id']}: {preview}...")
                    if count > 10:
                        print(f"  ... and {count - 10} more")
                continue

            if user_input.lower().startswith('add '):
                filepath = user_input[4:].strip()
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if content:
                        qa.add_documents([content])
                        print(f"Added: {filepath}")
                    else:
                        print("File is empty\n")
                except FileNotFoundError:
                    print(f"File not found: {filepath}\n")
                continue

            # Normal question
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(qa.ask(user_input, conv_id))
            loop.close()

            print(f"\nAI> {result.answer}")
            print(f"   Confidence: {result.confidence:.2%} | "
                  f"Time: {result.query_time_ms}ms | "
                  f"Sources: {len(result.source_documents)}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
            logger.error(f"Interactive error: {e}")


def main():
    import sys

    qa = QASystem()
    asyncio.run(qa.initialize())

    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        print("Starting API server... Use: uvicorn api.app:app --reload")
        print("Then: curl -X POST http://localhost:8000/ask -H 'Content-Type: application/json' -d '{\"question\": \"...\"}'")
        return

    interactive_mode(qa)


if __name__ == "__main__":
    main()
