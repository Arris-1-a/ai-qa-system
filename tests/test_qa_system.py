"""Tests for AI Q&A System."""

import pytest
import asyncio
from main import QASystem, AnswerResult, VectorStore, ResponseGenerator


class TestVectorStore:
    def test_add_and_search(self):
        store = VectorStore(dimension=10)
        docs = ["Machine learning is a subset of AI.",
                "Deep learning uses neural networks."]
        ids = store.add(docs)
        assert len(ids) == 2

        results = store.search("What is AI?", top_k=1)
        assert len(results) == 1
        assert results[0]['score'] > 0

    def test_empty_search(self):
        store = VectorStore()
        results = store.search("anything")
        assert results == []

    def test_clear(self):
        store = VectorStore()
        store.add(["test doc"])
        assert len(store.documents) == 1
        store.clear()
        assert len(store.documents) == 0


class TestQASystem:
    @pytest.fixture
    def qa(self):
        system = QASystem()
        asyncio.run(system.initialize())
        return system

    def test_ask_returns_result(self, qa):
        result = asyncio.run(qa.ask("What is machine learning?"))
        assert isinstance(result, AnswerResult)
        assert result.answer.strip() != ""

    def test_add_documents(self, qa):
        ids = qa.add_documents(["AI stands for Artificial Intelligence."])
        assert len(ids) == 1

    def test_stats(self, qa):
        stats = qa.get_stats()
        assert 'document_count' in stats
        assert 'initialized' in stats

    def test_conversation_history(self, qa):
        conv_id = qa.conversation_manager.create()
        qa.conversation_manager.add_turn(conv_id, "Hello", "Hi there!")
        history = qa.conversation_manager.get_history(conv_id)
        assert len(history) >= 1

    def test_multiple_questions_same_conversation(self, qa):
        conv_id = qa.conversation_manager.create()
        r1 = asyncio.run(qa.ask("What is Python?", conv_id))
        r2 = asyncio.run(qa.ask("Is it a snake?", conv_id))
        assert r1.conversation_id == r2.conversation_id
