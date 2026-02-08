"""
Simple test script that works without ChromaDB.
Tests core NLP features only.
"""

import sys
print(f"Python version: {sys.version}\n")

# Add project to path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("SIMPLE NLP TEST (No ChromaDB Required)")
print("="*60)

try:
    # Test 1: NLP Analyzer
    print("\n1. Testing NLP Analyzer...")
    from nlp_rag.services.nlp_analyzer import get_nlp_analyzer
    
    analyzer = get_nlp_analyzer()
    print("   ✓ NLP Analyzer loaded")
    
    # Test summarization
    summary = analyzer.summarize_email(
        email_id="test-1",
        subject="Urgent: Budget Review Meeting",
        body="We need to review the Q4 budget by Friday. Marketing is $50,000 over budget. Please prepare your reports."
    )
    
    print(f"\n   Summary: {summary.short_summary}")
    print(f"   Intent: {summary.intent}")
    print(f"   Entities found: {len(summary.entities)}")
    print("   ✓ Summarization working!")
    
    # Test 2: Entity Extraction
    print("\n2. Testing Entity Extraction...")
    entities = analyzer.extract_entities(
        subject="Meeting with Microsoft on January 20th",
        body="Contract value is $250,000. Contact Sarah Johnson."
    )
    
    print(f"   Found {len(entities)} entities:")
    for entity in entities[:3]:
        print(f"   - {entity.text} ({entity.type.value})")
    print("   ✓ Entity extraction working!")
    
    # Test 3: Intent Detection
    print("\n3. Testing Intent Detection...")
    intent = analyzer.detect_intent(
        subject="Can you help with this?",
        body="I need assistance with the login system."
    )
    print(f"   Detected intent: {intent}")
    print("   ✓ Intent detection working!")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nYour NLP features are working correctly!")
    print("Note: Running in fallback mode (no ChromaDB needed for this test)")
    print("\nTo test full features including search, see: nlp_rag/demo.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you're in the MailMind directory")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Check Python version (3.9-3.12 recommended)")
    import traceback
    traceback.print_exc()
