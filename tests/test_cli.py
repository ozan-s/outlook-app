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
            assert 'usage: outlook-cli' in help_output
            assert '{read,find,move,open}' in help_output


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
    with patch('sys.argv', ['outlook-cli', 'find', '--sender', 'john@example.com', '--subject', 'Meeting', '--folder', 'Work']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            assert 'sender=john@example.com' in output
            assert 'subject=Meeting' in output
            assert 'folder=Work' in output


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