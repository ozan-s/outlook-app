# windows_test_005_real_smtp_extraction.py - Focus on extracting REAL SMTP addresses
import sys
import os
import traceback
import re
from datetime import datetime, timezone

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def run_test():
    """Execute the test and return results."""
    print("Running test: real_smtp_extraction")
    print("=" * 50)
    
    try:
        import win32com.client
        
        def explore_email_properties(outlook_email, email_index):
            """Explore all available properties of an Outlook email to find SMTP addresses."""
            print(f"\n📧 EXPLORING EMAIL {email_index} PROPERTIES:")
            print(f"Subject: {getattr(outlook_email, 'Subject', 'N/A')}")
            print(f"SenderName: {getattr(outlook_email, 'SenderName', 'N/A')}")
            
            # Try all possible sender address properties
            sender_properties = [
                'SenderEmailAddress',
                'ReplyRecipientNames', 
                'SentOnBehalfOfEmailAddress',
                'SendUsingAccount'
            ]
            
            print("\n🔍 SENDER ADDRESS PROPERTIES:")
            for prop in sender_properties:
                try:
                    value = getattr(outlook_email, prop, None)
                    print(f"  {prop}: {value}")
                except Exception as e:
                    print(f"  {prop}: Error - {e}")
            
            # Explore Sender object if it exists
            try:
                if hasattr(outlook_email, 'Sender') and outlook_email.Sender:
                    sender = outlook_email.Sender
                    print(f"\n👤 SENDER OBJECT:")
                    print(f"  Name: {getattr(sender, 'Name', 'N/A')}")
                    print(f"  Address: {getattr(sender, 'Address', 'N/A')}")
                    
                    if hasattr(sender, 'AddressEntry') and sender.AddressEntry:
                        addr_entry = sender.AddressEntry
                        print(f"  AddressEntry.Address: {getattr(addr_entry, 'Address', 'N/A')}")
                        print(f"  AddressEntry.Type: {getattr(addr_entry, 'Type', 'N/A')}")
                        
                        # Try to get Exchange user
                        try:
                            if hasattr(addr_entry, 'GetExchangeUser'):
                                exchange_user = addr_entry.GetExchangeUser()
                                if exchange_user:
                                    print(f"  ExchangeUser.PrimarySmtpAddress: {getattr(exchange_user, 'PrimarySmtpAddress', 'N/A')}")
                                    print(f"  ExchangeUser.Alias: {getattr(exchange_user, 'Alias', 'N/A')}")
                        except Exception as e:
                            print(f"  ExchangeUser: Error - {e}")
            except Exception as e:
                print(f"Sender object: Error - {e}")
            
            # Explore Recipients
            try:
                if hasattr(outlook_email, 'Recipients') and outlook_email.Recipients.Count > 0:
                    print(f"\n👥 RECIPIENTS ({outlook_email.Recipients.Count} total):")
                    
                    for i in range(1, min(outlook_email.Recipients.Count + 1, 4)):  # Check first 3 recipients
                        try:
                            recip = outlook_email.Recipients[i]
                            print(f"  Recipient {i}:")
                            print(f"    Name: {getattr(recip, 'Name', 'N/A')}")
                            print(f"    Address: {getattr(recip, 'Address', 'N/A')}")
                            print(f"    Type: {getattr(recip, 'Type', 'N/A')}")  # 1=To, 2=CC, 3=BCC
                            
                            if hasattr(recip, 'AddressEntry') and recip.AddressEntry:
                                addr_entry = recip.AddressEntry
                                print(f"    AddressEntry.Address: {getattr(addr_entry, 'Address', 'N/A')}")
                                print(f"    AddressEntry.Type: {getattr(addr_entry, 'Type', 'N/A')}")
                                
                                # Try to get Exchange user for recipient
                                try:
                                    if hasattr(addr_entry, 'GetExchangeUser'):
                                        exchange_user = addr_entry.GetExchangeUser()
                                        if exchange_user:
                                            smtp_addr = getattr(exchange_user, 'PrimarySmtpAddress', 'N/A')
                                            print(f"    ✅ SMTP Address: {smtp_addr}")
                                except Exception as e:
                                    print(f"    ExchangeUser: Error - {e}")
                        except Exception as e:
                            print(f"  Recipient {i}: Error - {e}")
            except Exception as e:
                print(f"Recipients: Error - {e}")
            
            print("=" * 80)

        def get_real_sender_smtp(outlook_email):
            """Try multiple methods to get the real sender SMTP address."""
            
            # Method 1: Direct SenderEmailAddress
            try:
                sender_addr = getattr(outlook_email, 'SenderEmailAddress', None)
                if sender_addr and '@' in sender_addr and not sender_addr.startswith('/O='):
                    print(f"    Method 1 (SenderEmailAddress): {sender_addr}")
                    return sender_addr
            except:
                pass
            
            # Method 2: Sender.AddressEntry.GetExchangeUser().PrimarySmtpAddress
            try:
                if hasattr(outlook_email, 'Sender') and outlook_email.Sender:
                    sender = outlook_email.Sender
                    if hasattr(sender, 'AddressEntry') and sender.AddressEntry:
                        addr_entry = sender.AddressEntry
                        if hasattr(addr_entry, 'GetExchangeUser'):
                            exchange_user = addr_entry.GetExchangeUser()
                            if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                smtp_addr = exchange_user.PrimarySmtpAddress
                                if smtp_addr and '@' in smtp_addr:
                                    print(f"    Method 2 (Sender.ExchangeUser): {smtp_addr}")
                                    return smtp_addr
            except Exception as e:
                print(f"    Method 2 failed: {e}")
            
            # Method 3: Try to find sender in Recipients list (sometimes sender is in recipients)
            try:
                sender_name = getattr(outlook_email, 'SenderName', '')
                if hasattr(outlook_email, 'Recipients') and outlook_email.Recipients.Count > 0:
                    for i in range(1, outlook_email.Recipients.Count + 1):
                        try:
                            recip = outlook_email.Recipients[i]
                            if hasattr(recip, 'Name') and sender_name in recip.Name:
                                if hasattr(recip, 'AddressEntry') and recip.AddressEntry:
                                    addr_entry = recip.AddressEntry
                                    if hasattr(addr_entry, 'GetExchangeUser'):
                                        exchange_user = addr_entry.GetExchangeUser()
                                        if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                            smtp_addr = exchange_user.PrimarySmtpAddress
                                            if smtp_addr and '@' in smtp_addr:
                                                print(f"    Method 3 (Sender in Recipients): {smtp_addr}")
                                                return smtp_addr
                        except:
                            continue
            except Exception as e:
                print(f"    Method 3 failed: {e}")
            
            # Method 4: Extract from Sender.Address if it's SMTP format
            try:
                if hasattr(outlook_email, 'Sender') and outlook_email.Sender:
                    sender = outlook_email.Sender
                    if hasattr(sender, 'Address') and sender.Address:
                        addr = sender.Address
                        if '@' in addr and not addr.startswith('/O='):
                            print(f"    Method 4 (Sender.Address): {addr}")
                            return addr
            except:
                pass
            
            print(f"    ❌ Could not extract real SMTP address for sender")
            return None

        # Connect to Outlook
        print("Connecting to Outlook...")
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6)  # Inbox
        
        print(f"✅ Connected to Outlook")
        print(f"📥 Inbox has {inbox.Items.Count} emails")
        
        # Analyze first 3 emails in detail
        count = min(3, inbox.Items.Count)
        print(f"\n🔍 ANALYZING FIRST {count} EMAILS IN DETAIL:")
        
        for i in range(1, count + 1):
            try:
                email = inbox.Items[i]
                explore_email_properties(email, i)
                
                print(f"\n🎯 EXTRACTING REAL SMTP ADDRESS FOR EMAIL {i}:")
                real_smtp = get_real_sender_smtp(email)
                if real_smtp:
                    print(f"✅ SUCCESS: Real SMTP address found: {real_smtp}")
                else:
                    print(f"❌ FAILED: Could not find real SMTP address")
                
                print("\n" + "="*100)
                
            except Exception as e:
                print(f"❌ Error analyzing email {i}: {e}")
                traceback.print_exc()
        
        print("\n🎉 SMTP extraction analysis completed!")
        print("📋 Use the successful methods above to implement real email extraction.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_test()