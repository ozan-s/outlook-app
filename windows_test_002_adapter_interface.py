# windows_test_002_adapter_interface.py - Windows adapter test
import sys
import os
import traceback
from datetime import datetime, timezone

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def run_test():
    """Execute the test and return results."""
    print(f"Running test: adapter_interface")
    print("=" * 50)
    
    try:
        # Import our project modules
        from outlook_cli.adapters.outlook_adapter import OutlookAdapter
        from outlook_cli.models import Email, Folder
        import win32com.client
        from typing import List
        from datetime import datetime, timezone
        
        class WindowsOutlookAdapter(OutlookAdapter):
            """Windows implementation of OutlookAdapter using COM interface."""
            
            def __init__(self):
                print("Initializing Windows Outlook Adapter...")
                self.outlook = win32com.client.Dispatch("Outlook.Application")
                self.namespace = self.outlook.GetNamespace("MAPI")
                print("✅ Windows adapter initialized")
            
            def get_folders(self) -> List[Folder]:
                """Get all available folders."""
                folders = []
                
                # Get default folders
                folder_types = {
                    6: "Inbox",
                    5: "Sent Items", 
                    16: "Drafts",
                    3: "Deleted Items"
                }
                
                for folder_id, folder_name in folder_types.items():
                    try:
                        outlook_folder = self.namespace.GetDefaultFolder(folder_id)
                        folder = Folder(
                            path=folder_name,
                            name=folder_name,
                            email_count=outlook_folder.Items.Count,
                            unread_count=outlook_folder.UnReadItemCount
                        )
                        folders.append(folder)
                        print(f"✅ Folder: {folder_name} ({folder.email_count} emails, {folder.unread_count} unread)")
                    except Exception as e:
                        print(f"❌ Could not access folder {folder_name}: {e}")
                
                return folders
            
            def get_folder_info(self, folder_path: str) -> Folder:
                """Get information about a specific folder."""
                # This is a simplified implementation
                folders = self.get_folders()
                for folder in folders:
                    if folder.path == folder_path:
                        return folder
                raise ValueError(f"Folder '{folder_path}' not found")
            
            def get_emails(self, folder_path: str) -> List[Email]:
                """Get emails from a folder - simplified test implementation."""
                print(f"Getting emails from folder: {folder_path}")
                
                # Map folder names to Outlook folder IDs
                folder_map = {
                    "Inbox": 6,
                    "Sent Items": 5,
                    "Drafts": 16,
                    "Deleted Items": 3
                }
                
                if folder_path not in folder_map:
                    raise ValueError(f"Folder '{folder_path}' not found")
                
                outlook_folder = self.namespace.GetDefaultFolder(folder_map[folder_path])
                emails = []
                
                # Get first 5 emails for testing
                count = min(5, outlook_folder.Items.Count)
                print(f"Reading first {count} emails...")
                
                for i in range(1, count + 1):  # COM collections are 1-indexed
                    try:
                        outlook_email = outlook_folder.Items[i]
                        
                        email = Email(
                            id=f"{folder_path.lower()}-{i:03d}",
                            subject=outlook_email.Subject or "No Subject",
                            sender_email=getattr(outlook_email, 'SenderEmailAddress', 'unknown@example.com'),
                            sender_name=getattr(outlook_email, 'SenderName', 'Unknown'),
                            recipient_emails=[getattr(outlook_email, 'To', 'unknown@example.com')],
                            received_date=outlook_email.ReceivedTime,
                            body_text=getattr(outlook_email, 'Body', 'No content')[:500],  # First 500 chars
                            folder_path=folder_path,
                            has_attachments=outlook_email.Attachments.Count > 0,
                            attachment_count=outlook_email.Attachments.Count,
                            is_read=outlook_email.UnRead == False,
                            importance="Normal"  # Simplified
                        )
                        emails.append(email)
                        print(f"  ✅ Email {i}: {email.subject[:50]}...")
                        
                    except Exception as e:
                        print(f"  ❌ Could not read email {i}: {e}")
                
                print(f"✅ Retrieved {len(emails)} emails from {folder_path}")
                return emails
            
            def move_email(self, email_id: str, target_folder: str) -> bool:
                """Move email - not implemented in this test."""
                print(f"move_email called: {email_id} -> {target_folder}")
                return True
            
            def get_email_by_id(self, email_id: str) -> Email:
                """Get email by ID - not implemented in this test.""" 
                print(f"get_email_by_id called: {email_id}")
                raise NotImplementedError("get_email_by_id not implemented in test")
        
        # Test the adapter
        print("Testing Windows Outlook Adapter...")
        adapter = WindowsOutlookAdapter()
        
        print("\nTesting get_folders()...")
        folders = adapter.get_folders()
        
        print("\nTesting get_emails() for Inbox...")
        inbox_emails = adapter.get_emails("Inbox")
        
        print(f"\n🎉 Windows adapter test completed!")
        print(f"Found {len(folders)} folders and {len(inbox_emails)} emails in Inbox")
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_test()
