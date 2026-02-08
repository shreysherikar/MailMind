# NLP & RAG Setup Guide

Quick guide to get the NLP and RAG features running in MailMind.

## What Was Added

### 3 Major Features:

1. **Advanced NLP Analysis** 📧
   - Email summarization
   - Named entity extraction
   - Intent detection
   - Sentiment analysis

2. **Semantic Search & Company Memory** 🔍
   - Search emails by meaning, not keywords
   - Ask questions about email history
   - RAG-powered answers with sources

3. **Burnout Detection** 😌
   - Analyze email patterns
   - Detect late-night work, weekend emails
   - Track sentiment and stress levels
   - Get actionable recommendations

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `sentence-transformers` - For embeddings (semantic search)
- `chromadb` - Vector database
- `numpy` - Vector operations

### Step 2: Download Embedding Model (Optional)

The model (~80MB) downloads automatically on first use, but you can pre-download:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Step 3: Test the Features

Run the demo script:

```bash
python nlp_rag/demo.py
```

This will show you:
- NLP analysis of a sample email
- Semantic search in action
- Burnout detection example

## Quick Start

### Start the API

```bash
python main.py
```

The API will be available at: http://localhost:8000

### Try the Features

Visit the interactive docs: http://localhost:8000/docs

You'll see new endpoints:
- `/api/v1/nlp/*` - NLP analysis
- `/api/v1/rag/*` - Semantic search & company memory
- `/api/v1/burnout/*` - Burnout detection

## Usage Examples

### 1. Analyze an Email (NLP)

```bash
curl -X POST "http://localhost:8000/api/v1/nlp/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "123",
    "subject": "Urgent: Budget Review",
    "body": "We need to review the Q4 budget by Friday...",
    "sender_email": "john@company.com",
    "sender_name": "John Doe",
    "date": "2024-01-15T10:00:00Z"
  }'
```

Response includes:
- Summary (short + detailed)
- Key points
- Action items
- Entities (people, dates, money, etc.)
- Intent (request, question, etc.)
- Sentiment scores

### 2. Semantic Search

First, index some emails:

```bash
curl -X POST "http://localhost:8000/api/v1/rag/index" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "email-001",
    "subject": "AWS Contract Approval",
    "body": "Legal has approved the AWS contract...",
    "sender_email": "legal@company.com",
    "sender_name": "Legal Team",
    "date": "2024-01-10T10:00:00Z"
  }'
```

Then search:

```bash
curl -X POST "http://localhost:8000/api/v1/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "contract approval",
    "limit": 10,
    "min_similarity": 0.7
  }'
```

### 3. Ask Questions (Company Memory)

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What did legal say about the AWS contract?",
    "limit": 5
  }'
```

The AI will:
1. Search for relevant emails
2. Generate an answer based on the content
3. Cite source emails

### 4. Burnout Detection

```bash
curl -X POST "http://localhost:8000/api/v1/burnout/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "user@company.com",
    "emails": [
      {
        "id": "1",
        "subject": "Working late",
        "body": "Finishing this urgent task",
        "date": "2024-01-15T23:30:00Z",
        "sender": "user@company.com",
        "is_sent": true
      }
    ],
    "period_days": 30
  }'
```

Returns:
- Risk score (0-100)
- Risk level (low, moderate, high, critical)
- Signals detected (late-night emails, weekend work, etc.)
- Recommendations

## Integration with Frontend

### Add to Your React App

```javascript
// Search emails semantically
const searchEmails = async (query) => {
  const response = await fetch('http://localhost:8000/api/v1/rag/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query,
      limit: 10,
      min_similarity: 0.7
    })
  });
  return await response.json();
};

// Ask a question
const askQuestion = async (question) => {
  const response = await fetch('http://localhost:8000/api/v1/rag/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question: question,
      limit: 5
    })
  });
  return await response.json();
};

// Check burnout risk
const checkBurnout = async (userEmail, emails) => {
  const response = await fetch('http://localhost:8000/api/v1/burnout/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_email: userEmail,
      emails: emails,
      period_days: 30
    })
  });
  return await response.json();
};
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Required for AI features (you already have this)
GEMINI_API_KEY=your_api_key_here

# Optional: Custom embedding model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Optional: Vector store location
CHROMA_DB_PATH=./chroma_db
```

## Troubleshooting

### "Module not found" errors

Install dependencies:
```bash
pip install sentence-transformers chromadb numpy
```

### Embedding model download fails

Pre-download manually:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### ChromaDB errors

The system automatically falls back to in-memory storage. No action needed.

### Gemini API errors

All features have fallback methods that work without the API.

## Performance Tips

### For Large Email Volumes

1. **Batch indexing**: Use `/api/v1/rag/index/batch` instead of individual calls
2. **Limit search results**: Set appropriate `limit` in search queries
3. **Adjust similarity threshold**: Higher `min_similarity` = fewer but better results

### Memory Usage

- Each indexed email: ~1KB in memory
- Embedding model: ~80MB
- ChromaDB: Persists to disk automatically

## What's Next?

### Recommended Integration Steps:

1. **Add search bar** to your frontend
   - Use `/api/v1/rag/search` for semantic search
   - Show results with similarity scores

2. **Add "Ask MailMind" feature**
   - Use `/api/v1/rag/ask` for question answering
   - Display answer with source citations

3. **Add burnout dashboard**
   - Show risk level and signals
   - Display recommendations
   - Track trends over time

4. **Auto-index emails**
   - When new emails arrive, call `/api/v1/rag/index`
   - Run batch indexing for historical emails

5. **Add email summaries**
   - Show summary in email preview
   - Extract action items automatically

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     MailMind API                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │     NLP      │  │     RAG      │  │   Burnout    │ │
│  │   Analysis   │  │    Search    │  │  Detection   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                 │                  │         │
│         ▼                 ▼                  ▼         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Gemini AI  │  │  Embeddings  │  │   Pattern    │ │
│  │  (fallback)  │  │   (local)    │  │   Analysis   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                           │                            │
│                           ▼                            │
│                    ┌──────────────┐                    │
│                    │  ChromaDB    │                    │
│                    │ (persistent) │                    │
│                    └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

## Support

For questions or issues:
1. Check the detailed README: `nlp_rag/README.md`
2. Run the demo: `python nlp_rag/demo.py`
3. Check API docs: http://localhost:8000/docs

## Team Cipher | AlgosQuest 2025

Good luck with your project! 🚀
