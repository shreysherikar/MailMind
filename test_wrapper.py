
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "priority_scoring"))
sys.path.append(os.path.dirname(__file__))  # Add root logic

from priority_scoring.services.gemini_client import GeminiClient
from models.schemas import Email

def test_wrapper():
    print("Initializing GeminiClient (should use Groq wrapper)...")
    client = GeminiClient()
    
    if client.is_available:
        print("[PASS] Client is available via Groq!")
    else:
        print("[FAIL] Client is NOT available.")
        return

    print("\nTesting Tone Analysis (via Groq)...")
    tone = client.analyze_tone("This is urgent! calling you now!")
    print(f"Tone Result: {tone}")
    if tone and "urgency" in tone:
        print("[PASS] Tone analysis returned valid data")
    else:
        print("[FAIL] Tone analysis failed")

    print("\nTesting Task Extraction (via Groq)...")
    tasks = client.extract_tasks("Subject: Work", "Body: Please finish the report by Friday.")
    print(f"Tasks Result: {tasks}")
    if isinstance(tasks, list):
         print("[PASS] Task extraction returned a list")
         if len(tasks) > 0:
             print(f"   Found {len(tasks)} tasks: {tasks[0].get('title')}")
    else:
         print("[FAIL] Task extraction failed")

if __name__ == "__main__":
    test_wrapper()
