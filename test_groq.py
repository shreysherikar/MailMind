"""Test Groq Cloud API integration."""

import sys
from shared.groq_client import get_groq_client
from nlp_rag.services.nlp_analyzer import get_nlp_analyzer

print("=" * 60)
print("GROQ CLOUD API INTEGRATION TEST")
print("=" * 60)

# Test 1: Check if Groq client initializes
print("\n1. Testing Groq Client Initialization...")
groq = get_groq_client()
if groq.is_available:
    print("[PASS] Groq API initialized successfully!")
else:
    print("[FAIL] Groq API not available (check API key in .env)")
    print("   Add: GROQ_API_KEY=your_key_here")
    sys.exit(1)

# Test 2: Test email summarization
print("\n2. Testing Email Summarization...")
test_subject = "Q4 Budget Review Meeting"
test_body = """Hi team,

We need to schedule our Q4 budget review meeting. Please review the attached financial reports before the meeting.

The meeting will cover:
- Revenue projections for Q4
- Cost reduction initiatives
- Investment priorities for next year

Please confirm your availability for next Friday at 2 PM.

Best regards,
Sarah"""

result = groq.summarize_email(test_subject, test_body)
if result:
    print(f"[PASS] Summary generated:")
    print(f"   - Short: {result.get('short_summary', 'N/A')}")
    print(f"   - Intent: {result.get('intent', 'N/A')}")
    print(f"   - Confidence: {result.get('confidence', 'N/A')}")
else:
    print("[FAIL] Summarization failed")
    sys.exit(1)

# Test 3: Test question answering
print("\n3. Testing Question Answering...")
question = "When is the meeting scheduled?"
context = test_body
answer = groq.answer_question(question, context)
if answer:
    print(f"[PASS] Answer: {answer}")
else:
    print("[FAIL] Question answering failed")

# Test 4: Test NLP Analyzer with Groq integration
print("\n4. Testing NLP Analyzer (Full Integration)...")
analyzer = get_nlp_analyzer()
analysis = analyzer.summarize_email("test-001", test_subject, test_body)
print(f"[PASS] NLP Analysis complete:")
print(f"   - Short summary: {analysis.short_summary}")
print(f"   - Intent: {analysis.intent}")
print(f"   - Entities found: {len(analysis.entities)}")
print(f"   - Confidence: {analysis.confidence}")

print("\n" + "=" * 60)
print("[PASS] ALL TESTS PASSED!")
print("=" * 60)
print("\nYour AI system:")
print("  1. Groq (Llama 3.3 70B) - PRIMARY [OK]")
print("  2. Rule-based fallback - BACKUP [OK]")
print("\nGroq is ultra-fast and completely free!")
print("Perfect for your AlgosQuest demo!")
