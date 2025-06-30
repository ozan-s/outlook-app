"""Test CLI enhanced argument parser functionality."""
import pytest
import sys
from unittest.mock import patch
from outlook_cli.cli import main


class TestCLIEnhancedParser:
    """Test enhanced CLI argument parser with new flags."""
    
    def test_date_filters_parsing(self):
        """Test that --since and --until flags parse correctly."""
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--since', '2025-06-01', '--until', '2025-06-30']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                # Should get to handler with parsed args
                mock_handle.assert_called_once()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'since')
                assert hasattr(args, 'until')
                assert args.since == '2025-06-01'
                assert args.until == '2025-06-30'
    
    def test_since_flag_accepts_various_formats(self):
        """Test that --since accepts different date formats."""
        test_cases = [
            '2025-06-01',  # YYYY-MM-DD
            '7d',          # 7 days
            '2w',          # 2 weeks  
            'yesterday'    # relative
        ]
        
        for date_format in test_cases:
            with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--since', date_format]):
                with patch('outlook_cli.cli.handle_find') as mock_handle:
                    main()
                    args = mock_handle.call_args[0][0]
                    assert args.since == date_format
    
    def test_read_status_flags_parsing(self):
        """Test that --is-read and --is-unread flags parse correctly."""
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--is-read']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'is_read')
                assert args.is_read is True
                
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--is-unread']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'is_unread')
                assert args.is_unread is True
                
    def test_read_status_flags_mutually_exclusive(self):
        """Test that --is-read and --is-unread are mutually exclusive."""
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--is-read', '--is-unread']):
            with pytest.raises(SystemExit):  # Should exit due to mutually exclusive args
                main()
                
    def test_attachment_flags_parsing(self):
        """Test that attachment flags parse correctly."""
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--has-attachment']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'has_attachment')
                assert args.has_attachment is True
                
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--no-attachment']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'no_attachment')
                assert args.no_attachment is True
                
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--attachment-type', 'pdf']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'attachment_type')
                assert args.attachment_type == 'pdf'
                
    def test_attachment_flags_mutually_exclusive(self):
        """Test that --has-attachment and --no-attachment are mutually exclusive."""
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--has-attachment', '--no-attachment']):
            with pytest.raises(SystemExit):  # Should exit due to mutually exclusive args
                main()
                
    def test_content_filters_parsing(self):
        """Test that content filter flags parse correctly."""
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--importance', 'high']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'importance')
                assert args.importance == 'high'
                
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--folders', 'Inbox', 'Sent']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'folders')
                assert args.folders == ['Inbox', 'Sent']
                
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--not-sender', 'spam@example.com']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'not_sender')
                assert args.not_sender == 'spam@example.com'
                
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--not-subject', 'SPAM']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'not_subject')
                assert args.not_subject == 'SPAM'
                
    def test_result_control_flags_parsing(self):
        """Test that result control flags parse correctly."""
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--limit', '50']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'limit')
                assert args.limit == 50
                
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--all']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'all')
                assert args.all is True
                
    def test_result_control_flags_mutually_exclusive(self):
        """Test that --limit and --all are mutually exclusive."""
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--limit', '50', '--all']):
            with pytest.raises(SystemExit):  # Should exit due to mutually exclusive args
                main()
                
    def test_sorting_flags_parsing(self):
        """Test that sorting flags parse correctly."""
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--sort-by', 'received_date']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'sort_by')
                assert args.sort_by == 'received_date'
                
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--sort-order', 'asc']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert hasattr(args, 'sort_order')
                assert args.sort_order == 'asc'
                
        # Test all valid sort-by options
        sort_fields = ['received_date', 'subject', 'sender', 'importance']
        for field in sort_fields:
            with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'test', '--sort-by', field]):
                with patch('outlook_cli.cli.handle_find') as mock_handle:
                    main()
                    args = mock_handle.call_args[0][0]
                    assert args.sort_by == field
                    
    def test_folders_command_parsing(self):
        """Test that folders command and --tree flag parse correctly."""
        with patch.object(sys, 'argv', ['ocli', 'folders']):
            with patch('outlook_cli.cli.handle_folders') as mock_handle:
                main()
                mock_handle.assert_called_once()
                args = mock_handle.call_args[0][0]
                assert args.command == 'folders'
                assert hasattr(args, 'tree')
                assert args.tree is False  # Default value
                
        with patch.object(sys, 'argv', ['ocli', 'folders', '--tree']):
            with patch('outlook_cli.cli.handle_folders') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert args.command == 'folders'
                assert args.tree is True
                
    def test_integration_all_flags_together(self):
        """Integration test: verify multiple flags parse correctly together."""
        complex_command = [
            'ocli', 'find', 
            '--keyword', 'project',
            '--since', '2025-06-01',
            '--until', '2025-06-30', 
            '--is-unread',
            '--has-attachment',
            '--attachment-type', 'pdf',
            '--importance', 'high',
            '--folders', 'Inbox', 'Work',
            '--not-sender', 'spam@example.com',
            '--not-subject', 'URGENT',
            '--limit', '25',
            '--sort-by', 'received_date',
            '--sort-order', 'asc'
        ]
        
        with patch.object(sys, 'argv', complex_command):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                
                # Verify all arguments are parsed correctly
                assert args.keyword == 'project'
                assert args.since == '2025-06-01'
                assert args.until == '2025-06-30'
                assert args.is_unread is True
                assert args.has_attachment is True
                assert args.attachment_type == 'pdf'
                assert args.importance == 'high'
                assert args.folders == ['Inbox', 'Work']
                assert args.not_sender == 'spam@example.com'
                assert args.not_subject == 'URGENT'
                assert args.limit == 25
                assert args.sort_by == 'received_date'
                assert args.sort_order == 'asc'
                
    def test_backward_compatibility_existing_commands(self):
        """Test that existing commands still work with backward compatibility."""
        
        # Test existing read command
        with patch.object(sys, 'argv', ['ocli', 'read', '--folder', 'Inbox']):
            with patch('outlook_cli.cli.handle_read') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert args.command == 'read'
                assert args.folder == 'Inbox'
                
        # Test existing find command with keyword
        with patch.object(sys, 'argv', ['ocli', 'find', '--keyword', 'meeting']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert args.command == 'find'
                assert args.keyword == 'meeting'
                
        # Test existing find command with sender and subject
        with patch.object(sys, 'argv', ['ocli', 'find', '--sender', 'john@company.com', '--subject', 'project']):
            with patch('outlook_cli.cli.handle_find') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert args.sender == 'john@company.com'
                assert args.subject == 'project'
                
        # Test existing move command
        with patch.object(sys, 'argv', ['ocli', 'move', 'email123', 'Sent Items']):
            with patch('outlook_cli.cli.handle_move') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert args.command == 'move'
                assert args.email_id == 'email123'
                assert args.target_folder == 'Sent Items'
                
        # Test existing open command
        with patch.object(sys, 'argv', ['ocli', 'open', 'email456']):
            with patch('outlook_cli.cli.handle_open') as mock_handle:
                main()
                args = mock_handle.call_args[0][0]
                assert args.command == 'open'
                assert args.email_id == 'email456'