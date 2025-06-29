"""Tests for FolderService class."""

from outlook_cli.models.folder import Folder
from outlook_cli.services.folder_service import FolderService
from outlook_cli.config.adapter_factory import AdapterFactory


class TestFolderService:
    """Test FolderService functionality."""
    
    def setup_method(self):
        """Set up test data."""
        self.test_folders = [
            Folder(path="Inbox", name="Inbox", email_count=25, unread_count=5),
            Folder(path="Sent Items", name="Sent Items", email_count=120, unread_count=0),
            Folder(path="Drafts", name="Drafts", email_count=3, unread_count=3),
            Folder(path="Deleted Items", name="Deleted Items", email_count=42, unread_count=0),
            Folder(path="Custom/Projects", name="Projects", email_count=15, unread_count=2),
            Folder(path="Custom/Archive", name="Archive", email_count=200, unread_count=0),
        ]
    
    def test_organize_folders_into_hierarchy(self):
        """Test that FolderService organizes flat folder list into hierarchy."""
        service = FolderService()
        hierarchy = service.organize_into_hierarchy(self.test_folders)
        
        # Should return a structured hierarchy
        assert isinstance(hierarchy, list)
        
        # Should have root folders and nested structure
        root_folders = [item for item in hierarchy if item['level'] == 0]
        nested_folders = [item for item in hierarchy if item['level'] > 0]
        
        # Should have 4 root folders (Inbox, Sent Items, Drafts, Deleted Items)
        assert len(root_folders) == 4
        
        # Should have 2 nested folders under Custom/
        assert len(nested_folders) == 2
        
        # Nested folders should have level 1
        for folder in nested_folders:
            assert folder['level'] == 1
            assert folder['folder'].path.startswith('Custom/')
    
    def test_format_tree_view(self):
        """Test tree view formatting with proper indentation."""
        service = FolderService()
        tree_output = service.format_tree_view(self.test_folders)
        
        # Should return formatted string
        assert isinstance(tree_output, str)
        
        # Should contain Unicode box drawing characters
        assert "├──" in tree_output or "└──" in tree_output
        
        # Should show nested structure for Custom folders
        lines = tree_output.split('\n')
        custom_lines = [line for line in lines if 'Custom' in line or 'Projects' in line or 'Archive' in line]
        
        # Should have parent "Custom/" and children "Projects", "Archive"
        assert len(custom_lines) >= 3
    
    def test_format_flat_view_with_full_paths(self):
        """Test flat view shows full folder paths."""
        service = FolderService()
        flat_output = service.format_flat_view(self.test_folders)
        
        # Should return formatted string
        assert isinstance(flat_output, str)
        
        # Should show full paths for nested folders
        assert "Custom/Projects" in flat_output
        assert "Custom/Archive" in flat_output
        
        # Should show simple names for root folders
        assert "Inbox" in flat_output
        assert "Sent Items" in flat_output


class TestFolderServiceIntegration:
    """Integration tests for FolderService with real adapters."""
    
    def test_service_works_with_mock_adapter(self):
        """Test FolderService integration with MockOutlookAdapter."""
        # Create adapter and get real folder data
        adapter = AdapterFactory.create_adapter('mock')
        folders = adapter.get_folders()
        
        # Use FolderService with real data
        service = FolderService()
        
        # Test hierarchy organization
        hierarchy = service.organize_into_hierarchy(folders)
        assert len(hierarchy) == 6  # Should have 6 folders from mock adapter
        
        # Test tree view
        tree_output = service.format_tree_view(folders)
        assert "Inbox" in tree_output
        assert "Custom/" in tree_output
        assert "Projects" in tree_output
        assert "Archive" in tree_output
        
        # Test flat view  
        flat_output = service.format_flat_view(folders)
        assert "Custom/Projects" in flat_output
        assert "Custom/Archive" in flat_output
    
    def test_service_works_with_different_folder_structures(self):
        """Test service handles various folder path structures correctly."""
        # Test with different nesting levels
        test_folders = [
            Folder(path="Inbox", name="Inbox", email_count=10, unread_count=1),
            Folder(path="Work/Current", name="Current", email_count=5, unread_count=0),
            Folder(path="Work/Archive/2023", name="2023", email_count=100, unread_count=0),
            Folder(path="Personal/Family", name="Family", email_count=25, unread_count=3),
        ]
        
        service = FolderService()
        
        # Should handle multiple levels correctly
        hierarchy = service.organize_into_hierarchy(test_folders)
        root_folders = [item for item in hierarchy if item['level'] == 0]
        nested_folders = [item for item in hierarchy if item['level'] > 0]
        
        assert len(root_folders) == 1  # Only "Inbox"
        assert len(nested_folders) == 3  # Work/Current, Work/Archive/2023, Personal/Family
        
        # Tree view should group by parent
        tree_output = service.format_tree_view(test_folders)
        assert "Work/" in tree_output
        assert "Personal/" in tree_output
        assert "Current" in tree_output
        assert "Family" in tree_output