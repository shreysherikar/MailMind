# Email Priority Scoring & Smart Task Extraction

A standalone Python microservice that auto-prioritizes emails and extracts actionable tasks using NLP and Google Gemini AI.

## Features

### 1. Priority Scoring (0-100)
Multi-signal scoring algorithm analyzing:
- **Sender Authority** (25 pts): VIP, manager, client, recruiter detection
- **Deadline Urgency** (25 pts): NLP-based deadline and urgency extraction
- **Emotional Tone** (20 pts): Sentiment analysis (stress, anger, urgency)
- **Historical Patterns** (15 pts): Response time and rate tracking
- **Calendar Conflicts** (15 pts): Meeting and scheduling detection

### 2. Smart Task Extraction
- NLP-powered task detection from email body
- Auto-generated TODO list linked to source emails
- Due date extraction when mentioned
- Task priority inherited from email priority
- Auto-archive flag when all tasks from email complete

## Priority Levels

| Score | Level | Color | Badge |
|-------|-------|-------|-------|
| 80-100 | Critical | Red | 🔴 |
| 60-79 | High | Orange | 🟠 |
| 40-59 | Medium | Yellow | 🟡 |
| 20-39 | Low | Green | 🟢 |
| 0-19 | Minimal | Gray | ⚪ |

## Quick Start

### 1. Install Dependencies

```bash
cd priority_scoring
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your Gemini API key
# Get one from: https://aistudio.google.com/app/apikey
```

### 3. Run the Server

```bash
python main.py
# or
uvicorn main:app --reload --port 8000
```

### 4. Access the API

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## API Endpoints

### Priority Scoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/emails/score` | Score single email |
| POST | `/api/v1/emails/score/batch` | Score multiple emails |
| POST | `/api/v1/emails/score/explain` | Score with explanation |

### Task Extraction
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tasks/extract` | Extract tasks from email |
| GET | `/api/v1/tasks` | List all tasks |
| PATCH | `/api/v1/tasks/{id}/complete` | Complete task |

### Contacts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/contacts` | List contacts |
| POST | `/api/v1/contacts` | Add VIP/manager contact |

## Example Usage

### Score an Email

```bash
curl -X POST http://localhost:8000/api/v1/emails/score \
  -H "Content-Type: application/json" \
  -d '{
    "email": {
      "sender_email": "ceo@company.com",
      "sender_name": "John CEO",
      "subject": "URGENT: Review needed by tomorrow",
      "body": "Please review the Q4 budget proposal ASAP. Meeting tomorrow at 10 AM."
    }
  }'
```

### Response

```json
{
  "email_id": "abc123",
  "score": 78,
  "color": "orange",
  "label": "high",
  "badge": "🟠",
  "breakdown": {
    "sender_authority": {"score": 22, "max": 25, "reason": "VIP detected via title: CEO"},
    "deadline_urgency": {"score": 20, "max": 25, "reason": "Due TOMORROW"},
    "emotional_tone": {"score": 14, "max": 20, "reason": "Tone: high urgency"},
    "historical_pattern": {"score": 7, "max": 15, "reason": "New sender"},
    "calendar_conflict": {"score": 15, "max": 15, "reason": "Meeting mention"}
  },
  "confidence": 0.82
}
```

### Extract Tasks

```bash
curl -X POST http://localhost:8000/api/v1/tasks/extract \
  -H "Content-Type: application/json" \
  -d '{
    "email": {
      "sender_email": "manager@company.com",
      "subject": "Action items from meeting",
      "body": "Please complete the following by Friday: 1. Review the proposal 2. Send feedback to the team"
    }
  }'
```

## Integration with Node.js/React

Your teammates can call this API from their Node.js backend:

```javascript
// Node.js example
const response = await fetch('http://localhost:8000/api/v1/emails/score', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: {
      sender_email: emailData.from,
      subject: emailData.subject,
      body: emailData.body
    }
  })
});

const priorityScore = await response.json();
console.log(`Priority: ${priorityScore.score} (${priorityScore.label})`);
```

## Running Tests

```bash
cd priority_scoring
pytest tests/ -v
```

## Project Structure

```
priority_scoring/
├── main.py                 # FastAPI entry point
├── config.py               # Configuration
├── requirements.txt        # Dependencies
├── models/
│   ├── schemas.py          # Pydantic models
│   └── database.py         # SQLite models
├── services/
│   ├── scorer.py           # Main scoring orchestrator
│   ├── task_extractor.py   # Task extraction
│   ├── authority.py        # Sender authority detection
│   ├── deadline.py         # Deadline extraction
│   ├── tone.py             # Tone analysis
│   ├── history.py          # Historical patterns
│   ├── calendar.py         # Calendar detection
│   └── gemini_client.py    # Gemini API wrapper
├── api/
│   ├── routes_scoring.py   # Scoring endpoints
│   ├── routes_tasks.py     # Task endpoints
│   └── routes_contacts.py  # Contact endpoints
├── data/
│   └── sample_emails.json  # Demo data
└── tests/
    └── test_scorer.py      # Unit tests
```

## Notes

- Works without Gemini API key (uses rule-based fallback)
- SQLite database created automatically on first run
- CORS enabled for frontend integration
- Designed for hackathon demo but production-ready patterns
