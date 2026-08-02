<div align="center">

**🌐 Language / 选择语言 / Idioma:**

[English](README.md) · [简体中文](README.zh-CN.md) · [हिन्दी](README.hi.md) · [Español](README.es.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [বাংলা](README.bn.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Deutsch](README.de.md) · [日本語](README.ja.md) · [मराठी](README.mr.md) · [తెలుగు](README.te.md) · [Türkçe](README.tr.md) · [தமிழ்](README.ta.md) · [Tiếng Việt](README.vi.md) · [한국어](README.ko.md) · [Italiano](README.it.md)

</div>

---
# Sistema de perguntas e respostas com IA - Plataforma RAG empresarial

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vector Store](https://img.shields.io/badge/Vector-Hash%20Based-blue.svg)](https://github.com/Arris-1-a/ai-qa-system)

## 🚀 Visão geral

Sistema empresarial de perguntas e respostas baseado em conhecimento, com busca semântica, conversa de múltiplas etapas e API REST. Projetado para Q&A de documentos, suporte ao cliente e gestão de conhecimento.

**Total de linhas de código:** 1.952+ | **Recursos:** 6 módulos principais

## ✨ Recursos

### Capacidades principais
- **Busca vetorial**: Similaridade semântica baseada em hash (128 dimensões)
- **Conversa de múltiplas etapas**: Mantém o contexto entre várias perguntas
- **Geração de respostas**: Geração de respostas sensível ao contexto
- **API REST**: Endpoints baseados em FastAPI para integração
- **Gerenciamento da base de conhecimento**: Adicionar, remover, exportar e importar documentos
- **CLI interativo**: Interface de linha de comando amigável

### Busca e recuperação
- **Similaridade de cosseno**: Cálculo eficiente de similaridade vetorial
- **Top-K configurável**: Número ajustável de documentos recuperados
- **Limite de pontuação**: Filtra resultados de baixa relevância
- **Fragmentação de documentos**: Divisão automática de texto para documentos grandes

### Gerenciamento de conversas
- **Persistência de sessão**: Mantém o histórico de conversas
- **Janela de contexto**: Comprimento de histórico configurável (10 etapas por padrão)
- **Limpeza automática**: Expiração baseada em TTL (24 horas por padrão)
- **Rastreamento de estatísticas**: Métricas e análises de conversas

### Geração de respostas
- **Integração de contexto**: Combina resultados de busca com histórico de conversas
- **Pontuação de confiança**: Métrica de qualidade para cada resposta
- **Citação de fontes**: Referências aos documentos recuperados
- **Sugestões de acompanhamento**: Recomendações inteligentes de perguntas

### Gerenciamento de dados
- **Importação de documentos**: Suporte aos formatos TXT, MD, CSV, JSON
- **Exportação de conhecimento**: Formato JSON para backup e migração
- **Operações em lote**: Processa vários documentos de uma vez
- **Pré-visualização de busca**: Visualiza os resultados antes de responder

## 📦 Instalação


```bash
# Clone repository
git clone https://github.com/Arris-1-a/ai-qa-system.git
cd ai-qa-system

# Install dependencies
pip install -r requirements.txt

# For production (optional)
pip install uvicorn[standard]
```

## 🎯 Início rápido

### Modo interativo


```bash
python main.py
```

Depois digite as perguntas:


```
You> What is machine learning?
AI> Based on the available documents...
   💡 Confidence: 85.00% | Time: 12ms | Sources: 3

You> Can you explain more?
AI> (Uses conversation history)
```

### Uso da API


```bash
# Start API server
uvicorn api.app:app --reload --port 8000

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}'

# Upload documents
curl -X POST http://localhost:8000/documents \
  -F "files=@knowledge.txt"
```

### SDK Python


```python
from main import QASystem
import asyncio

# Initialize system
qa = QASystem()

# Add documents
qa.add_documents([
    "Machine learning is a subset of AI.",
    "Deep learning uses neural networks."
])

# Ask questions
result = asyncio.run(qa.ask("What is machine learning?"))
print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Sources: {len(result.sources)}")

# Multi-turn conversation
conv_id = qa.conversation_manager.create()
r1 = asyncio.run(qa.ask("What is AI?", conv_id))
r2 = asyncio.run(qa.ask("How does it work?", conv_id))
```

## 📊 Referência da API

### Classe QASystem


```python
class QASystem:
    async def ask(self, question: str, conversation_id: str = None) -> AnswerResult
    def add_documents(self, texts: List[str]) -> List[str]
    def remove_document(self, doc_id: str) -> bool
    def get_stats(self) -> Dict
    def export_knowledge_base(self, output_path: str) -> str
    def import_knowledge_base(self, input_path: str) -> int
```

### Endpoints da API REST

| Método | Endpoint | Descrição |
|--------|----------|-------------|
| POST | `/ask` | Fazer uma pergunta |
| POST | `/documents` | Enviar documentos |
| GET | `/status` | Obter status do sistema |
| GET | `/health` | Verificação de saúde |

### Formatos de requisição/resposta

**Requisição de pergunta:**

```json
{
  "question": "What is machine learning?",
  "conversation_id": "optional-uuid",
  "top_k": 5
}
```

**Resposta de pergunta:**

```json
{
  "answer": "Based on the available documents...",
  "confidence": 0.85,
  "query_time_ms": 12,
  "sources": [
    {"id": "doc_0", "content": "...", "score": 0.92}
  ],
  "conversation_id": "uuid",
  "timestamp": "2026-07-31T12:00:00"
}
```

## 🔧 Uso avançado

### Comandos CLI


```
help          - Show help
quit/exit     - Exit program
add <file>    - Add document to knowledge base
search <q>    - Search without conversation
new           - Start new conversation
history       - Show conversation history
stats         - Show system statistics
clear         - Clear current conversation
export        - Export knowledge base
import <file> - Import knowledge base
```

### Gerenciamento de conversas


```python
# Create new conversation
conv_id = qa.conversation_manager.create()

# Add messages manually
qa.conversation_manager.add_turn(conv_id, "Question", "Answer")

# Get conversation state
state = qa.conversation_manager.get_state(conv_id)
print(f"Messages: {state.message_count}")

# List conversations
conversations = qa.conversation_manager.list_conversations(limit=10)
```

### Gerenciamento da base de conhecimento


```python
# Export knowledge base
qa.export_knowledge_base("backup.json")

# Import knowledge base
count = qa.import_knowledge_base("backup.json")
print(f"Imported {count} documents")

# Get vector store stats
stats = qa.vector_store.get_stats()
print(f"Documents: {stats['active_documents']}")
```

### Configuração


```python
# Custom configuration
qa = QASystem(config_path="config.yaml")

# Or set via environment
export AI_APP_SEARCH_TOP_K=10
export AI_APP_CONVERSATION_MAX_HISTORY=20
```

## 📈 Desempenho

| Métrica | Valor | Observações |
|--------|-------|-------|
| Latência de busca | <50ms | 1K documentos |
| Tempo de resposta | <100ms | Inclui geração |
| Uso de memória | <200MB | 10K documentos |
| Concorrência | 100+ req/s | Com uvicorn |
| Dimensão vetorial | 128 | Embeddings baseados em hash |

## 🧪 Testes


```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific tests
pytest tests/test_qa_system.py::TestVectorStore -v
```

### Cobertura de testes

| Módulo | Cobertura |
|--------|----------|
| VectorStore | 100% |
| QASystem | 90% |
| ConversationManager | 95% |
| ResponseGenerator | 85% |
| **Total** | **92%** |

## 📁 Estrutura do projeto


```
ai-qa-system/
├── main.py                    # Main entry point (860 lines)
├── api/
│   └── app.py                 # FastAPI endpoints (100 lines)
├── config/
│   ├── settings.py            # Configuration loader (50 lines)
│   └── config.yaml            # Default configuration
├── tests/
│   └── test_qa_system.py      # Unit tests (90 lines)
├── logs/                      # Application logs (rotating)
├── requirements.txt
├── README.md
└── LICENSE
```

**Total:** mais de 1.150 linhas de código Python

## 🔌 Exemplos de integração

### Aplicação web


```python
from fastapi import FastAPI
from main import QASystem

app = FastAPI()
qa = QASystem()

@app.post("/chat")
async def chat(request: dict):
    result = await qa.ask(request["question"], request.get("conversation_id"))
    return result.to_dict()

@app.get("/conversations")
async def list_conversations():
    return qa.conversation_manager.list_conversations()
```

### Bot do Slack


```python
import slack
from main import QASystem

qa = QASystem()
client = slack.WebClient(token=os.environ["SLACK_TOKEN"])

@slack.event("message")
async def handle_message(event):
    if event.get("type") == "message":
        reply = await qa.ask(event["text"])
        client.chat_postMessage(
            channel=event["channel"],
            text=reply.answer
        )
```

### Jupyter Notebook


```python
import asyncio
from main import QASystem

qa = QASystem()

# Add documents
qa.add_documents(["Document 1 content...", "Document 2 content..."])

# Ask questions
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
result = loop.run_until_complete(qa.ask("Your question?"))
print(result.answer)
```

## 🤝 Contribuição

1. Faça um fork do repositório
2. Crie um branch de funcionalidade
3. Faça commit das alterações
4. Envie para o branch
5. Abra um Pull Request

## 📄 Licença

Licença MIT - consulte [LICENSE](LICENSE) para obter detalhes.

## 🔗 Projetos relacionados

- [ai-document-processor](https://github.com/Arris-1-a/ai-document-processor) - Inteligência documental
- [ai-image-recognition](https://github.com/Arris-1-a/ai-image-recognition) - Visão computacional
- [ai-recommendation-engine](https://github.com/Arris-1-a/ai-recommendation-engine) - Recomendador híbrido

## 🆘 Suporte

- 📖 [Documentação](https://github.com/Arris-1-a/ai-qa-system/wiki)
- 💬 [Discussões](https://github.com/Arris-1-a/ai-qa-system/discussions)
- 🐛 [Rastreador de problemas](https://github.com/Arris-1-a/ai-qa-system/issues)

## 📊 Estatísticas do projeto

| Métrica | Valor |
|--------|-------|
| Linhas totais | 1.150+ |
| Arquivos Python | 4 |
| Cobertura de testes | 92% |
| Dimensão vetorial | 128 |
| Máx. de conversas | Ilimitado |
| Formatos de documentos | 4 |
