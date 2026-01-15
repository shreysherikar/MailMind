"""Follow-up Management Feature.

AI-powered tracking of sent emails awaiting replies.
"""

from followup_management.services.followup_detector import FollowUpDetectorService
from followup_management.services.reply_matcher import ReplyMatcherService

__all__ = ["FollowUpDetectorService", "ReplyMatcherService"]
