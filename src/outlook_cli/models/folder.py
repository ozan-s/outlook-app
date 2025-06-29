"""Folder model with pydantic validation."""

from pydantic import BaseModel, Field, field_validator


class Folder(BaseModel):
    """Folder data model with validation."""
    
    path: str = Field(..., min_length=1, description="Folder path (e.g., 'Inbox', 'Inbox/Subfolder')")
    name: str = Field(..., min_length=1, description="Display name of the folder")
    email_count: int = Field(..., ge=0, description="Total number of emails in folder")
    unread_count: int = Field(..., ge=0, description="Number of unread emails in folder")
    
    @field_validator('unread_count')
    @classmethod
    def validate_unread_count(cls, v: int, info) -> int:
        """Ensure unread_count doesn't exceed email_count."""
        # Get email_count from the data being validated
        if hasattr(info, 'data') and info.data and 'email_count' in info.data:
            email_count = info.data['email_count']
            if v > email_count:
                raise ValueError(f"unread_count ({v}) cannot be greater than email_count ({email_count})")
        return v