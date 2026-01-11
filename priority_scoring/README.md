# Priority Scoring Feature

Auto-prioritizes emails with a multi-signal scoring algorithm (0-100 score).

## Scoring Components

| Component | Max Points | Method |
|-----------|------------|--------|
| **Sender Authority** | 25 | User-defined VIP/manager/client lists + domain rules + AI-inferred from signatures/titles |
| **Deadline Urgency** | 25 | NLP date extraction ("by Friday", "ASAP", "due March 15") + urgency keywords |
| **Emotional Tone** | 20 | Gemini sentiment analysis (stress, anger, urgency, excitement) |
| **Historical Patterns** | 15 | Track avg response time & rate per sender |
| **Calendar Conflicts** | 15 | Detect meeting mentions & scheduling requests |

## Priority Levels

| Score Range | Label | Color | Badge |
|-------------|-------|-------|-------|
| 80-100 | Critical | Red | 🔴 |
| 60-79 | High | Orange | 🟠 |
| 40-59 | Medium | Yellow | 🟡 |
| 20-39 | Low | Green | 🟢 |
| 0-19 | Minimal | Gray | ⚪ |

## API Endpoints

- `POST /api/v1/emails/score` - Score a single email
- `POST /api/v1/emails/score/batch` - Score multiple emails
- `POST /api/v1/emails/score/explain` - Score with human-readable explanation
- `GET /api/v1/contacts` - List VIP/manager contacts
- `POST /api/v1/contacts` - Add contact with authority level

## Usage

```python
from priority_scoring import PriorityScorerService

scorer = PriorityScorerService()
score = scorer.score_email(email, db)
print(f"Priority: {score.score}/100 ({score.label})")
```
