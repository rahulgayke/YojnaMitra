"""Import all ORM models once so metadata and relationships are registered."""

from yojanamitra.models.chunk import Chunk
from yojanamitra.models.document import Document
from yojanamitra.models.eligibility_rule import EligibilityRule
from yojanamitra.models.scheme import Scheme
from yojanamitra.models.source import Source
from yojanamitra.models.user_profile import UserProfile

__all__ = ["Scheme", "Source", "EligibilityRule", "Document", "Chunk", "UserProfile"]
