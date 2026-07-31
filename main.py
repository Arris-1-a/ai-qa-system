#!/usr/bin/env python3
"""
AI Question Answering System - Knowledge-based Q&A engine
Supports vector search, multi-turn conversation, and API service
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import numpy as np
import yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('logs/qa.log'), logging.StreamHandler()]
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
    """Lightweight vector store for semantic search."""

    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.documents: List[Dict] = []
        self.vectors: List[List[float]] = []

    def add(self, texts: List[str], ids: Optional[List[str]] = None) -> List[str]:
        doc_ids = ids or [f"doc_{i}" for i in range(len(texts))]
        for text, did in zip(texts, doc_ids):
            embedding = self._embed(text)
            self.documents.append({
                'id': did, 'text': text, 'embedding': embedding
            })
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
        """Simple hash-based embedding for demo purposes.
        In production, use sentence-transformers or similar."""
        np.random.seed(abs(hash(text)) % (2**32))
        vec = np.random.randn(self.dimension).tolist()
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0

    def clear(self) -> None:
        self.documents.clear()
        self.vectors.clear()


class ResponseGenerator:
    """Generates natural language responses based on retrieved context."""

    PROMPT_TEMPLATE = """Please answer the following question based on the provided context.

Context:
{context}

Question: {question}

Answer (cite sources when possible):"""

    FALLBACK_ANSWER = (
        "I'm sorry, I don't have enough information to answer this question. "
        "Please try rephrasing your question or consult the relevant documentation."
    )

    def generate(self, context_docs: List[Dict], question: str) -> AnswerResult:
        context_text = "\n\n".join([
            f"[Source: {doc['id']}] {doc['content'][:2000]}"
            for doc in context_docs
        ])

        prompt = self.PROMPT_TEMPLATE.format(
            context=context_text, question=question
        )

        answer = self._generate_response(prompt, question, context_text)

        avg_confidence = np.mean([d.get('score', 0.5) for d in context_docs]) if context_docs else 0.3
        avg_confidence = min(1.0, max(0.0, avg_confidence))

        return AnswerResult(
            answer=answer,
            source_documents=context_docs,
            confidence=float(avg_confidence),
            query_time_ms=0,
            timestamp=datetime.now().isoformat()
        )

    def _generate_response(self, prompt: str, question: str, context: str) -> str:
        """In production, call OpenAI/GPT-4 API here.
        For demo, provide context-aware response."""
        keywords_in_question = question.lower().split()
        relevant_context = []

        for kw in keywords_in_question:
            if len(kw) > 2:
                matches = [c for c in context.split('. ') if kw in c.lower()]
                relevant_context.extend(matches[:2])

        unique_relevant = list(dict.fromkeys(relevant_context))[:3]

        if unique_relevant:
            return (
                f"Based on the available documents:\n\n"
                + "\n\n".join(f"- {p}" for p in unique_relevant)
                + "\n\nPlease refer to the source documents for more details."
            )

        return self.FALLBACK_ANSWER


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
        if len(self.conversations[conv_id]) > self.max_history * 2:
            self.conversations[conv_id] = self.conversations[conv_id][-self.max_history * 2:]

    def get_history(self, conv_id: str) -> List[str]:
        if conv_id not in self.conversations:
            return []
        return [entry.question for entry in self.conversations[conv_id]]

    def get_context_for_question(self, conv_id: str, current_q: str) -> str:
        history = self.get_history(conv_id)
        if not history:
            return current_q
        recent = history[-4:]
        return "\n\nPrevious conversation:\n" + "\n".join(recent) + f"\n\nCurrent question: {current_q}"

    def clear(self, conv_id: str) -> bool:
        if conv_id in self.conversations:
            del self.conversations[conv_id]
            return True
        return False


class QASystem:
    """Main QA system combining search, generation, and conversation."""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.vector_store = VectorStore()
        self.generator = ResponseGenerator()
        self.conversation_manager = ConversationManager(
            max_history=self.config.get('conversation', {}).get('max_history', 5)
        )
        self.is_initialized = False

    def _load_config(self, config_path: str) -> Dict:
        defaults = {
            'search': {'top_k': 5},
            'conversation': {'max_history': 5},
            'output': {'format': 'json'}
        }
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or defaults
        return defaults

    async def initialize(self) -> None:
        await asyncio.sleep(0)  # Placeholder for async init
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

        docs = self.vector_store.search(full_question, top_k=self.config['search']['top_k'])

        result = self.generator.generate(docs, full_question)
        result.conversation_id = conversation_id
        result.query_time_ms = int(datetime.now().timestamp() * 1000) - start_ms

        self.conversation_manager.add_turn(conversation_id, question, result.answer)
        logger.info(f"Q: {question[:60]}... | Confidence: {result.confidence:.2%}")
        return result

    def add_documents(self, texts: List[str]) -> List[str]:
        ids = self.vector_store.add(texts)
        logger.info(f"Added {len(texts)} documents to knowledge base")
        return ids

    def get_stats(self) -> Dict:
        return {
            'document_count': len(self.vector_store.documents),
            'initialized': self.is_initialized,
            'active_conversations': len(self.conversation_manager.conversations)
        }


def interactive_mode(qa: QASystem) -> None:
    print("\n" + "=" * 50)
    print("🤖 AI Question Answering System")
    print("=" * 50)
    print("Type 'help' for commands, 'quit' to exit\n")

    conv_id = None

    while True:
        try:
            user_input = input("You> ").strip()
            if not user_input:
                continue

            if user_input.lower() == 'quit' or user_input.lower() == 'exit':
                break

            if user_input.lower() == 'help':
                print("""
Commands:
  help          Show this help
  quit          Exit the program
  add <file>    Add document from file to knowledge base
  clear         Clear current conversation
  new           Start a new conversation
  stats         Show system statistics
  load <file>   Load JSON knowledge base
""")
                continue

            if user_input.lower() == 'clear':
                if conv_id:
                    qa.conversation_manager.clear(conv_id)
                    conv_id = None
                    print("✅ Conversation cleared\n")
                continue

            if user_input.lower() == 'new':
                conv_id = qa.conversation_manager.create()
                print(f"✅ New conversation started\n")
                continue

            if user_input.lower() == 'stats':
                stats = qa.get_stats()
                print(f"\n📊 Stats: docs={stats['document_count']}, "
                      f"conversations={stats['active_conversations']}\n")
                continue

            if user_input.lower().startswith('add '):
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

            # Normal question
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                qa.ask(user_input, conv_id)
            )
            loop.close()

            print(f"\nAI> {result.answer}")
            print(f"   💡 Confidence: {result.confidence:.2%} "
                  f"| Time: {result.query_time_ms}ms "
                  f"| Sources: {len(result.source_documents)}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            logger.error(f"Interactive error: {e}")


def main():
    import sys

    qa = QASystem()

    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        print("Starting API server... Use: uvicorn api.app:app --reload")
        print("Then: curl -X POST http://localhost:8000/ask -H 'Content-Type: application/json' -d '{\"question\": \"...\"}'")
        return

    asyncio.run(qa.initialize())
    interactive_mode(qa)


if __name__ == "__main__":
    main()
