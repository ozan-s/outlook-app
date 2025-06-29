"""FolderService handles folder hierarchy organization and display formatting."""

from typing import List, Dict, Any
from outlook_cli.models.folder import Folder


class FolderService:
    """Service for organizing and formatting folder display."""
    
    def organize_into_hierarchy(self, folders: List[Folder]) -> List[Dict[str, Any]]:
        """Organize flat folder list into hierarchical structure.
        
        Args:
            folders: List of Folder objects
            
        Returns:
            List of dictionaries with 'folder' and 'level' keys
        """
        hierarchy = []
        
        for folder in folders:
            if '/' in folder.path:
                # Nested folder - level 1
                hierarchy.append({
                    'folder': folder,
                    'level': 1
                })
            else:
                # Root folder - level 0
                hierarchy.append({
                    'folder': folder,
                    'level': 0
                })
        
        return hierarchy
    
    def format_tree_view(self, folders: List[Folder]) -> str:
        """Format folders as tree view with indentation.
        
        Args:
            folders: List of Folder objects
            
        Returns:
            Formatted tree view string
        """
        hierarchy = self.organize_into_hierarchy(folders)
        lines = []
        
        # Group by parent folders
        root_folders = []
        nested_folders = {}
        
        for item in hierarchy:
            folder = item['folder']
            if item['level'] == 0:
                root_folders.append(folder)
            else:
                # Extract parent path (e.g., "Custom" from "Custom/Projects")
                parent = folder.path.split('/')[0]
                if parent not in nested_folders:
                    nested_folders[parent] = []
                nested_folders[parent].append(folder)
        
        # Format root folders first
        for folder in root_folders:
            lines.append(f"├── {folder.name}")
        
        # Format parent folders with children
        for parent_name, children in nested_folders.items():
            lines.append(f"└── {parent_name}/")
            # Add children with indentation
            for i, child in enumerate(children):
                if i == len(children) - 1:
                    lines.append(f"    └── {child.name}")
                else:
                    lines.append(f"    ├── {child.name}")
        
        return '\n'.join(lines)
    
    def format_flat_view(self, folders: List[Folder]) -> str:
        """Format folders as flat list with full paths.
        
        Args:
            folders: List of Folder objects
            
        Returns:
            Formatted flat view string
        """
        lines = []
        for folder in folders:
            lines.append(f"  {folder.path}")
        
        return '\n'.join(lines)