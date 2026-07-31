# AI Question Answering System
Intelligent knowledge-base powered Q&A system with vector search, multi-turn conversation, and REST API.

## Features

- **Semantic Search**: Vector-based document retrieval using cosine similarity
- **Multi-turn Conversation**: Maintains conversation context across turns
- **REST API**: FastAPI-based endpoints for integration
- **Knowledge Base**: Add documents via API or CLI for instant indexing
- **Confidence Scoring**: Each answer includes a relevance confidence metric

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

### API Usage

```bash
# Start API server
uvicorn api.app:app --reload --port 8000

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is deep learning?"}'

# Upload documents
curl -X POST http://localhost:8000/documents \
  -F "files=@knowledge.txt"
```

## Architecture

```
User Request → VectorSearch → ResponseGenerator → ConversationManager
                                        ↓
                              AnswerResult (with sources & confidence)
```

## Testing

```bash
pytest tests/ -v --cov
```
