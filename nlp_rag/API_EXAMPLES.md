# API Examples & Response Formats

Complete examples of all NLP & RAG API endpoints with sample requests and responses.

## NLP Analysis Endpoints

### 1. Complete Email Analysis

**Endpoint:** `POST /api/v1/nlp/analyze`

**Request:**
```json
{
  "id": "email-123",
  "subject": "Urgent: Q4 Budget Review Meeting - Action Required",
  "body": "Hi Team,\n\nWe need to schedule an urgent meeting to review the Q4 budget. The deadline is this Friday, December 15th.\n\nKey points to discuss:\n1. Marketing spend is 20% over budget ($50,000 overage)\n2. Engineering needs additional $30,000 for AWS infrastructure\n3. Legal team requires approval for the new contract with Acme Corp\n\nPlease review the attached spreadsheet and come prepared with your recommendations.\n\nCan everyone make it Thursday at 2 PM? Let me know ASAP.\n\nThanks,\nJohn Smith\nVP of Finance",
  "sender_email": "john.smith@company.com",
  "sender_name": "John Smith",
  "date": "2024-01-15T10:00:00Z"
}
```

**Response:**
```json
{
  "email_id": "email-123",
  "summary": {
    "email_id": "email-123",
    "short_summary": "Urgent Q4 budget review meeting needed by Friday to discuss overages and approvals",
    "detailed_summary": "The team needs to meet urgently to review Q4 budget issues. Marketing is $50,000 over budget, Engineering needs $30,000 for AWS, and Legal needs contract approval for Acme Corp. Meeting proposed for Thursday at 2 PM.",
    "key_points": [
      "Urgent budget review meeting required",
      "Deadline: Friday, December 15th",
      "Marketing 20% over budget ($50,000)",
      "Engineering needs $30,000 for AWS",
      "Legal approval needed for Acme Corp contract"
    ],
    "action_items": [
      "Review attached spreadsheet",
      "Prepare recommendations",
      "Confirm availability for Thursday 2 PM meeting"
    ],
    "entities": [
      {
        "text": "December 15th",
        "type": "date",
        "confidence": 0.95
      },
      {
        "text": "$50,000",
        "type": "money",
        "confidence": 0.98
      },
      {
        "text": "$30,000",
        "type": "money",
        "confidence": 0.98
      },
      {
        "text": "Acme Corp",
        "type": "organization",
        "confidence": 0.85
      },
      {
        "text": "John Smith",
        "type": "person",
        "confidence": 0.90
      }
    ],
    "intent": "request",
    "confidence": 0.92
  },
  "sentiment": {
    "urgency": 85,
    "stress": 65,
    "anger": 10,
    "excitement": 15,
    "formality": 70,
    "overall_intensity": 44
  },
  "intent": "request",
  "entities": [...],
  "language": "en",
  "readability_score": 68.5,
  "word_count": 142,
  "analyzed_at": "2024-01-15T10:05:23.456Z"
}
```

### 2. Email Summarization

**Endpoint:** `POST /api/v1/nlp/summarize`

**Request:**
```json
{
  "id": "email-456",
  "subject": "Project Status Update",
  "body": "The project is progressing well. We've completed phase 1 and are moving into phase 2. Expected completion is next month.",
  "sender_email": "pm@company.com",
  "sender_name": "Project Manager",
  "date": "2024-01-15T14:00:00Z"
}
```

**Response:**
```json
{
  "email_id": "email-456",
  "short_summary": "Project progressing well, phase 1 complete, phase 2 starting, completion next month",
  "detailed_summary": "The project is making good progress with phase 1 completed. The team is now moving into phase 2 with an expected completion date of next month.",
  "key_points": [
    "Project progressing well",
    "Phase 1 completed",
    "Moving into phase 2",
    "Expected completion: next month"
  ],
  "action_items": [],
  "entities": [
    {
      "text": "next month",
      "type": "date",
      "confidence": 0.75
    }
  ],
  "intent": "information",
  "confidence": 0.88
}
```

### 3. Entity Extraction

**Endpoint:** `POST /api/v1/nlp/entities`

**Request:**
```json
{
  "id": "email-789",
  "subject": "Meeting with Microsoft on January 20th",
  "body": "We have a meeting scheduled with Microsoft representatives at their Seattle office on January 20th at 3 PM. The contract value is $250,000. Please contact Sarah Johnson for details.",
  "sender_email": "sales@company.com",
  "sender_name": "Sales Team",
  "date": "2024-01-15T09:00:00Z"
}
```

**Response:**
```json
{
  "email_id": "email-789",
  "entities": [
    {
      "text": "Microsoft",
      "type": "organization",
      "confidence": 0.95
    },
    {
      "text": "January 20th",
      "type": "date",
      "confidence": 0.98
    },
    {
      "text": "Seattle",
      "type": "location",
      "confidence": 0.90
    },
    {
      "text": "$250,000",
      "type": "money",
      "confidence": 0.99
    },
    {
      "text": "Sarah Johnson",
      "type": "person",
      "confidence": 0.92
    }
  ],
  "count": 5
}
```

### 4. Intent Detection

**Endpoint:** `POST /api/v1/nlp/intent`

**Request:**
```json
{
  "id": "email-101",
  "subject": "Can you help with this issue?",
  "body": "I'm having trouble with the login system. Can you help me figure out what's wrong?",
  "sender_email": "user@company.com",
  "sender_name": "User",
  "date": "2024-01-15T11:00:00Z"
}
```

**Response:**
```json
{
  "email_id": "email-101",
  "intent": "question",
  "subject": "Can you help with this issue?"
}
```

## RAG & Search Endpoints

### 5. Semantic Search

**Endpoint:** `POST /api/v1/rag/search`

**Request:**
```json
{
  "query": "budget approval and financial discussions",
  "limit": 5,
  "min_similarity": 0.7,
  "sender_filter": null,
  "date_from": null,
  "date_to": null
}
```

**Response:**
```json
{
  "query": "budget approval and financial discussions",
  "results": [
    {
      "email_id": "email-123",
      "subject": "Q4 Budget Review Meeting",
      "sender": "john.smith@company.com",
      "date": "2024-01-15T10:00:00Z",
      "snippet": "We need to schedule an urgent meeting to review the Q4 budget. Marketing spend is 20% over budget ($50,000 overage)...",
      "similarity_score": 0.92
    },
    {
      "email_id": "email-456",
      "subject": "Budget Approval Request",
      "sender": "finance@company.com",
      "date": "2024-01-10T14:30:00Z",
      "snippet": "Requesting approval for the additional $30,000 budget allocation for Q4 marketing initiatives...",
      "similarity_score": 0.88
    },
    {
      "email_id": "email-789",
      "subject": "Financial Planning Discussion",
      "sender": "cfo@company.com",
      "date": "2024-01-08T09:15:00Z",
      "snippet": "Let's discuss the financial planning for next quarter. We need to review our spending patterns...",
      "similarity_score": 0.75
    }
  ],
  "total_found": 3,
  "search_time_ms": 45.2
}
```

### 6. Company Memory (Question Answering)

**Endpoint:** `POST /api/v1/rag/ask`

**Request:**
```json
{
  "question": "What did legal say about the AWS contract?",
  "limit": 5
}
```

**Response:**
```json
{
  "question": "What did legal say about the AWS contract?",
  "answer": "According to the email from the legal team on January 10th, they have completed the review of the AWS contract and approve the terms with minor modifications to the SLA section. The contract value is $120,000 annually. They mentioned that the modifications are necessary to ensure better service guarantees.",
  "sources": [
    {
      "email_id": "email-001",
      "subject": "AWS Contract Approval - Legal Review Complete",
      "sender": "legal@company.com",
      "date": "2024-01-10T10:00:00Z",
      "snippet": "The legal team has completed the review of the AWS contract. We approve the terms with minor modifications to the SLA section. The contract value is $120,000 annually...",
      "similarity_score": 0.94
    },
    {
      "email_id": "email-002",
      "subject": "Re: AWS Contract Questions",
      "sender": "legal@company.com",
      "date": "2024-01-08T15:30:00Z",
      "snippet": "Regarding your questions about the AWS contract, we need to review the SLA terms more carefully...",
      "similarity_score": 0.82
    }
  ],
  "confidence": 0.89
}
```

### 7. Index Email

**Endpoint:** `POST /api/v1/rag/index`

**Request:**
```json
{
  "id": "email-new-001",
  "subject": "New Product Launch Discussion",
  "body": "We're planning to launch the new product next quarter. Marketing team is preparing the campaign.",
  "sender_email": "product@company.com",
  "sender_name": "Product Team",
  "date": "2024-01-15T16:00:00Z"
}
```

**Response:**
```json
{
  "status": "indexed",
  "email_id": "email-new-001",
  "message": "Email added to search index"
}
```

### 8. Batch Index

**Endpoint:** `POST /api/v1/rag/index/batch`

**Request:**
```json
[
  {
    "id": "email-batch-001",
    "subject": "Email 1",
    "body": "Content 1",
    "sender_email": "user1@company.com",
    "sender_name": "User 1",
    "date": "2024-01-15T10:00:00Z"
  },
  {
    "id": "email-batch-002",
    "subject": "Email 2",
    "body": "Content 2",
    "sender_email": "user2@company.com",
    "sender_name": "User 2",
    "date": "2024-01-15T11:00:00Z"
  }
]
```

**Response:**
```json
{
  "status": "indexed",
  "count": 2,
  "message": "Successfully indexed 2 emails"
}
```

### 9. Delete from Index

**Endpoint:** `DELETE /api/v1/rag/index/email-123`

**Response:**
```json
{
  "status": "deleted",
  "email_id": "email-123",
  "message": "Email removed from search index"
}
```

### 10. RAG Statistics

**Endpoint:** `GET /api/v1/rag/stats`

**Response:**
```json
{
  "total_emails": 1247,
  "backend": "chromadb",
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_dim": 384
}
```

## Burnout Detection Endpoints

### 11. Full Burnout Analysis

**Endpoint:** `POST /api/v1/burnout/analyze`

**Request:**
```json
{
  "user_email": "user@company.com",
  "emails": [
    {
      "id": "email-1",
      "subject": "Working late",
      "body": "Finishing this urgent task. Very stressed.",
      "date": "2024-01-15T23:30:00Z",
      "sender": "user@company.com",
      "is_sent": true
    },
    {
      "id": "email-2",
      "subject": "Weekend work",
      "body": "Catching up on emails",
      "date": "2024-01-13T14:00:00Z",
      "sender": "user@company.com",
      "is_sent": true
    }
    // ... more emails
  ],
  "period_days": 30
}
```

**Response:**
```json
{
  "user_email": "user@company.com",
  "period_start": "2023-12-16T00:00:00Z",
  "period_end": "2024-01-15T23:59:59Z",
  "total_emails_sent": 245,
  "total_emails_received": 312,
  "late_night_count": 18,
  "weekend_count": 12,
  "avg_response_time_hours": 6.5,
  "avg_sentiment_score": -0.15,
  "stress_level": 68.5,
  "negative_email_ratio": 0.32,
  "daily_email_avg": 18.6,
  "peak_day_count": 45,
  "signals": [
    "late_night_emails",
    "weekend_work",
    "stress_language"
  ],
  "risk_score": 62.3,
  "risk_level": "high",
  "recommendations": [
    "Consider setting email boundaries: avoid sending emails after 9 PM",
    "Try to disconnect on weekends to recharge and prevent burnout",
    "High stress detected in communications. Consider stress management techniques or seeking support",
    "High burnout risk detected. Take proactive steps to manage workload and stress"
  ]
}
```

### 12. Quick Burnout Check

**Endpoint:** `POST /api/v1/burnout/quick-check`

**Request:** (Same as full analysis)

**Response:**
```json
{
  "user_email": "user@company.com",
  "risk_level": "high",
  "risk_score": 62.3,
  "signals_detected": 3,
  "top_recommendation": "Consider setting email boundaries: avoid sending emails after 9 PM",
  "period_days": 30
}
```

### 13. Burnout Info

**Endpoint:** `GET /api/v1/burnout/info`

**Response:**
```json
{
  "feature": "Burnout Detection",
  "description": "AI-powered early detection of burnout signals from email patterns",
  "signals_detected": [
    {
      "name": "Late Night Emails",
      "description": "Emails sent after 10 PM or before 6 AM",
      "threshold": "More than 5 in analysis period"
    },
    {
      "name": "Weekend Work",
      "description": "Emails sent on Saturdays or Sundays",
      "threshold": "More than 3 in analysis period"
    },
    {
      "name": "High Volume",
      "description": "Excessive number of emails per day",
      "threshold": "More than 50 emails per day average"
    },
    {
      "name": "Negative Sentiment",
      "description": "Consistently negative tone in communications",
      "threshold": "Average sentiment below -0.3"
    },
    {
      "name": "Stress Language",
      "description": "High stress indicators in email content",
      "threshold": "Average stress level above 60/100"
    },
    {
      "name": "Response Delay",
      "description": "Increasing response times (may indicate overwhelm)",
      "threshold": "Average response time over 48 hours"
    }
  ],
  "risk_levels": {
    "low": "0-24: Healthy email patterns",
    "moderate": "25-49: Some signals present, monitor",
    "high": "50-74: Multiple signals, take action",
    "critical": "75-100: Urgent attention needed"
  },
  "privacy_note": "All analysis is private and designed for early help, not surveillance"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid email format: missing required field 'subject'"
}
```

### 404 Not Found
```json
{
  "detail": "Email not found in index: email-999"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Analysis failed: Gemini API error - rate limit exceeded"
}
```

## Response Time Benchmarks

| Endpoint | Typical Response Time | Notes |
|----------|----------------------|-------|
| `/nlp/analyze` | 1-2s | With Gemini AI |
| `/nlp/analyze` | 50-100ms | Without Gemini (fallback) |
| `/nlp/summarize` | 1-2s | With Gemini AI |
| `/nlp/entities` | 10-50ms | Rule-based extraction |
| `/nlp/intent` | 5-20ms | Pattern matching |
| `/rag/search` | 50-100ms | For 10k indexed emails |
| `/rag/ask` | 2-3s | Includes search + AI generation |
| `/rag/index` | 50-100ms | Single email |
| `/rag/index/batch` | 2-5s | 100 emails |
| `/burnout/analyze` | 2-5s | 1000 emails, with sentiment |
| `/burnout/quick-check` | 1-2s | Simplified analysis |

## Usage Tips

### 1. Batch Operations
For better performance, use batch endpoints:
```javascript
// Good: Batch indexing
await indexEmailsBatch(emails);

// Avoid: Individual indexing in loop
for (const email of emails) {
  await indexEmail(email);  // Slow!
}
```

### 2. Similarity Threshold
Adjust based on your needs:
- `0.9+`: Very strict, only near-exact matches
- `0.7-0.9`: Good balance (recommended)
- `0.5-0.7`: More results, less precise
- `<0.5`: Too loose, many false positives

### 3. Error Handling
Always handle fallback responses:
```javascript
const analysis = await analyzeEmail(email);
if (analysis.confidence < 0.5) {
  // Low confidence, show warning
  console.warn('Analysis may be inaccurate');
}
```

### 4. Caching
Cache frequent queries:
```javascript
const cache = new Map();
const cacheKey = `search:${query}`;

if (cache.has(cacheKey)) {
  return cache.get(cacheKey);
}

const results = await searchEmails({ query });
cache.set(cacheKey, results);
return results;
```

## Testing with cURL

### Quick Test Script
```bash
#!/bin/bash
API_URL="http://localhost:8000"

# Test NLP Analysis
echo "Testing NLP Analysis..."
curl -X POST "$API_URL/api/v1/nlp/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-1",
    "subject": "Test Email",
    "body": "This is a test email for the API",
    "sender_email": "test@example.com",
    "sender_name": "Test User",
    "date": "2024-01-15T10:00:00Z"
  }'

# Test Search
echo "\nTesting Search..."
curl -X POST "$API_URL/api/v1/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test email",
    "limit": 5
  }'

# Test Stats
echo "\nTesting Stats..."
curl -X GET "$API_URL/api/v1/rag/stats"
```

**Team Cipher | AlgosQuest 2025** 🚀
