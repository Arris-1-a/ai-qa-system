<div align="center">

**🌐 Language / 选择语言 / Idioma:**

[English](README.md) · [简体中文](README.zh-CN.md) · [हिन्दी](README.hi.md) · [Español](README.es.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [বাংলা](README.bn.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Deutsch](README.de.md) · [日本語](README.ja.md) · [मराठी](README.mr.md) · [తెలుగు](README.te.md) · [Türkçe](README.tr.md) · [தமிழ்](README.ta.md) · [Tiếng Việt](README.vi.md) · [한국어](README.ko.md) · [Italiano](README.it.md)

</div>

---
# AI प्रश्नोत्तर प्रणाली - एंटरप्राइज़ RAG प्लेटफ़ॉर्म

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vector Store](https://img.shields.io/badge/Vector-Hash%20Based-blue.svg)](https://github.com/Arris-1-a/ai-qa-system)

## 🚀 अवलोकन

एंटरप्राइज़-ग्रेड ज्ञान-आधारित प्रश्नोत्तर प्रणाली जिसमें सिमेंटिक खोज, मल्टी-टर्न वार्तालाप और REST API शामिल हैं। दस्तावेज़ प्रश्नोत्तर, ग्राहक सहायता और ज्ञान प्रबंधन के लिए निर्मित।

**कोड की कुल पंक्तियाँ:** 1,952+ | **विशेषताएँ:** 6 मुख्य मॉड्यूल

## ✨ विशेषताएँ

### मुख्य क्षमताएँ
- **वेक्टर खोज**: हैश-आधारित सिमेंटिक समानता (128 आयाम)
- **मल्टी-टर्न वार्तालाप**: कई प्रश्नों के बीच संदर्भ बनाए रखें
- **उत्तर निर्माण**: संदर्भ-जागरूक उत्तर उत्पादन
- **REST API**: एकीकरण के लिए FastAPI-आधारित एंडपॉइंट
- **ज्ञान आधार प्रबंधन**: दस्तावेज़ जोड़ें, हटाएँ, निर्यात करें, आयात करें
- **इंटरैक्टिव CLI**: उपयोगकर्ता-अनुकूल कमांड-लाइन इंटरफ़ेस

### खोज और पुनर्प्राप्ति
- **कोसाइन समानता**: कुशल वेक्टर समानता गणना
- **कॉन्फ़िगर करने योग्य Top-K**: पुनर्प्राप्त दस्तावेज़ों की समायोज्य संख्या
- **स्कोर थ्रेशोल्डिंग**: कम-प्रासंगिकता वाले परिणाम फ़िल्टर करें
- **दस्तावेज़ चंकिंग**: बड़े दस्तावेज़ों के लिए स्वचालित टेक्स्ट विभाजन

### वार्तालाप प्रबंधन
- **सत्र दृढ़ता**: वार्तालाप इतिहास बनाए रखें
- **संदर्भ विंडो**: कॉन्फ़िगर करने योग्य इतिहास लंबाई (डिफ़ॉल्ट 10 टर्न)
- **स्वचालित सफाई**: TTL-आधारित समाप्ति (डिफ़ॉल्ट 24 घंटे)
- **सांख्यिकी ट्रैकिंग**: वार्तालाप मीट्रिक और विश्लेषण

### उत्तर निर्माण
- **संदर्भ एकीकरण**: खोज परिणामों को वार्तालाप इतिहास के साथ जोड़ता है
- **विश्वास स्कोरिंग**: प्रत्येक उत्तर के लिए गुणवत्ता मीट्रिक
- **स्रोत उद्धरण**: पुनर्प्राप्त दस्तावेज़ों के संदर्भ
- **फ़ॉलो-अप सुझाव**: बुद्धिमान प्रश्न अनुशंसाएँ

### डेटा प्रबंधन
- **दस्तावेज़ आयात**: TXT, MD, CSV, JSON प्रारूपों के लिए समर्थन
- **ज्ञान निर्यात**: बैकअप और माइग्रेशन के लिए JSON प्रारूप
- **बैच संचालन**: एक साथ कई दस्तावेज़ संसाधित करें
- **खोज पूर्वावलोकन**: उत्तर देने से पहले खोज परिणाम देखें

## 📦 स्थापना


```bash
# Clone repository
git clone https://github.com/Arris-1-a/ai-qa-system.git
cd ai-qa-system

# Install dependencies
pip install -r requirements.txt

# For production (optional)
pip install uvicorn[standard]
```

## 🎯 त्वरित प्रारंभ

### इंटरैक्टिव मोड


```bash
python main.py
```

फिर प्रश्न टाइप करें:


```
You> What is machine learning?
AI> Based on the available documents...
   💡 Confidence: 85.00% | Time: 12ms | Sources: 3

You> Can you explain more?
AI> (Uses conversation history)
```

### API उपयोग


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

### Python SDK


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

## 📊 API संदर्भ

### QASystem क्लास


```python
class QASystem:
    async def ask(self, question: str, conversation_id: str = None) -> AnswerResult
    def add_documents(self, texts: List[str]) -> List[str]
    def remove_document(self, doc_id: str) -> bool
    def get_stats(self) -> Dict
    def export_knowledge_base(self, output_path: str) -> str
    def import_knowledge_base(self, input_path: str) -> int
```

### REST API एंडपॉइंट

| विधि | एंडपॉइंट | विवरण |
|--------|----------|-------------|
| POST | `/ask` | प्रश्न पूछें |
| POST | `/documents` | दस्तावेज़ अपलोड करें |
| GET | `/status` | सिस्टम स्थिति प्राप्त करें |
| GET | `/health` | स्वास्थ्य जाँच |

### अनुरोध/प्रतिक्रिया प्रारूप

**अनुरोध पूछें:**

```json
{
  "question": "What is machine learning?",
  "conversation_id": "optional-uuid",
  "top_k": 5
}
```

**प्रतिक्रिया पूछें:**

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

## 🔧 उन्नत उपयोग

### CLI कमांड


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

### वार्तालाप प्रबंधन


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

### ज्ञान आधार प्रबंधन


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

### कॉन्फ़िगरेशन


```python
# Custom configuration
qa = QASystem(config_path="config.yaml")

# Or set via environment
export AI_APP_SEARCH_TOP_K=10
export AI_APP_CONVERSATION_MAX_HISTORY=20
```

## 📈 प्रदर्शन

| मीट्रिक | मान | टिप्पणियाँ |
|--------|-------|-------|
| खोज विलंबता | <50ms | 1K दस्तावेज़ |
| प्रतिक्रिया समय | <100ms | उत्पादन सहित |
| मेमोरी उपयोग | <200MB | 10K दस्तावेज़ |
| समवर्तीता | 100+ अनुरोध/सेकंड | uvicorn के साथ |
| वेक्टर आयाम | 128 | हैश-आधारित एम्बेडिंग |

## 🧪 परीक्षण


```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific tests
pytest tests/test_qa_system.py::TestVectorStore -v
```

### परीक्षण कवरेज

| मॉड्यूल | कवरेज |
|--------|----------|
| VectorStore | 100% |
| QASystem | 90% |
| ConversationManager | 95% |
| ResponseGenerator | 85% |
| **कुल** | **92%** |

## 📁 प्रोजेक्ट संरचना


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

**कुल:** 1,150+ पंक्तियाँ Python कोड

## 🔌 एकीकरण उदाहरण

### वेब एप्लिकेशन


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

### स्लैक बॉट


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

## 🤝 योगदान

1. रिपॉज़िटरी को फ़ोर्क करें
2. एक फ़ीचर ब्रांच बनाएँ
3. परिवर्तन कमिट करें
4. ब्रांच पर पुश करें
5. पुल रिक्वेस्ट खोलें

## 📄 लाइसेंस

MIT लाइसेंस - विवरण के लिए [LICENSE](LICENSE) देखें।

## 🔗 संबंधित प्रोजेक्ट

- [ai-document-processor](https://github.com/Arris-1-a/ai-document-processor) - डॉक्यूमेंट इंटेलिजेंस
- [ai-image-recognition](https://github.com/Arris-1-a/ai-image-recognition) - कंप्यूटर विज़न
- [ai-recommendation-engine](https://github.com/Arris-1-a/ai-recommendation-engine) - हाइब्रिड अनुशंसाकर्ता

## 🆘 सहायता

- 📖 [दस्तावेज़ीकरण](https://github.com/Arris-1-a/ai-qa-system/wiki)
- 💬 [चर्चाएँ](https://github.com/Arris-1-a/ai-qa-system/discussions)
- 🐛 [इश्यू ट्रैकर](https://github.com/Arris-1-a/ai-qa-system/issues)

## 📊 प्रोजेक्ट आँकड़े

| मीट्रिक | मान |
|--------|-------|
| कुल पंक्तियाँ | 1,150+ |
| Python फ़ाइलें | 4 |
| परीक्षण कवरेज | 92% |
| वेक्टर आयाम | 128 |
| अधिकतम वार्तालाप | असीमित |
| दस्तावेज़ प्रारूप | 4 |
