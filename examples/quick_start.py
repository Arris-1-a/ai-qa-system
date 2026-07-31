"""Quick Start Guide for AI QA System"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import QASystem

async def main():
    qa = QASystem()
    
    print("🤖 AI Question Answering System - Quick Start")
    print("=" * 50)
    
    # Add documents to knowledge base
    print("\n📚 Adding documents to knowledge base...")
    qa.add_documents([
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning uses neural networks with multiple layers.",
        "Natural language processing helps computers understand text.",
        "Computer vision enables machines to see and interpret images."
    ])
    
    print("✅ Added 4 documents")
    
    # Ask questions
    print("\n❓ Asking questions...")
    
    questions = [
        "What is machine learning?",
        "How does deep learning work?",
        "What is NLP?"
    ]
    
    for question in questions:
        result = await qa.ask(question)
        print(f"\nQ: {question}")
        print(f"A: {result.answer[:100]}...")
        print(f"💡 Confidence: {result.confidence:.2%}")
    
    print("\n" + "=" * 50)
    print("✅ Quick start complete!")
    print(f"📊 Stats: {qa.get_stats()}")

if __name__ == "__main__":
    asyncio.run(main())
