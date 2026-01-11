"""Quick test script to verify all imports work correctly."""

print("Testing imports...")

try:
    from config import settings
    print("✅ Config loaded")
    
    from models.schemas import Email, PriorityScore, Task
    print("✅ Schemas loaded")
    
    from models.database import Base, init_db
    print("✅ Database models loaded")
    
    from services.scorer import PriorityScorerService
    from services.task_extractor import TaskExtractorService
    print("✅ Services loaded")
    
    from api.routes_scoring import router as scoring_router
    from api.routes_tasks import router as tasks_router
    from api.routes_contacts import router as contacts_router
    print("✅ API routes loaded")
    
    # Test scoring an email
    scorer = PriorityScorerService()
    test_email = Email(
        sender_email="ceo@company.com",
        sender_name="John CEO",
        subject="URGENT: Review needed by tomorrow",
        body="Please review the Q4 budget proposal ASAP. Meeting tomorrow at 10 AM."
    )
    
    result = scorer.score_email(test_email)
    print(f"\n📧 Test Email Score: {result.score}/100 ({result.label}) {result.badge}")
    print(f"   Breakdown:")
    print(f"   - Sender Authority: {result.breakdown.sender_authority.score}/25")
    print(f"   - Deadline Urgency: {result.breakdown.deadline_urgency.score}/25")
    print(f"   - Emotional Tone: {result.breakdown.emotional_tone.score}/20")
    print(f"   - Historical Pattern: {result.breakdown.historical_pattern.score}/15")
    print(f"   - Calendar Conflict: {result.breakdown.calendar_conflict.score}/15")
    
    print("\n✅ All tests passed! The module is ready to use.")
    print("\nTo start the server, run:")
    print("  cd priority_scoring")
    print("  pip install -r requirements.txt")
    print("  python main.py")
    print("\nThen open http://localhost:8000/docs for the API documentation.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
