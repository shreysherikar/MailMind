# Quick Start: NLP & RAG Features

## ✅ Installation Checklist

### Step 1: Install Dependencies (2 minutes)

```bash
pip install -r requirements.txt
```

This installs:
- ✅ sentence-transformers (embeddings)
- ✅ chromadb (vector database)
- ✅ numpy (vector operations)

### Step 2: Test the Features (1 minute)

```bash
python nlp_rag/demo.py
```

You should see:
- ✅ NLP analysis of a sample email
- ✅ Semantic search demo
- ✅ Burnout detection example

### Step 3: Start the API (30 seconds)

```bash
python main.py
```

Visit: http://localhost:8000/docs

You should see new endpoints:
- ✅ `/api/v1/nlp/*` - NLP analysis
- ✅ `/api/v1/rag/*` - Semantic search
- ✅ `/api/v1/burnout/*` - Burnout detection

## 🚀 Quick Test

### Test 1: Analyze an Email

```bash
curl -X POST "http://localhost:8000/api/v1/nlp/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-1",
    "subject": "Urgent: Budget Review Meeting",
    "body": "We need to review the Q4 budget by Friday. Please prepare your reports.",
    "sender_email": "boss@company.com",
    "sender_name": "Boss",
    "date": "2024-01-15T10:00:00Z"
  }'
```

Expected: Summary with key points and action items

### Test 2: Semantic Search

First, index an email:
```bash
curl -X POST "http://localhost:8000/api/v1/rag/index" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "email-1",
    "subject": "AWS Contract Approved",
    "body": "Legal has approved the AWS contract for $120,000",
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
    "limit": 5
  }'
```

Expected: Search results with similarity scores

### Test 3: Ask a Question

```bash
curl -X POST "http://localhost:8000/api/v1/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What did legal say about the AWS contract?"
  }'
```

Expected: AI-generated answer with sources

## 📊 What You Can Do Now

### 1. Email Analysis
- Summarize emails automatically
- Extract people, companies, dates, money
- Detect intent (request, question, complaint, etc.)
- Analyze sentiment and stress levels

### 2. Semantic Search
- Search by meaning: "emails about budget"
- Not just keywords: finds related content
- Filter by date, sender, similarity

### 3. Company Memory
- Ask questions: "What did John say about the deadline?"
- Get AI answers with source citations
- Search across all email history

### 4. Burnout Detection
- Analyze email patterns (late-night, weekend work)
- Track sentiment and stress over time
- Get risk score and recommendations

## 🎨 Frontend Integration

Use the provided client in your React app:

```javascript
import nlpRagClient from './api/nlp-rag-client';

// Example: Search emails
const results = await nlpRagClient.searchEmails({
  query: 'budget approval',
  limit: 10
});

// Example: Ask a question
const answer = await nlpRagClient.askQuestion(
  'What did legal say about the contract?'
);

// Example: Check burnout
const metrics = await nlpRagClient.analyzeBurnout(
  'user@company.com',
  emails,
  30
);
```

## 🐛 Troubleshooting

### "Module not found: sentence_transformers"
```bash
pip install sentence-transformers
```

### "Module not found: chromadb"
```bash
pip install chromadb
```

### Embedding model download is slow
The model (~80MB) downloads on first use. Be patient or pre-download:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### ChromaDB errors
The system automatically falls back to in-memory storage. No action needed.

### Gemini API not configured
All features work without Gemini API using fallback methods.

## 📚 Documentation

- **Detailed docs**: `nlp_rag/README.md`
- **Setup guide**: `NLP_RAG_SETUP.md`
- **Summary**: `NLP_RAG_SUMMARY.md`
- **API docs**: http://localhost:8000/docs

## 🎯 For Your Demo

### Show These Features:

1. **Email Summarization**
   - Pick a long email
   - Show AI-generated summary
   - Highlight key points and action items

2. **Semantic Search**
   - Search "budget discussions"
   - Show results with similarity scores
   - Compare to keyword search

3. **Company Memory**
   - Ask "What did legal say about the contract?"
   - Show AI answer with sources
   - Demonstrate understanding of context

4. **Burnout Detection**
   - Show sample email patterns
   - Display risk level and signals
   - Show recommendations

### Sample Data

Use the demo script to generate sample data:
```bash
python nlp_rag/demo.py
```

Or use the sample emails in `priority_scoring/data/sample_emails.json`

## ✨ Key Selling Points

1. **No Vendor Lock-in**: Works with or without external APIs
2. **Privacy-First**: All processing is local
3. **Production-Ready**: Error handling, fallbacks, scalable
4. **Easy to Use**: Simple API, clear documentation
5. **Extensible**: Easy to add new features

## 🚀 Next Steps

1. ✅ Install dependencies
2. ✅ Run demo script
3. ✅ Test API endpoints
4. ✅ Integrate with frontend
5. ✅ Prepare demo presentation

## 💡 Tips

- Start with small dataset (10-20 emails) for testing
- Use batch indexing for better performance
- Adjust similarity threshold based on your needs
- Monitor API response times
- Check logs for any errors

## 🎉 You're Ready!

All NLP and RAG features are now integrated and working. Good luck with your project!

**Team Cipher | AlgosQuest 2025** 🚀
