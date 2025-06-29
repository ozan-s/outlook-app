"""Tests for CLI module."""

import pytest
from io import StringIO
from unittest.mock import patch
from outlook_cli import cli


def test_cli_module_can_be_imported():
    """Test that cli module can be imported."""
    assert cli is not None


def test_cli_has_main_function():
    """Test that cli module has a main() function."""
    assert hasattr(cli, 'main')
    assert callable(cli.main)


def test_main_with_help_shows_available_commands():
    """Test that main() with --help shows available commands."""
    with patch('sys.argv', ['outlook-cli', '--help']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            
            # argparse exits with code 0 for help
            assert exc_info.value.code == 0
            
            help_output = mock_stdout.getvalue()
            assert 'read' in help_output
            assert 'find' in help_output
            assert 'move' in help_output
            assert 'open' in help_output


def test_read_command_help():
    """Test that 'read --help' shows read command options."""
    with patch('sys.argv', ['outlook-cli', 'read', '--help']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            
            assert exc_info.value.code == 0
            help_output = mock_stdout.getvalue()
            assert '--folder' in help_output


def test_find_command_help():
    """Test that 'find --help' shows find command options."""
    with patch('sys.argv', ['outlook-cli', 'find', '--help']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            
            assert exc_info.value.code == 0
            help_output = mock_stdout.getvalue()
            assert '--sender' in help_output
            assert '--subject' in help_output
            assert '--folder' in help_output


def test_move_command_help():
    """Test that 'move --help' shows move command usage."""
    with patch('sys.argv', ['outlook-cli', 'move', '--help']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            
            assert exc_info.value.code == 0
            help_output = mock_stdout.getvalue()
            assert 'email_id' in help_output
            assert 'target_folder' in help_output


def test_open_command_help():
    """Test that 'open --help' shows open command usage."""
    with patch('sys.argv', ['outlook-cli', 'open', '--help']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            
            assert exc_info.value.code == 0
            help_output = mock_stdout.getvalue()
            assert 'email_id' in help_output


def test_read_command_routing():
    """Test that read command is routed to read handler."""
    with patch('sys.argv', ['outlook-cli', 'read']):
        with patch('sys.stdout', new_callable=StringIO):
            with patch.object(cli, 'handle_read') as mock_handle:
                cli.main()
                mock_handle.assert_called_once()


def test_find_command_routing():
    """Test that find command is routed to find handler."""
    with patch('sys.argv', ['outlook-cli', 'find', '--sender', 'test@example.com']):
        with patch('sys.stdout', new_callable=StringIO):
            with patch.object(cli, 'handle_find') as mock_handle:
                cli.main()
                mock_handle.assert_called_once()


def test_move_command_routing():
    """Test that move command is routed to move handler."""
    with patch('sys.argv', ['outlook-cli', 'move', '123', 'Sent']):
        with patch('sys.stdout', new_callable=StringIO):
            with patch.object(cli, 'handle_move') as mock_handle:
                cli.main()
                mock_handle.assert_called_once()


def test_open_command_routing():
    """Test that open command is routed to open handler."""
    with patch('sys.argv', ['outlook-cli', 'open', '123']):
        with patch('sys.stdout', new_callable=StringIO):
            with patch.object(cli, 'handle_open') as mock_handle:
                cli.main()
                mock_handle.assert_called_once()


def test_no_command_shows_help():
    """Test that no command shows help message."""
    with patch('sys.argv', ['outlook-cli']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            help_output = mock_stdout.getvalue()
            assert 'usage: ocli' in help_output
            assert '{read,find,move,open,folders}' in help_output


def test_integration_read_with_folder():
    """Integration test: read command with folder option."""
    with patch('sys.argv', ['outlook-cli', 'read', '--folder', 'Sent Items']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            # Should show pagination info for Sent Items folder
            assert 'Page 1 of' in output
            assert 'showing' in output.lower()


def test_integration_find_with_multiple_filters():
    """Integration test: find command with multiple filters."""
    with patch('sys.argv', ['outlook-cli', 'find', '--sender', 'manager', '--subject', 'meeting', '--folder', 'Inbox']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            assert "Searching for emails with sender 'manager' and subject 'meeting'" in output
            assert "in folder 'Inbox'" in output


class TestReadCommandImplementation:
    """Tests for read command implementation with EmailReader integration."""
    
    def test_read_valid_folder_displays_emails_with_pagination(self):
        """Test read command displays emails from valid folder with pagination info."""
        with patch('sys.argv', ['outlook-cli', 'read', '--folder', 'Inbox']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show email list
                assert 'Subject:' in output or 'From:' in output
                # Should show pagination info
                assert 'Page 1' in output
                assert 'showing' in output.lower()
    
    def test_read_folder_with_spaces_handles_correctly(self):
        """Test read command handles folder names with spaces."""
        with patch('sys.argv', ['outlook-cli', 'read', '--folder', 'Sent Items']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should not show error about folder name
                assert 'error' not in output.lower()
                assert 'invalid' not in output.lower()
    
    def test_read_nonexistent_folder_shows_error(self):
        """Test read command shows helpful error for non-existent folder."""
        with patch('sys.argv', ['outlook-cli', 'read', '--folder', 'NonExistentFolder']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show user-friendly error
                assert 'error' in output.lower() or 'not found' in output.lower()
                assert 'NonExistentFolder' in output
    
    def test_read_large_folder_shows_only_first_page(self):
        """Test read command shows only first 10 emails with pagination info."""
        with patch('sys.argv', ['outlook-cli', 'read', '--folder', 'Inbox']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show pagination indicating more emails exist
                assert 'Page 1 of' in output or '1-10 of' in output
    
    def test_read_empty_folder_shows_no_emails_message(self):
        """Test read command shows helpful message for empty folder."""
        with patch('sys.argv', ['outlook-cli', 'read', '--folder', 'EmptyFolder']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show no emails message
                assert 'no emails' in output.lower() or 'empty' in output.lower()


class TestReadCommandIntegration:
    """Integration tests for read command with real services."""
    
    def test_end_to_end_read_inbox_with_mock_adapter(self):
        """Integration test: Complete read flow with MockOutlookAdapter."""
        with patch('sys.argv', ['outlook-cli', 'read', '--folder', 'Inbox']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show pagination (Inbox has 3 emails in mock data)
                assert 'Page 1 of 1' in output
                assert 'showing 1-3 of 3 emails' in output
                
                # Should show email details
                assert 'Subject:' in output
                assert 'From:' in output
                assert 'Date:' in output
                
                # Should show read/unread status
                assert '[READ]' in output or '[UNREAD]' in output
    
    def test_end_to_end_read_sent_items_folder(self):
        """Integration test: Read sent items folder."""
        with patch('sys.argv', ['outlook-cli', 'read', '--folder', 'Sent Items']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show pagination (Sent Items has 2 emails in mock data)
                assert 'Page 1 of 1' in output
                assert 'showing 1-2 of 2 emails' in output
    
    def test_end_to_end_read_drafts_folder(self):
        """Integration test: Read drafts folder."""
        with patch('sys.argv', ['outlook-cli', 'read', '--folder', 'Drafts']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show pagination (Drafts has 1 email in mock data)
                assert 'Page 1 of 1' in output
                assert 'showing 1-1 of 1 emails' in output


class TestFindCommandIntegration:
    """Integration tests for find command with EmailSearcher service."""
    
    def test_find_by_sender_only_displays_filtered_emails_with_pagination(self):
        """Test find command with --sender filters emails and shows with pagination."""
        with patch('sys.argv', ['outlook-cli', 'find', '--sender', 'manager']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show search criteria summary
                assert "Searching for emails with sender 'manager'" in output
                assert "in folder 'Inbox'" in output
                
                # Should show pagination info for results
                assert 'Page 1 of' in output
                assert 'showing' in output.lower()
                
                # Should show email details in same format as read
                assert 'Subject:' in output
                assert 'From:' in output
                assert 'Date:' in output
                
                # Should show read/unread status
                assert '[READ]' in output or '[UNREAD]' in output
    
    def test_find_by_subject_only_displays_filtered_emails_with_pagination(self):
        """Test find command with --subject filters emails and shows with pagination."""
        with patch('sys.argv', ['outlook-cli', 'find', '--subject', 'project']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show search criteria summary
                assert "Searching for emails with subject 'project'" in output
                assert "in folder 'Inbox'" in output
                
                # Should show pagination info for results
                assert 'Page 1 of' in output
                assert 'showing' in output.lower()
                
                # Should show email details
                assert 'Subject:' in output
                assert 'From:' in output
    
    def test_find_with_combined_sender_and_subject_shows_and_filtered_results(self):
        """Test find command with both --sender and --subject uses AND logic."""
        with patch('sys.argv', ['outlook-cli', 'find', '--sender', 'pm', '--subject', 'update']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show both criteria in summary
                assert "Searching for emails with sender 'pm' and subject 'update'" in output
                assert "in folder 'Inbox'" in output
                
                # Should show pagination info
                assert 'Page 1 of' in output
                assert 'showing' in output.lower()
    
    def test_find_with_folder_scoping_searches_specific_folder(self):
        """Test find command with --folder searches in specified folder."""
        with patch('sys.argv', ['outlook-cli', 'find', '--sender', 'user', '--folder', 'Sent Items']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show specified folder in summary
                assert "Searching for emails with sender 'user'" in output
                assert "in folder 'Sent Items'" in output
                
                # Should show results from Sent Items folder
                assert 'Page 1 of' in output
                assert 'showing' in output.lower()
    
    def test_find_with_no_results_shows_helpful_message(self):
        """Test find command with no matching emails shows clear message."""
        with patch('sys.argv', ['outlook-cli', 'find', '--sender', 'nonexistent@example.com']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show search criteria
                assert "Searching for emails with sender 'nonexistent@example.com'" in output
                
                # Should show no results message
                assert 'No emails found matching your criteria' in output
                
                # Should NOT show pagination info when no results
                assert 'Page' not in output
    
    def test_find_with_invalid_folder_shows_user_friendly_error(self):
        """Test find command with invalid folder shows helpful error message."""
        with patch('sys.argv', ['outlook-cli', 'find', '--sender', 'test', '--folder', 'NonExistentFolder']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show user-friendly error
                assert "Error: Folder 'NonExistentFolder' not found" in output
                
                # Should NOT show search results
                assert 'Subject:' not in output
                assert 'Page' not in output
    
    def test_find_with_no_criteria_shows_helpful_usage_message(self):
        """Test find command with no search criteria shows usage guidance."""
        with patch('sys.argv', ['outlook-cli', 'find']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show helpful usage message
                assert 'Error: Please specify --keyword, --sender, and/or --subject to search' in output
                
                # Should NOT show search results
                assert 'Searching for emails' not in output
                assert 'Subject:' not in output


class TestMoveCommandImplementation:
    """Tests for move command implementation with EmailMover integration."""
    
    def test_move_valid_email_to_valid_folder_shows_success_message(self):
        """Test move command with valid email ID and folder shows success."""
        with patch('sys.argv', ['outlook-cli', 'move', 'inbox-001', 'Drafts']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show success message
                assert 'Successfully moved email inbox-001 to Drafts' in output
                
                # Should NOT show error messages
                assert 'Error:' not in output
    
    def test_move_nonexistent_email_shows_user_friendly_error(self):
        """Test move command with nonexistent email ID shows helpful error."""
        with patch('sys.argv', ['outlook-cli', 'move', 'nonexistent', 'Drafts']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show user-friendly error from service
                assert "Error: Email 'nonexistent' not found" in output
                
                # Should NOT show success message
                assert 'Successfully moved' not in output
    
    def test_move_to_nonexistent_folder_shows_user_friendly_error(self):
        """Test move command with nonexistent folder shows helpful error."""
        with patch('sys.argv', ['outlook-cli', 'move', 'inbox-001', 'BadFolder']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show user-friendly error from service
                assert "Error: Target folder 'BadFolder' not found" in output
                
                # Should NOT show success message
                assert 'Successfully moved' not in output
    
    def test_move_with_folder_containing_spaces_works_correctly(self):
        """Test move command handles folder names with spaces."""
        with patch('sys.argv', ['outlook-cli', 'move', 'inbox-001', 'Custom/Archive']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show success message with folder name
                assert 'Successfully moved email inbox-001 to Custom/Archive' in output
                
                # Should NOT show error about folder name parsing
                assert 'Error:' not in output


class TestMoveCommandIntegration:
    """Integration tests for move command with EmailMover service."""
    
    def test_end_to_end_move_email_between_real_folders(self):
        """Integration test: Complete move flow with MockOutlookAdapter."""
        with patch('sys.argv', ['outlook-cli', 'move', 'inbox-002', 'Sent Items']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show successful move operation
                assert 'Successfully moved email inbox-002 to Sent Items' in output
                
                # Should use EmailMover service correctly
                assert 'Error:' not in output
    
    def test_end_to_end_move_to_custom_folder_works(self):
        """Integration test: Move email to custom folder path."""
        with patch('sys.argv', ['outlook-cli', 'move', 'sent-001', 'Custom/Projects']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should handle custom folder path correctly
                assert 'Successfully moved email sent-001 to Custom/Projects' in output
                assert 'Error:' not in output
    
    def test_end_to_end_move_with_service_layer_error_handling(self):
        """Integration test: Service layer errors convert to CLI-friendly messages."""
        with patch('sys.argv', ['outlook-cli', 'move', 'invalid-id', 'Drafts']):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                cli.main()
                output = mock_stdout.getvalue()
                
                # Should show ValueError from EmailMover as user-friendly error
                assert "Error: Email 'invalid-id' not found" in output
                assert 'Successfully moved' not in output