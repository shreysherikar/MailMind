# Follow-up Management Feature

AI-powered tracking of sent emails awaiting replies. Automatically detects when emails expect responses and tracks them until replies are received.

## Features

- **AI-Powered Detection**: Analyzes sent emails to detect if they expect a reply
- **Smart Reply Matching**: Matches incoming emails to pending follow-ups
- **Status Tracking**: Tracks follow-up status (waiting, overdue, replied)
- **Overdue Alerts**: Automatically marks follow-ups as overdue after configurable days

## Detection Signals

The AI looks for:
- Direct questions (?)
- Request patterns ("please let me know", "could you please", etc.)
- Action assignments ("please review", "your feedback needed", etc.)
- Urgency indicators ("ASAP", "urgent", "by tomorrow")

## Status Flow

```
[SENT EMAIL] → detect → [WAITING] → time passes → [OVERDUE]
                                    ↓
                              reply received
                                    ↓
                               [REPLIED]
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/followups/detect` | Analyze a sent email for follow-up potential |
| POST | `/api/v1/followups/detect/batch` | Batch detection for multiple emails |
| GET | `/api/v1/followups` | List all follow-ups (filterable by status) |
| GET | `/api/v1/followups/waiting` | Get emails awaiting reply |
| GET | `/api/v1/followups/overdue` | Get overdue follow-ups |
| GET | `/api/v1/followups/stats` | Get follow-up statistics |
| GET | `/api/v1/followups/{id}` | Get a single follow-up |
| PATCH | `/api/v1/followups/{id}` | Update follow-up status |
| PATCH | `/api/v1/followups/{id}/replied` | Mark as replied |
| DELETE | `/api/v1/followups/{id}` | Delete a follow-up |
| POST | `/api/v1/followups/check-reply` | Check if incoming email is a reply |
| POST | `/api/v1/followups/find-matches` | Find potential matches for an email |

## Usage Example

```python
from followup_management import FollowUpDetectorService

detector = FollowUpDetectorService()

# Detect if a sent email expects a reply
result = detector.detect_followup(email, db=db)

if result.should_track:
    print(f"Tracking: {result.followup.subject}")
    print(f"Confidence: {result.intent.confidence:.0%}")
    print(f"Reasons: {result.intent.reasons}")
```

## Reply Matching

When a new email arrives, check if it's a reply:

```python
from followup_management import ReplyMatcherService

matcher = ReplyMatcherService()

# Check if incoming email is a reply
result = matcher.check_if_reply(incoming_email, db=db)

if result.is_reply:
    print(f"Reply to: {result.matched_subject}")
    # Follow-up status automatically updated to 'replied'
```

## Configuration

Default settings (can be customized):
- Overdue threshold: 3 days
- Minimum confidence for tracking: 50%
- Maximum suggestions: 5 reasons per detection
