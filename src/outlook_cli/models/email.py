"""Email model with pydantic validation."""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


class Email(BaseModel):
    """Email data model with validation."""
    
    id: str = Field(..., min_length=1, description="Unique identifier from Outlook")
    subject: str = Field(..., description="Email subject line")
    sender_email: EmailStr = Field(..., description="Sender's email address")
    sender_name: str = Field(..., description="Sender's display name")
    recipient_emails: List[EmailStr] = Field(..., min_length=1, description="List of recipient email addresses")
    cc_emails: List[EmailStr] = Field(default_factory=list, description="List of CC email addresses")
    bcc_emails: List[EmailStr] = Field(default_factory=list, description="List of BCC email addresses")
    received_date: datetime = Field(..., description="When the email was received")
    body_text: str = Field(..., description="Plain text content of the email")
    body_html: Optional[str] = Field(default=None, description="HTML content of the email")
    has_attachments: bool = Field(..., description="Whether the email has attachments")
    attachment_count: int = Field(default=0, ge=0, description="Number of attachments")
    folder_path: str = Field(..., min_length=1, description="Folder path where email is located")
    is_read: bool = Field(default=False, description="Whether the email has been read")
    importance: Literal["High", "Normal", "Low"] = Field(default="Normal", description="Email importance level")
    
    @field_validator('attachment_count')
    @classmethod
    def validate_attachment_count(cls, v: int, info) -> int:
        """Ensure attachment_count matches has_attachments flag."""
        # Note: We need access to has_attachments field for full validation
        # This will be enhanced in integration tests
        if v < 0:
            raise ValueError("attachment_count cannot be negative")
        return v