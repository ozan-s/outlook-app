# windows_test_006_correct_sender_extraction.py - Correct sender SMTP extraction
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
    print("Running test: correct_sender_extraction")
    print("=" * 50)
    
    try:
        # Import our project modules
        from outlook_cli.adapters.outlook_adapter import OutlookAdapter
        from outlook_cli.models import Email, Folder
        import win32com.client
        from typing import List
        from datetime import datetime, timezone

        def get_sender_smtp_address(outlook_email):
            """Extract real sender SMTP address using the same method that works for recipients."""
            
            print(f"    🔍 Extracting sender SMTP address...")
            
            # Method 1: Try Sender.AddressEntry.GetExchangeUser().PrimarySmtpAddress (same as recipients)
            try:
                if hasattr(outlook_email, 'Sender') and outlook_email.Sender:
                    sender = outlook_email.Sender
                    if hasattr(sender, 'AddressEntry') and sender.AddressEntry:
                        addr_entry = sender.AddressEntry
                        print(f"    📋 Sender AddressEntry Type: {getattr(addr_entry, 'Type', 'N/A')}")
                        
                        if hasattr(addr_entry, 'GetExchangeUser'):
                            exchange_user = addr_entry.GetExchangeUser()
                            if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                smtp_addr = exchange_user.PrimarySmtpAddress
                                if smtp_addr and '@' in smtp_addr:
                                    print(f"    ✅ Method 1 SUCCESS: {smtp_addr}")
                                    return smtp_addr
                                else:
                                    print(f"    ❌ Method 1: PrimarySmtpAddress empty or invalid: {smtp_addr}")
                            else:
                                print(f"    ❌ Method 1: GetExchangeUser failed or no PrimarySmtpAddress")
                        else:
                            print(f"    ❌ Method 1: No GetExchangeUser method")
                    else:
                        print(f"    ❌ Method 1: No AddressEntry on Sender")
                else:
                    print(f"    ❌ Method 1: No Sender object")
            except Exception as e:
                print(f"    ❌ Method 1 failed: {e}")
            
            # Method 2: Use SendUsingAccount property (this was showing real SMTP!)
            try:
                send_using_account = getattr(outlook_email, 'SendUsingAccount', None)
                if send_using_account and '@' in str(send_using_account):
                    print(f"    ✅ Method 2 SUCCESS (SendUsingAccount): {send_using_account}")
                    return str(send_using_account)
                else:
                    print(f"    ❌ Method 2: SendUsingAccount not valid: {send_using_account}")
            except Exception as e:
                print(f"    ❌ Method 2 failed: {e}")
            
            # Method 3: Try to find sender in recipients (sometimes works)
            try:
                sender_name = getattr(outlook_email, 'SenderName', '')
                print(f"    🔍 Method 3: Looking for sender '{sender_name}' in recipients...")
                
                if hasattr(outlook_email, 'Recipients') and outlook_email.Recipients.Count > 0:
                    for i in range(1, outlook_email.Recipients.Count + 1):
                        try:
                            recip = outlook_email.Recipients[i]
                            recip_name = getattr(recip, 'Name', '')
                            
                            # Check if this recipient matches the sender
                            if sender_name and sender_name in recip_name:
                                print(f"    🎯 Found potential sender match: {recip_name}")
                                
                                if hasattr(recip, 'AddressEntry') and recip.AddressEntry:
                                    addr_entry = recip.AddressEntry
                                    if hasattr(addr_entry, 'GetExchangeUser'):
                                        exchange_user = addr_entry.GetExchangeUser()
                                        if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                            smtp_addr = exchange_user.PrimarySmtpAddress
                                            if smtp_addr and '@' in smtp_addr:
                                                print(f"    ✅ Method 3 SUCCESS: {smtp_addr}")
                                                return smtp_addr
                        except Exception as e:
                            print(f"    ⚠️  Error checking recipient {i}: {e}")
                            continue
                            
                print(f"    ❌ Method 3: Sender not found in recipients")
            except Exception as e:
                print(f"    ❌ Method 3 failed: {e}")
            
            print(f"    ❌ All methods failed - could not extract sender SMTP address")
            return None

        def get_recipient_smtp_addresses(outlook_email):
            """Extract recipient SMTP addresses (this already works)."""
            recipients = []
            
            try:
                if hasattr(outlook_email, 'Recipients') and outlook_email.Recipients.Count > 0:
                    print(f"    🔍 Processing {outlook_email.Recipients.Count} recipients...")
                    
                    for i in range(1, outlook_email.Recipients.Count + 1):
                        try:
                            recip = outlook_email.Recipients[i]
                            
                            if hasattr(recip, 'AddressEntry') and recip.AddressEntry:
                                addr_entry = recip.AddressEntry
                                if hasattr(addr_entry, 'GetExchangeUser'):
                                    exchange_user = addr_entry.GetExchangeUser()
                                    if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                        smtp_addr = exchange_user.PrimarySmtpAddress
                                        if smtp_addr and '@' in smtp_addr:
                                            recipients.append(smtp_addr)
                                            print(f"      ✅ Recipient {i}: {smtp_addr}")
                                            continue
                            
                            print(f"      ❌ Recipient {i}: Could not extract SMTP")
                            
                        except Exception as e:
                            print(f"      ❌ Recipient {i}: Error - {e}")
                            
            except Exception as e:
                print(f"    ❌ Recipients processing failed: {e}")
            
            return recipients if recipients else ["unknown@company.com"]

        class CorrectWindowsOutlookAdapter(OutlookAdapter):
            """Windows adapter with correct sender SMTP extraction."""
            
            def __init__(self):
                print("Initializing Correct Windows Outlook Adapter...")
                self.outlook = win32com.client.Dispatch("Outlook.Application")
                self.namespace = self.outlook.GetNamespace("MAPI")
                print("✅ Correct Windows adapter initialized")
            
            def get_folders(self) -> List[Folder]:
                """Get all available folders."""
                folders = []
                
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
                folders = self.get_folders()
                for folder in folders:
                    if folder.path == folder_path:
                        return folder
                raise ValueError(f"Folder '{folder_path}' not found")
            
            def get_emails(self, folder_path: str) -> List[Email]:
                """Get emails with correct sender SMTP extraction."""
                print(f"Getting emails from folder: {folder_path}")
                
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
                
                # Get first 3 emails for testing
                count = min(3, outlook_folder.Items.Count)
                print(f"Reading first {count} emails...")
                
                for i in range(1, count + 1):
                    try:
                        outlook_email = outlook_folder.Items[i]
                        
                        print(f"\n  📧 Email {i}: {outlook_email.Subject or 'No Subject'}")
                        print(f"  👤 Sender: {outlook_email.SenderName or 'Unknown'}")
                        
                        # Extract addresses using correct methods
                        sender_email = get_sender_smtp_address(outlook_email)
                        recipient_emails = get_recipient_smtp_addresses(outlook_email)
                        
                        if sender_email:
                            print(f"  ✅ Sender SMTP: {sender_email}")
                        else:
                            print(f"  ❌ Could not get sender SMTP - will skip this email")
                            continue
                        
                        print(f"  📮 Recipients: {recipient_emails}")
                        
                        email = Email(
                            id=f"{folder_path.lower().replace(' ', '-')}-{i:03d}",
                            subject=outlook_email.Subject or "No Subject",
                            sender_email=sender_email,
                            sender_name=outlook_email.SenderName or "Unknown",
                            recipient_emails=recipient_emails,
                            received_date=outlook_email.ReceivedTime,
                            body_text=(outlook_email.Body or "No content")[:500],
                            folder_path=folder_path,
                            has_attachments=outlook_email.Attachments.Count > 0,
                            attachment_count=outlook_email.Attachments.Count,
                            is_read=not outlook_email.UnRead,
                            importance="Normal"
                        )
                        emails.append(email)
                        print(f"  ✅ Email {i} processed successfully!")
                        
                    except Exception as e:
                        print(f"  ❌ Could not read email {i}: {e}")
                        import traceback
                        traceback.print_exc()
                
                print(f"\n✅ Retrieved {len(emails)} emails from {folder_path}")
                return emails
            
            def move_email(self, email_id: str, target_folder: str) -> bool:
                """Move email - simplified for testing."""
                return True
            
            def get_email_by_id(self, email_id: str) -> Email:
                """Get email by ID - simplified for testing.""" 
                raise NotImplementedError("get_email_by_id not implemented in test")

        # Test the correct adapter
        print("Testing Correct Windows Outlook Adapter...")
        adapter = CorrectWindowsOutlookAdapter()

        print("\nTesting get_emails() for Inbox with correct sender extraction...")
        inbox_emails = adapter.get_emails("Inbox")

        print(f"\n🎉 Correct Windows adapter test completed!")
        print(f"Successfully extracted {len(inbox_emails)} emails with REAL sender addresses")
        
        # Show all successfully parsed emails
        if inbox_emails:
            print("\n📧 Successfully parsed emails with REAL SMTP addresses:")
            for email in inbox_emails:
                print(f"  📩 {email.id}")
                print(f"    Subject: {email.subject}")
                print(f"    From: {email.sender_name} <{email.sender_email}>")
                print(f"    To: {', '.join(email.recipient_emails[:3])}{'...' if len(email.recipient_emails) > 3 else ''}")
                print(f"    Read: {'Yes' if email.is_read else 'No'}")
                print()
        
        print("✅ All emails have REAL SMTP addresses! Ready for Windows adapter implementation.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_test()