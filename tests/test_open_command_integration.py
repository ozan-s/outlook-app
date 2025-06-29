"""Integration tests for open command end-to-end flow."""

import subprocess
from pathlib import Path


class TestOpenCommandIntegration:
    """Integration tests for the complete open command workflow."""
    
    def test_open_command_end_to_end_with_existing_email(self):
        """Test complete open command flow with existing email ID."""
        # Run the actual CLI command using uv run
        result = subprocess.run([
            "uv", "run", "outlook-cli", "open", "inbox-001"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Should succeed (return code 0)
        assert result.returncode == 0, f"Command failed with error: {result.stderr}"
        
        # Verify output contains expected email content
        output = result.stdout
        assert "Email ID: inbox-001" in output
        assert "Weekly Team Meeting" in output
        assert "Alice Manager" in output
        assert "manager@company.com" in output
        assert "CONTENT:" in output
        assert "Hi team, our weekly meeting" in output
        assert "="*50 in output
    
    def test_open_command_end_to_end_with_sent_email(self):
        """Test complete open command flow with sent email ID."""
        # Run the actual CLI command using uv run
        result = subprocess.run([
            "uv", "run", "outlook-cli", "open", "sent-001"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Should succeed (return code 0)
        assert result.returncode == 0, f"Command failed with error: {result.stderr}"
        
        # Verify output contains expected email content
        output = result.stdout
        assert "Email ID: sent-001" in output
        assert "Re: Project Update Required" in output
        assert "Current User" in output
        assert "user@company.com" in output
        assert "Sent Items" in output
        assert "The project is on track" in output
    
    def test_open_command_end_to_end_with_draft_email(self):
        """Test complete open command flow with draft email ID."""
        # Run the actual CLI command using uv run
        result = subprocess.run([
            "uv", "run", "outlook-cli", "open", "draft-001"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Should succeed (return code 0)
        assert result.returncode == 0, f"Command failed with error: {result.stderr}"
        
        # Verify output contains expected email content
        output = result.stdout
        assert "Email ID: draft-001" in output
        assert "Vacation Request" in output
        assert "Drafts" in output
        assert "I would like to request vacation" in output
        assert "[UNREAD]" in output  # Drafts are typically unread
    
    def test_open_command_end_to_end_with_nonexistent_email(self):
        """Test complete open command flow with non-existent email ID."""
        # Run the actual CLI command using uv run
        result = subprocess.run([
            "uv", "run", "outlook-cli", "open", "nonexistent-999"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Should succeed (CLI handles error gracefully)
        assert result.returncode == 0, f"Command failed with error: {result.stderr}"
        
        # Verify error message is user-friendly
        output = result.stdout
        assert "Error: Email 'nonexistent-999' not found" in output
    
    def test_open_command_displays_all_email_headers(self):
        """Test that open command displays all email headers correctly."""
        # Use inbox-002 which has attachments and CC recipients
        result = subprocess.run([
            "uv", "run", "outlook-cli", "open", "inbox-002"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        assert result.returncode == 0, f"Command failed with error: {result.stderr}"
        
        output = result.stdout
        # Verify all headers are displayed
        assert "Subject: Project Update Required" in output
        assert "From: Bob ProjectManager <pm@company.com>" in output
        assert "To: user@company.com, team@company.com" in output
        assert "Date:" in output
        assert "Importance:" in output
        assert "📎 Attachments: 2" in output
        assert "Folder: Inbox" in output
        assert "[READ]" in output  # This email is marked as read