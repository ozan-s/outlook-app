# windows_test_001_outlook_connection.py - Windows adapter test
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
    print(f"Running test: outlook_connection")
    print("=" * 50)
    
    try:
        import win32com.client
        import platform
        
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.executable}")
        
        # Test Outlook connection
        print("Connecting to Outlook...")
        outlook = win32com.client.Dispatch("Outlook.Application")
        print("✅ Outlook COM interface connected")
        
        # Test namespace access
        namespace = outlook.GetNamespace("MAPI")
        print("✅ MAPI namespace accessible")
        
        # Test folder access
        inbox = namespace.GetDefaultFolder(6)  # olFolderInbox
        sent_items = namespace.GetDefaultFolder(5)  # olFolderSentMail  
        drafts = namespace.GetDefaultFolder(16)  # olFolderDrafts
        
        print(f"📥 Inbox: {inbox.Name} ({inbox.Items.Count} items)")
        print(f"📤 Sent Items: {sent_items.Name} ({sent_items.Items.Count} items)")
        print(f"📝 Drafts: {drafts.Name} ({drafts.Items.Count} items)")
        
        # Test email access if inbox has emails
        if inbox.Items.Count > 0:
            first_email = inbox.Items[1]  # COM collections are 1-indexed
            print(f"✅ Sample email subject: {first_email.Subject[:50]}...")
            print(f"✅ From: {first_email.SenderName}")
            print(f"✅ Received: {first_email.ReceivedTime}")
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_test()
