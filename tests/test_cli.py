"""Tests for CLI module."""

import pytest
import sys
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
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch.object(cli, 'handle_read') as mock_handle:
                cli.main()
                mock_handle.assert_called_once()


def test_find_command_routing():
    """Test that find command is routed to find handler."""
    with patch('sys.argv', ['outlook-cli', 'find', '--sender', 'test@example.com']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch.object(cli, 'handle_find') as mock_handle:
                cli.main()
                mock_handle.assert_called_once()


def test_move_command_routing():
    """Test that move command is routed to move handler."""
    with patch('sys.argv', ['outlook-cli', 'move', '123', 'Sent']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch.object(cli, 'handle_move') as mock_handle:
                cli.main()
                mock_handle.assert_called_once()


def test_open_command_routing():
    """Test that open command is routed to open handler."""
    with patch('sys.argv', ['outlook-cli', 'open', '123']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
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
    with patch('sys.argv', ['outlook-cli', 'read', '--folder', 'Sent']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            assert 'Reading emails from folder: Sent' in output


def test_integration_find_with_multiple_filters():
    """Integration test: find command with multiple filters."""
    with patch('sys.argv', ['outlook-cli', 'find', '--sender', 'john@example.com', '--subject', 'Meeting', '--folder', 'Work']):
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cli.main()
            output = mock_stdout.getvalue()
            assert 'sender=john@example.com' in output
            assert 'subject=Meeting' in output
            assert 'folder=Work' in output