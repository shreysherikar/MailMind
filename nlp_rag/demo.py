"""
Demo script for NLP & RAG features.

Run this to test the NLP and RAG functionality without starting the full API.
"""

from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp_rag.services.nlp_analyzer import get_nlp_analyzer
from nlp_rag.services.rag_service import get_rag_service
from nlp_rag.services.burnout_detector import get_burnout_detector
from nlp_rag.models.schemas import SearchQuery, CompanyMemoryQuery


def demo_nlp_analysis():
    """Demo NLP analysis features."""
    print("\n" + "="*60)
    print("📧 NLP ANALYSIS DEMO")
    print("="*60)
    
    analyzer = get_nlp_analyzer()
    
    # Sample email
    email_id = "demo-001"
    subject = "Urgent: Q4 Budget Review Meeting - Action Required"
    body = """Hi Team,

We need to schedule an urgent meeting to review the Q4 budget. The deadline is this Friday, December 15th.

Key points to discuss:
1. Marketing spend is 20% over budget ($50,000 overage)
2. Engineering needs additional $30,000 for AWS infrastructure
3. Legal team requires approval for the new contract with Acme Corp

Please review the attached spreadsheet and come prepared with your recommendations.

Can everyone make it Thursday at 2 PM? Let me know ASAP.

Thanks,
John Smith
VP of Finance
john.smith@company.com
"""
    
    print(f"\n📨 Analyzing email: '{subject}'\n")
    
    # Full analysis
    analysis = analyzer.analyze_email(email_id, subject, body)
    
    print("📝 SUMMARY:")
    print(f"  Short: {analysis.summary.short_summary}")
    print(f"  Detailed: {analysis.summary.detailed_summary}")
    
    print("\n🎯 KEY POINTS:")
    for i, point in enumerate(analysis.summary.key_points, 1):
        print(f"  {i}. {point}")
    
    print("\n✅ ACTION ITEMS:")
    for i, action in enumerate(analysis.summary.action_items, 1):
        print(f"  {i}. {action}")
    
    print("\n🏷️ ENTITIES FOUND:")
    for entity in analysis.entities[:5]:
        print(f"  - {entity.text} ({entity.type.value}) [confidence: {entity.confidence:.0%}]")
    
    print(f"\n🎭 INTENT: {analysis.intent.value}")
    
    print("\n😊 SENTIMENT:")
    print(f"  Urgency: {analysis.sentiment.get('urgency', 0)}/100")
    print(f"  Stress: {analysis.sentiment.get('stress', 0)}/100")
    print(f"  Formality: {analysis.sentiment.get('formality', 0)}/100")
    
    print(f"\n📖 READABILITY: {analysis.readability_score:.1f}/100")
    print(f"📊 WORD COUNT: {analysis.word_count}")


def demo_semantic_search():
    """Demo semantic search and RAG."""
    print("\n" + "="*60)
    print("🔍 SEMANTIC SEARCH & RAG DEMO")
    print("="*60)
    
    rag = get_rag_service()
    
    # Index some sample emails
    print("\n📥 Indexing sample emails...")
    
    sample_emails = [
        {
            "id": "email-001",
            "subject": "AWS Contract Approval - Legal Review Complete",
            "body": "The legal team has completed the review of the AWS contract. We approve the terms with minor modifications to the SLA section. The contract value is $120,000 annually.",
            "sender": "legal@company.com",
            "date": datetime.now() - timedelta(days=5)
        },
        {
            "id": "email-002",
            "subject": "Marketing Campaign Budget Increase Request",
            "body": "We're requesting an additional $50,000 for the Q4 marketing campaign. The ROI projections show a 3x return on this investment.",
            "sender": "marketing@company.com",
            "date": datetime.now() - timedelta(days=3)
        },
        {
            "id": "email-003",
            "subject": "Engineering Infrastructure Costs",
            "body": "Our AWS infrastructure costs have increased due to scaling. We need $30,000 additional budget for Q4 to maintain performance.",
            "sender": "engineering@company.com",
            "date": datetime.now() - timedelta(days=2)
        },
        {
            "id": "email-004",
            "subject": "Project Deadline Extension Approved",
            "body": "The project deadline has been extended to December 31st. This gives us two more weeks to complete testing.",
            "sender": "pm@company.com",
            "date": datetime.now() - timedelta(days=1)
        }
    ]
    
    rag.index_emails_batch(sample_emails)
    print(f"✅ Indexed {len(sample_emails)} emails")
    
    # Semantic search
    print("\n🔎 SEMANTIC SEARCH:")
    print("   Query: 'budget and costs'")
    
    query = SearchQuery(
        query="budget and costs",
        limit=3,
        min_similarity=0.5
    )
    
    results = rag.search_emails(query)
    print(f"\n   Found {results.total_found} results in {results.search_time_ms:.1f}ms:\n")
    
    for i, result in enumerate(results.results, 1):
        print(f"   {i}. {result.subject}")
        print(f"      From: {result.sender}")
        print(f"      Similarity: {result.similarity_score:.0%}")
        print(f"      Snippet: {result.snippet[:100]}...")
        print()
    
    # Company Memory (Question Answering)
    print("\n💭 COMPANY MEMORY (Question Answering):")
    print("   Question: 'What did legal say about the AWS contract?'")
    
    memory_query = CompanyMemoryQuery(
        question="What did legal say about the AWS contract?",
        limit=3
    )
    
    response = rag.answer_question(memory_query)
    print(f"\n   Answer (confidence: {response.confidence:.0%}):")
    print(f"   {response.answer}")
    print(f"\n   Based on {len(response.sources)} source email(s)")


def demo_burnout_detection():
    """Demo burnout detection."""
    print("\n" + "="*60)
    print("😌 BURNOUT DETECTION DEMO")
    print("="*60)
    
    detector = get_burnout_detector()
    
    # Sample email patterns showing burnout signals
    print("\n📊 Analyzing email patterns for: user@company.com")
    print("   Period: Last 30 days\n")
    
    sample_emails = []
    base_date = datetime.now() - timedelta(days=30)
    
    # Generate sample emails with burnout signals
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        
        # Regular work emails
        for hour in [9, 11, 14, 16]:
            sample_emails.append({
                "id": f"email-{day}-{hour}",
                "subject": "Work email",
                "body": "Regular work communication",
                "date": current_date.replace(hour=hour),
                "sender": "user@company.com",
                "is_sent": True
            })
        
        # Late night emails (burnout signal)
        if day % 3 == 0:
            sample_emails.append({
                "id": f"email-{day}-late",
                "subject": "Urgent: Need to finish this",
                "body": "Working late to meet the deadline. This is stressful.",
                "date": current_date.replace(hour=23),
                "sender": "user@company.com",
                "is_sent": True
            })
        
        # Weekend work (burnout signal)
        if current_date.weekday() >= 5:  # Saturday or Sunday
            sample_emails.append({
                "id": f"email-{day}-weekend",
                "subject": "Catching up on work",
                "body": "Working on the weekend to catch up",
                "date": current_date.replace(hour=14),
                "sender": "user@company.com",
                "is_sent": True
            })
    
    metrics = detector.analyze_user_patterns(
        user_email="user@company.com",
        emails=sample_emails,
        period_days=30
    )
    
    print(f"📈 RESULTS:")
    print(f"   Risk Level: {metrics.risk_level.upper()}")
    print(f"   Risk Score: {metrics.risk_score:.1f}/100")
    
    print(f"\n📧 EMAIL PATTERNS:")
    print(f"   Total Sent: {metrics.total_emails_sent}")
    print(f"   Daily Average: {metrics.daily_email_avg:.1f}")
    print(f"   Peak Day: {metrics.peak_day_count} emails")
    
    print(f"\n🌙 WORK HOURS:")
    print(f"   Late Night Emails: {metrics.late_night_count}")
    print(f"   Weekend Emails: {metrics.weekend_count}")
    
    print(f"\n😰 SENTIMENT:")
    print(f"   Average Sentiment: {metrics.avg_sentiment_score:.2f} (-1 to 1)")
    print(f"   Stress Level: {metrics.stress_level:.1f}/100")
    print(f"   Negative Email Ratio: {metrics.negative_email_ratio:.0%}")
    
    print(f"\n⚠️ SIGNALS DETECTED:")
    if metrics.signals:
        for signal in metrics.signals:
            print(f"   - {signal.value.replace('_', ' ').title()}")
    else:
        print("   None - healthy patterns!")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(metrics.recommendations, 1):
        print(f"   {i}. {rec}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("🚀 MAILMIND - NLP & RAG DEMO")
    print("   Team Cipher | AlgosQuest 2025")
    print("="*60)
    
    try:
        demo_nlp_analysis()
        demo_semantic_search()
        demo_burnout_detection()
        
        print("\n" + "="*60)
        print("✅ DEMO COMPLETE!")
        print("="*60)
        print("\nTo use these features in your app:")
        print("  1. Start the API: python main.py")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Try the /api/v1/nlp, /api/v1/rag, and /api/v1/burnout endpoints")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: Some features require dependencies:")
        print("  pip install sentence-transformers chromadb numpy")
        print("\nThe system will use fallback methods if dependencies are missing.")


if __name__ == "__main__":
    main()
