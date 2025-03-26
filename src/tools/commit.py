"""Commit message."""

from pydantic import BaseModel

from src.resources.types import CommitType


class CommitMessage(BaseModel):
    """Commit message."""

    type: CommitType
    scope: str
    short_description: str
    description: str
    reason: str
