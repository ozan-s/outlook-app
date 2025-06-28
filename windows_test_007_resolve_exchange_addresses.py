# windows_test_007_resolve_exchange_addresses.py - Resolve Exchange DN to real SMTP
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
    print("Running test: resolve_exchange_addresses")
    print("=" * 50)
    
    try:
        import win32com.client
        
        def resolve_exchange_dn_to_smtp(outlook_app, exchange_dn):
            """Resolve Exchange Distinguished Name to SMTP address."""
            try:
                print(f"    🔍 Resolving Exchange DN: {exchange_dn[:80]}...")
                
                # Method 1: Use AddressEntry to resolve the DN
                try:
                    # Get a recipient object from the DN
                    namespace = outlook_app.GetNamespace("MAPI")
                    
                    # Create a recipient object from the Exchange DN
                    recipient = namespace.CreateRecipient(exchange_dn)
                    
                    if recipient:
                        # Resolve the recipient
                        resolved = recipient.Resolve()
                        print(f"    📋 Recipient resolved: {resolved}")
                        
                        if resolved and recipient.AddressEntry:
                            addr_entry = recipient.AddressEntry
                            print(f"    📋 AddressEntry Type: {getattr(addr_entry, 'Type', 'N/A')}")
                            
                            # Try to get Exchange user from resolved recipient
                            if hasattr(addr_entry, 'GetExchangeUser'):
                                exchange_user = addr_entry.GetExchangeUser()
                                if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                    smtp_addr = exchange_user.PrimarySmtpAddress
                                    if smtp_addr and '@' in smtp_addr:
                                        print(f"    ✅ Method 1 SUCCESS: {smtp_addr}")
                                        return smtp_addr
                                    else:
                                        print(f"    ❌ Method 1: PrimarySmtpAddress empty: {smtp_addr}")
                                else:
                                    print(f"    ❌ Method 1: No ExchangeUser or PrimarySmtpAddress")
                            else:
                                print(f"    ❌ Method 1: No GetExchangeUser method")
                        else:
                            print(f"    ❌ Method 1: Recipient not resolved or no AddressEntry")
                    else:
                        print(f"    ❌ Method 1: Could not create recipient from DN")
                        
                except Exception as e:
                    print(f"    ❌ Method 1 failed: {e}")
                
                # Method 2: Try using the AddressList to find the user
                try:
                    namespace = outlook_app.GetNamespace("MAPI")
                    
                    # Get the Global Address List
                    gal = namespace.AddressLists["Global Address List"]
                    
                    if gal:
                        print(f"    🔍 Searching Global Address List...")
                        
                        # Extract the user part from the Exchange DN
                        # Format: /o=ExchangeLabs/ou=Exchange Administrative Group (FYDIBOHF23SPDLT)/cn=Recipients/cn=94f465afbfe445f5a3ed6202f4bf07ce-NG1NFR1_390
                        if '/cn=' in exchange_dn.lower():
                            # Get the last CN part which should be the user identifier
                            parts = exchange_dn.lower().split('/cn=')
                            if len(parts) >= 2:
                                user_part = parts[-1]  # Get the last part
                                print(f"    🔍 Looking for user part: {user_part}")
                                
                                # Search through address entries
                                entries = gal.AddressEntries
                                print(f"    📋 GAL has {entries.Count} entries")
                                
                                # Check first 10 entries to see the pattern
                                for i in range(1, min(11, entries.Count + 1)):
                                    try:
                                        entry = entries[i]
                                        entry_addr = getattr(entry, 'Address', '').lower()
                                        
                                        if user_part in entry_addr:
                                            print(f"    🎯 Found matching entry: {entry.Name}")
                                            
                                            if hasattr(entry, 'GetExchangeUser'):
                                                exchange_user = entry.GetExchangeUser()
                                                if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                                    smtp_addr = exchange_user.PrimarySmtpAddress
                                                    if smtp_addr and '@' in smtp_addr:
                                                        print(f"    ✅ Method 2 SUCCESS: {smtp_addr}")
                                                        return smtp_addr
                                    except Exception as e:
                                        continue  # Skip entries that cause errors
                        
                        print(f"    ❌ Method 2: User not found in GAL")
                    else:
                        print(f"    ❌ Method 2: Could not access Global Address List")
                        
                except Exception as e:
                    print(f"    ❌ Method 2 failed: {e}")
                
                print(f"    ❌ Could not resolve Exchange DN to SMTP address")
                return None
                
            except Exception as e:
                print(f"    ❌ Resolution failed: {e}")
                return None

        def get_real_sender_smtp(outlook_app, outlook_email):
            """Get the real sender SMTP address by resolving Exchange DN."""
            
            print(f"    🎯 Getting REAL sender SMTP address...")
            
            # Get the sender's Exchange DN
            sender_dn = getattr(outlook_email, 'SenderEmailAddress', '')
            sender_name = getattr(outlook_email, 'SenderName', '')
            
            print(f"    👤 Sender Name: {sender_name}")
            print(f"    📧 Sender DN: {sender_dn[:80]}...")
            
            if sender_dn and sender_dn.startswith('/O='):
                # This is an Exchange DN - resolve it to SMTP
                smtp_addr = resolve_exchange_dn_to_smtp(outlook_app, sender_dn)
                if smtp_addr:
                    return smtp_addr
            
            # Fallback: try other methods
            print(f"    🔄 Trying fallback methods...")
            
            # Try SendUsingAccount as last resort (but note it might be the mailbox owner)
            send_using = getattr(outlook_email, 'SendUsingAccount', None)
            if send_using and '@' in str(send_using):
                print(f"    ⚠️  Fallback to SendUsingAccount: {send_using} (might be mailbox owner, not actual sender)")
                return str(send_using)
            
            return None

        # Connect to Outlook
        print("Connecting to Outlook...")
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6)
        
        print(f"✅ Connected to Outlook")
        print(f"📥 Testing real sender SMTP resolution...")
        
        # Test first 3 emails
        count = min(3, inbox.Items.Count)
        
        for i in range(1, count + 1):
            try:
                email = inbox.Items[i]
                
                print(f"\n📧 EMAIL {i}: {email.Subject or 'No Subject'}")
                print(f"=" * 80)
                
                real_sender_smtp = get_real_sender_smtp(outlook, email)
                
                if real_sender_smtp:
                    print(f"✅ REAL SENDER SMTP: {real_sender_smtp}")
                else:
                    print(f"❌ Could not determine real sender SMTP")
                
                print()
                
            except Exception as e:
                print(f"❌ Error processing email {i}: {e}")
                traceback.print_exc()
        
        print("\n🎉 Exchange DN resolution test completed!")
        print("📋 If this found real sender addresses, we can implement it in the adapter.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_test()