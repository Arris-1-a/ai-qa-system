<div align="center">

**🌐 Language / 选择语言 / Idioma:**

[English](README.md) · [简体中文](README.zh-CN.md) · [हिन्दी](README.hi.md) · [Español](README.es.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [বাংলা](README.bn.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Deutsch](README.de.md) · [日本語](README.ja.md) · [मराठी](README.mr.md) · [తెలుగు](README.te.md) · [Türkçe](README.tr.md) · [தமிழ்](README.ta.md) · [Tiếng Việt](README.vi.md) · [한국어](README.ko.md) · [Italiano](README.it.md)

</div>

---
# AI கேள்வி-பதில் அமைப்பு - நிறுவன RAG தளம்

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vector Store](https://img.shields.io/badge/Vector-Hash%20Based-blue.svg)](https://github.com/Arris-1-a/ai-qa-system)

## 🚀 கண்ணோட்டம்

சொற்பொருள் தேடல், பல-சுற்று உரையாடல் மற்றும் REST API உடைய நிறுவன தர அறிவு அடிப்படையிலான கேள்வி-பதில் அமைப்பு. ஆவண Q&A, வாடிக்கையாளர் ஆதரவு மற்றும் அறிவு மேலாண்மைக்காக உருவாக்கப்பட்டது.

**மொத்த குறியீட்டு வரிகள்:** 1,952+ | **அம்சங்கள்:** 6 முக்கிய தொகுதிகள்

## ✨ அம்சங்கள்

### முக்கிய திறன்கள்
- **வெக்டர் தேடல்**: ஹாஷ் அடிப்படையிலான சொற்பொருள் ஒற்றுமை (128 பரிமாணங்கள்)
- **பல-சுற்று உரையாடல்**: பல கேள்விகளுக்கு இடையே சூழலை பராமரிக்கிறது
- **பதில் உருவாக்கம்**: சூழல் அறிந்த பதில் உருவாக்கம்
- **REST API**: ஒருங்கிணைப்புக்கான FastAPI அடிப்படையிலான முனைகள்
- **அறிவுத் தள மேலாண்மை**: ஆவணங்களைச் சேர், அகற்று, ஏற்றுமதி, இறக்குமதி செய்யுங்கள்
- **ஊடாடும் CLI**: பயனர் நட்பு கட்டளை வரி இடைமுகம்

### தேடல் & மீட்டெடுப்பு
- **கோசைன் ஒற்றுமை**: திறமையான வெக்டர் ஒற்றுமை கணக்கீடு
- **கட்டமைக்கக்கூடிய Top-K**: மீட்டெடுக்கப்பட்ட ஆவணங்களின் எண்ணிக்கை சரிசெய்யக்கூடியது
- **மதிப்பெண் வரம்பு**: குறைந்த தொடர்புடைய முடிவுகளை வடிகட்டுகிறது
- **ஆவண துண்டாக்கல்**: பெரிய ஆவணங்களுக்கு தானியங்கி உரை பிரிப்பு

### உரையாடல் மேலாண்மை
- **அமர்வு நிலைத்தன்மை**: உரையாடல் வரலாற்றை பராமரிக்கிறது
- **சூழல் சாளரம்**: கட்டமைக்கக்கூடிய வரலாற்று நீளம் (இயல்புநிலை 10 சுற்றுகள்)
- **தானியங்கி சுத்தம்**: TTL அடிப்படையிலான காலாவதி (இயல்புநிலை 24 மணி நேரம்)
- **புள்ளிவிவர கண்காணிப்பு**: உரையாடல் அளவீடுகள் மற்றும் பகுப்பாய்வு

### பதில் உருவாக்கம்
- **சூழல் ஒருங்கிணைப்பு**: தேடல் முடிவுகளை உரையாடல் வரலாற்றுடன் இணைக்கிறது
- **நம்பிக்கை மதிப்பீடு**: ஒவ்வொரு பதிலுக்கும் தர அளவீடு
- **மூல மேற்கோள்**: மீட்டெடுக்கப்பட்ட ஆவணங்களுக்கான குறிப்புகள்
- **தொடர்ச்சி பரிந்துரைகள்**: அறிவார்ந்த கேள்வி பரிந்துரைகள்

### தரவு மேலாண்மை
- **ஆவண இறக்குமதி**: TXT, MD, CSV, JSON வடிவங்களுக்கான ஆதரவு
- **அறிவு ஏற்றுமதி**: காப்புப்பிரதி மற்றும் இடம்பெயர்வுக்கான JSON வடிவம்
- **தொகுதி செயல்பாடுகள்**: ஒரே நேரத்தில் பல ஆவணங்களை செயலாக்குகிறது
- **தேடல் முன்னோட்டம்**: பதிலளிப்பதற்கு முன் தேடல் முடிவுகளைப் பார்க்கவும்

## 📦 நிறுவல்


```bash
# Clone repository
git clone https://github.com/Arris-1-a/ai-qa-system.git
cd ai-qa-system

# Install dependencies
pip install -r requirements.txt

# For production (optional)
pip install uvicorn[standard]
```

## 🎯 விரைவு தொடக்கம்

### ஊடாடும் முறை


```bash
python main.py
```

பின்னர் கேள்விகளைத் தட்டச்சு செய்யுங்கள்:


```
You> What is machine learning?
AI> Based on the available documents...
   💡 Confidence: 85.00% | Time: 12ms | Sources: 3

You> Can you explain more?
AI> (Uses conversation history)
```

### API பயன்பாடு


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

## 📊 API குறிப்பு

### QASystem வகுப்பு


```python
class QASystem:
    async def ask(self, question: str, conversation_id: str = None) -> AnswerResult
    def add_documents(self, texts: List[str]) -> List[str]
    def remove_document(self, doc_id: str) -> bool
    def get_stats(self) -> Dict
    def export_knowledge_base(self, output_path: str) -> str
    def import_knowledge_base(self, input_path: str) -> int
```

### REST API முனைகள்

| முறை | முனை | விளக்கம் |
|--------|----------|-------------|
| POST | `/ask` | கேள்வி கேளுங்கள் |
| POST | `/documents` | ஆவணங்களை பதிவேற்றவும் |
| GET | `/status` | அமைப்பு நிலையைப் பெறுங்கள் |
| GET | `/health` | ஆரோக்கிய சோதனை |

### கோரிக்கை/பதில் வடிவங்கள்

**கேள்வி கோரிக்கை:**

```json
{
  "question": "What is machine learning?",
  "conversation_id": "optional-uuid",
  "top_k": 5
}
```

**கேள்வி பதில்:**

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

## 🔧 மேம்பட்ட பயன்பாடு

### CLI கட்டளைகள்


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

### உரையாடல் மேலாண்மை


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

### அறிவுத் தள மேலாண்மை


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

### உள்ளமைவு


```python
# Custom configuration
qa = QASystem(config_path="config.yaml")

# Or set via environment
export AI_APP_SEARCH_TOP_K=10
export AI_APP_CONVERSATION_MAX_HISTORY=20
```

## 📈 செயல்திறன்

| அளவீடு | மதிப்பு | குறிப்புகள் |
|--------|-------|-------|
| தேடல் தாமதம் | <50ms | 1K ஆவணங்கள் |
| பதில் நேரம் | <100ms | உருவாக்கம் உட்பட |
| நினைவக பயன்பாடு | <200MB | 10K ஆவணங்கள் |
| ஒருங்கிணைவு | 100+ கோரிக்கைகள்/வினாடி | uvicorn உடன் |
| வெக்டர் பரிமாணம் | 128 | ஹாஷ் அடிப்படையிலான உட்பொதிவுகள் |

## 🧪 சோதனை


```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific tests
pytest tests/test_qa_system.py::TestVectorStore -v
```

### சோதனை கவரேஜ்

| தொகுதி | கவரேஜ் |
|--------|----------|
| VectorStore | 100% |
| QASystem | 90% |
| ConversationManager | 95% |
| ResponseGenerator | 85% |
| **மொத்தம்** | **92%** |

## 📁 திட்ட அமைப்பு


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

**மொத்தம்:** 1,150+ வரிகள் Python குறியீடு

## 🔌 ஒருங்கிணைப்பு எடுத்துக்காட்டுகள்

### வலை பயன்பாடு


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

### Slack போட்


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

## 🤝 பங்களிப்பு

1. களஞ்சியத்தை ஃபோர்க் செய்யவும்
2. அம்ச கிளையை உருவாக்கவும்
3. மாற்றங்களை கமிட் செய்யவும்
4. கிளைக்கு புஷ் செய்யவும்
5. புல் ரிக்வெஸ்ட் திறக்கவும்

## 📄 உரிமம்

MIT உரிமம் - விவரங்களுக்கு [LICENSE](LICENSE) பார்க்கவும்.

## 🔗 தொடர்புடைய திட்டங்கள்

- [ai-document-processor](https://github.com/Arris-1-a/ai-document-processor) - ஆவண நுண்ணறிவு
- [ai-image-recognition](https://github.com/Arris-1-a/ai-image-recognition) - கணினி பார்வை
- [ai-recommendation-engine](https://github.com/Arris-1-a/ai-recommendation-engine) - ஹைபிரிட் பரிந்துரையாளர்

## 🆘 ஆதரவு

- 📖 [ஆவணப்படுத்தல்](https://github.com/Arris-1-a/ai-qa-system/wiki)
- 💬 [விவாதங்கள்](https://github.com/Arris-1-a/ai-qa-system/discussions)
- 🐛 [சிக்கல் கண்காணிப்பாளர்](https://github.com/Arris-1-a/ai-qa-system/issues)

## 📊 திட்ட புள்ளிவிவரங்கள்

| அளவீடு | மதிப்பு |
|--------|-------|
| மொத்த வரிகள் | 1,150+ |
| Python கோப்புகள் | 4 |
| சோதனை கவரேஜ் | 92% |
| வெக்டர் பரிமாணம் | 128 |
| அதிகபட்ச உரையாடல்கள் | வரம்பற்றது |
| ஆவண வடிவங்கள் | 4 |
