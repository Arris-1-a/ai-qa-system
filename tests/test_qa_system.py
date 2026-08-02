"""Tests for AI Q&A System."""

import pytest
import asyncio
from main import QASystem, AnswerResult, VectorStore, ResponseGenerator


class TestVectorStore:
    def test_add_and_search(self):
        store = VectorStore(dimension=32)
        docs = ["Machine learning is a subset of AI.",
                "Deep learning uses neural networks."]
        ids = store.add(docs)
        assert len(ids) == 2

        results = store.search("What is AI?", top_k=1)
        assert len(results) == 1
        assert results[0].score > 0

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

    def test_count(self):
        store = VectorStore()
        assert store.count() == 0
        store.add(["doc1", "doc2"])
        assert store.count() == 2


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


class TestKnowledgeManager:
    def test_add_from_file(self, qa):
        """Test adding documents from file."""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test document content for knowledge base.")
            filepath = f.name
        
        km = KnowledgeManager(qa)
        count = km.add_from_file(filepath)
        assert count == 1
        
        os.unlink(filepath)
    
    def test_get_document_count(self, qa):
        """Test getting document count."""
        qa.add_documents(["Doc 1", "Doc 2", "Doc 3"])
        assert qa.vector_store.count() == 3
    
    def test_list_documents(self, qa):
        """Test listing documents."""
        qa.add_documents(["Document 1", "Document 2"])
        docs = qa.vector_store.documents
        assert len([d for d in docs if d is not None]) == 2


class TestConversationHistory:
    def test_save_and_load(self, qa):
        """Test saving and loading conversation history."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            history = ConversationHistory(tmpdir)
            
            # Save
            conv_id = qa.conversation_manager.create()
            history.save(conv_id, [{"question": "Hello", "answer": "Hi"}])
            
            # Load
            loaded = history.load(conv_id)
            assert loaded is not None
            assert loaded['conversation_id'] == conv_id
            
            # List
            conversations = history.list_conversations()
            assert len(conversations) == 1
            
            # Delete
            assert history.delete(conv_id)
            assert history.load(conv_id) is None
