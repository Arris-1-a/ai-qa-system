<div align="center">

**🌐 Language / 选择语言 / Idioma:**

[English](README.md) · [简体中文](README.zh-CN.md) · [हिन्दी](README.hi.md) · [Español](README.es.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [বাংলা](README.bn.md) · [Português](README.pt.md) · [Русский](README.ru.md) · [اردو](README.ur.md) · [Bahasa Indonesia](README.id.md) · [Deutsch](README.de.md) · [日本語](README.ja.md) · [मराठी](README.mr.md) · [తెలుగు](README.te.md) · [Türkçe](README.tr.md) · [தமிழ்](README.ta.md) · [Tiếng Việt](README.vi.md) · [한국어](README.ko.md) · [Italiano](README.it.md)

</div>

---
# نظام الإجابة على الأسئلة بالذكاء الاصطناعي - منصة RAG مؤسسية

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vector Store](https://img.shields.io/badge/Vector-Hash%20Based-blue.svg)](https://github.com/Arris-1-a/ai-qa-system)

## 🚀 نظرة عامة

نظام إجابة على الأسئلة قائم على المعرفة بمستوى المؤسسات، مع بحث دلالي، ومحادثة متعددة الجولات، وREST API. مصمم للإجابة على أسئلة المستندات، ودعم العملاء، وإدارة المعرفة.

**إجمالي أسطر الكود:** 1,952+ | **الميزات:** 6 وحدات أساسية

## ✨ الميزات

### القدرات الأساسية
- **البحث المتجهي**: تشابه دلالي قائم على التجزئة (128 بُعدًا)
- **محادثة متعددة الجولات**: الحفاظ على السياق عبر أسئلة متعددة
- **توليد الردود**: توليد إجابات مدركة للسياق
- **REST API**: نقاط نهاية قائمة على FastAPI للتكامل
- **إدارة قاعدة المعرفة**: إضافة وحذف وتصدير واستيراد المستندات
- **CLI تفاعلي**: واجهة سطر أوامر سهلة الاستخدام

### البحث والاسترجاع
- **تشابه جيب التمام**: حساب فعال لتشابه المتجهات
- **Top-K قابل للتكوين**: عدد قابل للتعديل من المستندات المسترجعة
- **حدود الدرجات**: تصفية النتائج منخفضة الصلة
- **تقسيم المستندات**: تقسيم تلقائي للنصوص الكبيرة

### إدارة المحادثات
- **استمرارية الجلسة**: الحفاظ على سجل المحادثة
- **نافذة السياق**: طول سجل قابل للتكوين (10 جولات افتراضيًا)
- **التنظيف التلقائي**: انتهاء صلاحية قائم على TTL (24 ساعة افتراضيًا)
- **تتبع الإحصائيات**: مقاييس وتحليلات المحادثة

### توليد الردود
- **دمج السياق**: يجمع نتائج البحث مع سجل المحادثة
- **تقييم الثقة**: مقياس جودة لكل إجابة
- **الاستشهاد بالمصادر**: مراجع للمستندات المسترجعة
- **اقتراحات المتابعة**: توصيات ذكية للأسئلة

### إدارة البيانات
- **استيراد المستندات**: دعم صيغ TXT وMD وCSV وJSON
- **تصدير المعرفة**: صيغة JSON للنسخ الاحتياطي والترحيل
- **العمليات المجمعة**: معالجة مستندات متعددة دفعة واحدة
- **معاينة البحث**: معاينة النتائج قبل الإجابة

## 📦 التثبيت


```bash
# Clone repository
git clone https://github.com/Arris-1-a/ai-qa-system.git
cd ai-qa-system

# Install dependencies
pip install -r requirements.txt

# For production (optional)
pip install uvicorn[standard]
```

## 🎯 بدء سريع

### الوضع التفاعلي


```bash
python main.py
```

ثم اكتب الأسئلة:


```
You> What is machine learning?
AI> Based on the available documents...
   💡 Confidence: 85.00% | Time: 12ms | Sources: 3

You> Can you explain more?
AI> (Uses conversation history)
```

### استخدام API


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

## 📊 مرجع API

### فئة QASystem


```python
class QASystem:
    async def ask(self, question: str, conversation_id: str = None) -> AnswerResult
    def add_documents(self, texts: List[str]) -> List[str]
    def remove_document(self, doc_id: str) -> bool
    def get_stats(self) -> Dict
    def export_knowledge_base(self, output_path: str) -> str
    def import_knowledge_base(self, input_path: str) -> int
```

### نقاط نهاية REST API

| الطريقة | نقطة النهاية | الوصف |
|--------|----------|-------------|
| POST | `/ask` | طرح سؤال |
| POST | `/documents` | رفع المستندات |
| GET | `/status` | الحصول على حالة النظام |
| GET | `/health` | فحص الصحة |

### صيغ الطلب/الاستجابة

**طلب السؤال:**

```json
{
  "question": "What is machine learning?",
  "conversation_id": "optional-uuid",
  "top_k": 5
}
```

**استجابة السؤال:**

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

## 🔧 استخدام متقدم

### أوامر CLI


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

### إدارة المحادثات


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

### إدارة قاعدة المعرفة


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

### الإعدادات


```python
# Custom configuration
qa = QASystem(config_path="config.yaml")

# Or set via environment
export AI_APP_SEARCH_TOP_K=10
export AI_APP_CONVERSATION_MAX_HISTORY=20
```

## 📈 الأداء

| المقياس | القيمة | ملاحظات |
|--------|-------|-------|
| زمن البحث | <50ms | 1K مستند |
| زمن الاستجابة | <100ms | شامل التوليد |
| استخدام الذاكرة | <200MB | 10K مستند |
| التوافقية | 100+ طلب/ثانية | مع uvicorn |
| بُعد المتجه | 128 | تضمينات قائمة على التجزئة |

## 🧪 الاختبارات


```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific tests
pytest tests/test_qa_system.py::TestVectorStore -v
```

### تغطية الاختبارات

| الوحدة | التغطية |
|--------|----------|
| VectorStore | 100% |
| QASystem | 90% |
| ConversationManager | 95% |
| ResponseGenerator | 85% |
| **الإجمالي** | **92%** |

## 📁 بنية المشروع


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

**الإجمالي:** أكثر من 1,150 سطر من كود Python

## 🔌 أمثلة التكامل

### تطبيق ويب


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

### بوت Slack


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

## 🤝 المساهمة

1. انسخ المستودع (Fork)
2. أنشئ فرع ميزة
3. أرسل التغييرات (Commit)
4. ادفع إلى الفرع (Push)
5. افتح طلب سحب (Pull Request)

## 📄 الترخيص

رخصة MIT - راجع [LICENSE](LICENSE) للتفاصيل.

## 🔗 مشاريع ذات صلة

- [ai-document-processor](https://github.com/Arris-1-a/ai-document-processor) - ذكاء المستندات
- [ai-image-recognition](https://github.com/Arris-1-a/ai-image-recognition) - رؤية الكمبيوتر
- [ai-recommendation-engine](https://github.com/Arris-1-a/ai-recommendation-engine) - موصٍّ هجين

## 🆘 الدعم

- 📖 [التوثيق](https://github.com/Arris-1-a/ai-qa-system/wiki)
- 💬 [المناقشات](https://github.com/Arris-1-a/ai-qa-system/discussions)
- 🐛 [متتبع المشكلات](https://github.com/Arris-1-a/ai-qa-system/issues)

## 📊 إحصائيات المشروع

| المقياس | القيمة |
|--------|-------|
| إجمالي الأسطر | 1,150+ |
| ملفات Python | 4 |
| تغطية الاختبارات | 92% |
| بُعد المتجه | 128 |
| الحد الأقصى للمحادثات | غير محدود |
| صيغ المستندات | 4 |
