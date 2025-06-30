"""PyWin32OutlookAdapter implementation using COM interface.

This module provides a real implementation of OutlookAdapter using pywin32
COM interface to connect to Microsoft Outlook on Windows systems.
"""

from typing import List, Optional
from datetime import datetime
import logging

from .outlook_adapter import OutlookAdapter
from ..models.email import Email
from ..models.folder import Folder

# Platform-specific imports - only available on Windows
try:
    import win32com.client
    from pywintypes import com_error
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class PyWin32OutlookAdapter(OutlookAdapter):
    """Real Outlook adapter using Windows COM interface.
    
    This adapter connects to the actual Microsoft Outlook application
    running on Windows and provides access to real email data.
    """
    
    def __init__(self):
        """Initialize the adapter and connect to Outlook."""
        if not WIN32_AVAILABLE:
            raise ImportError("pywin32 not available - this adapter requires Windows")
        
        self._logger = logging.getLogger(__name__)
        self._outlook = None
        self._namespace = None
        self._connect_to_outlook()
    
    def _connect_to_outlook(self):
        """Establish connection to Outlook COM interface."""
        try:
            self._outlook = win32com.client.Dispatch("Outlook.Application")
            self._namespace = self._outlook.GetNamespace("MAPI")
            self._logger.info("Successfully connected to Outlook via COM")
        except com_error as e:
            raise ValueError(f"Failed to connect to Outlook: {e}")
    
    def get_folders(self) -> List[Folder]:
        """Get all available folders from Outlook.
        
        Returns:
            List[Folder]: All folders accessible through Outlook.
        """
        folders = []
        
        try:
            # Get all accounts/stores
            folders_collection = self._namespace.Folders
            
            # Set start time for timeout protection
            import time
            self._folder_start_time = time.time()
            
            # Use defensive iteration pattern proven to work in Windows corporate environments
            # Based on successful Milestone 005C testing with 48 folders
            index = 1
            consecutive_failures = 0
            max_consecutive_failures = 3
            
            while consecutive_failures < max_consecutive_failures:
                try:
                    account_folder = folders_collection[index]
                    # Add account folders recursively with depth limiting
                    folders.extend(self._get_folders_recursive(account_folder, "", depth=0))
                    consecutive_failures = 0  # Reset on success
                    index += 1
                    
                except (IndexError, com_error) as e:
                    self._logger.warning(f"Skipping inaccessible folder at index {index}: {e}")
                    consecutive_failures += 1
                    index += 1
                    
                    # Safety check: don't iterate beyond reasonable bounds
                    if index > folders_collection.Count + max_consecutive_failures:
                        break
            
            self._logger.info(f"Successfully enumerated {len(folders)} folders")
            return folders
            
        except com_error as e:
            raise ValueError(f"Failed to retrieve folders: {e}")
    
    def _get_folders_recursive(self, com_folder, parent_path: str, depth: int = 0, max_depth: int = 5) -> List[Folder]:
        """Recursively build folder list from COM folder object.
        
        Args:
            com_folder: COM folder object
            parent_path: Path of parent folder
            depth: Current recursion depth
            max_depth: Maximum recursion depth to prevent infinite loops
            
        Returns:
            List[Folder]: Folders found in this folder and subfolders
        """
        folders = []
        
        # Prevent infinite recursion in complex folder hierarchies
        if depth > max_depth:
            self._logger.warning(f"Maximum recursion depth {max_depth} reached for folder {parent_path}")
            return folders
        
        # Aggressive timeout protection - check if we should abort early
        # This helps prevent hanging in problematic folder structures
        import time
        if hasattr(self, '_folder_start_time'):
            elapsed = time.time() - self._folder_start_time
            if elapsed > 45.0:  # Give up after 45 seconds to allow outer timeout to handle
                self._logger.warning(f"Folder enumeration taking too long ({elapsed:.1f}s), stopping early")
                return folders
        
        try:
            # Build folder path with COM property protection
            try:
                folder_name = com_folder.Name
            except (com_error, Exception) as e:
                self._logger.warning(f"Failed to get folder name at depth {depth}: {e}")
                folder_name = f"Unknown_Folder_{depth}"
                
            folder_path = f"{parent_path}/{folder_name}" if parent_path else folder_name
            
            # Get folder statistics with timeout protection for COM property access
            try:
                # Protect against hanging COM property access
                try:
                    email_count = com_folder.Items.Count
                except (AttributeError, com_error, Exception) as e:
                    self._logger.debug(f"Failed to get email count for {folder_path}: {e}")
                    email_count = 0
                
                try:
                    unread_count = com_folder.UnReadItemCount
                except (AttributeError, com_error, Exception) as e:
                    self._logger.debug(f"Failed to get unread count for {folder_path}: {e}")
                    unread_count = 0
                    
            except (AttributeError, com_error, Exception):
                # Some folders may not have these properties or may be inaccessible
                email_count = 0
                unread_count = 0
            
            # Create Folder model
            folder = Folder(
                path=folder_path,
                name=folder_name,
                email_count=email_count,
                unread_count=unread_count
            )
            folders.append(folder)
            
            # Process subfolders using defensive iteration pattern with COM property timeout protection
            if hasattr(com_folder, 'Folders'):
                try:
                    subfolders = com_folder.Folders
                    
                    # Protect against hanging COM property access
                    try:
                        subfolder_count = subfolders.Count
                    except (com_error, Exception) as e:
                        self._logger.warning(f"Failed to get subfolder count for {folder_path}: {e}")
                        subfolder_count = 0
                    
                    if subfolder_count > 0:
                        index = 1
                        consecutive_failures = 0
                        max_consecutive_failures = 3
                        
                        while consecutive_failures < max_consecutive_failures:
                            try:
                                subfolder = subfolders[index]
                                folders.extend(self._get_folders_recursive(subfolder, folder_path, depth + 1, max_depth))
                                consecutive_failures = 0  # Reset on success
                                index += 1
                                
                            except (IndexError, com_error) as e:
                                self._logger.warning(f"Skipping inaccessible subfolder at index {index}: {e}")
                                consecutive_failures += 1
                                index += 1
                                
                                # Safety check: don't iterate beyond reasonable bounds
                                if index > subfolder_count + max_consecutive_failures:
                                    break
                                    
                except (com_error, Exception) as e:
                    self._logger.warning(f"Failed to access subfolders for {folder_path}: {e}")
            
        except com_error as e:
            self._logger.error(f"Error processing folder {parent_path}: {e}")
        
        return folders
    
    def get_folder_info(self, folder_path: str) -> Folder:
        """Get information about a specific folder.
        
        Args:
            folder_path: The path to the folder (e.g., 'Inbox', 'Inbox/Subfolder').
            
        Returns:
            Folder: Information about the specified folder.
            
        Raises:
            ValueError: If the folder path does not exist.
        """
        try:
            com_folder = self._find_folder_by_path(folder_path)
            if not com_folder:
                raise ValueError(f"Folder not found: {folder_path}")
            
            # Get folder statistics
            try:
                email_count = com_folder.Items.Count
                unread_count = com_folder.UnReadItemCount
            except (AttributeError, com_error):
                email_count = 0
                unread_count = 0
            
            return Folder(
                path=folder_path,
                name=com_folder.Name,
                email_count=email_count,
                unread_count=unread_count
            )
            
        except com_error as e:
            raise ValueError(f"Failed to get folder info for {folder_path}: {e}")
    
    def get_emails(self, folder_path: str) -> List[Email]:
        """Get all emails from a specific folder.
        
        Args:
            folder_path: The path to the folder containing emails.
            
        Returns:
            List[Email]: All emails in the specified folder.
            
        Raises:
            ValueError: If the folder path does not exist.
        """
        try:
            com_folder = self._find_folder_by_path(folder_path)
            if not com_folder:
                raise ValueError(f"Folder not found: {folder_path}")
            
            emails = []
            items = com_folder.Items
            
            # COM collections are 1-indexed
            for i in range(1, items.Count + 1):
                try:
                    item = items[i]
                    # Only process email items (ignore calendar, tasks, etc.)
                    if hasattr(item, 'Subject') and hasattr(item, 'SenderEmailAddress'):
                        email = self._convert_com_email_to_model(item, folder_path)
                        if email:
                            emails.append(email)
                except (IndexError, com_error) as e:
                    self._logger.warning(f"Skipping inaccessible email at index {i}: {e}")
                    continue
            
            return emails
            
        except com_error as e:
            raise ValueError(f"Failed to get emails from {folder_path}: {e}")
    
    def move_email(self, email_id: str, target_folder: str) -> bool:
        """Move an email to a different folder.
        
        Args:
            email_id: Unique identifier of the email to move.
            target_folder: Path to the destination folder.
            
        Returns:
            bool: True if the move was successful, False otherwise.
            
        Raises:
            ValueError: If email_id or target_folder does not exist.
        """
        try:
            # Find the email by ID across all folders
            email_item = self._find_email_by_id(email_id)
            if not email_item:
                raise ValueError(f"Email not found: {email_id}")
            
            # Find target folder
            target_com_folder = self._find_folder_by_path(target_folder)
            if not target_com_folder:
                raise ValueError(f"Target folder not found: {target_folder}")
            
            # Move the email
            email_item.Move(target_com_folder)
            return True
            
        except com_error as e:
            self._logger.error(f"Failed to move email {email_id} to {target_folder}: {e}")
            return False
    
    def get_email_by_id(self, email_id: str) -> Email:
        """Get a specific email by its unique identifier.
        
        Args:
            email_id: Unique identifier of the email to retrieve.
            
        Returns:
            Email: The email with the specified ID.
            
        Raises:
            ValueError: If email_id does not exist.
        """
        try:
            email_item = self._find_email_by_id(email_id)
            if not email_item:
                raise ValueError(f"Email not found: {email_id}")
            
            # Determine folder path for this email
            folder_path = self._get_folder_path_for_email(email_item)
            
            email = self._convert_com_email_to_model(email_item, folder_path)
            if not email:
                raise ValueError(f"Failed to convert email {email_id} to model")
            
            return email
            
        except com_error as e:
            raise ValueError(f"Failed to get email {email_id}: {e}")
    
    def _find_folder_by_path(self, folder_path: str):
        """Find COM folder object by path string.
        
        Args:
            folder_path: Folder path like 'Inbox' or 'Account/Inbox/Subfolder'
            
        Returns:
            COM folder object or None if not found
        """
        try:
            # Handle special case for default Inbox
            if folder_path.lower() == 'inbox':
                return self._namespace.GetDefaultFolder(6)  # olFolderInbox = 6
            
            # Parse path components
            path_parts = folder_path.split('/')
            
            # Start with root folders
            folders_collection = self._namespace.Folders
            current_folder = None
            
            # Navigate through path components
            for part in path_parts:
                found = False
                if current_folder is None:
                    # Search root level
                    for i in range(1, folders_collection.Count + 1):
                        try:
                            folder = folders_collection[i]
                            if folder.Name.lower() == part.lower():
                                current_folder = folder
                                found = True
                                break
                        except (IndexError, com_error):
                            continue
                else:
                    # Search in current folder's subfolders
                    if hasattr(current_folder, 'Folders'):
                        subfolders = current_folder.Folders
                        for i in range(1, subfolders.Count + 1):
                            try:
                                folder = subfolders[i]
                                if folder.Name.lower() == part.lower():
                                    current_folder = folder
                                    found = True
                                    break
                            except (IndexError, com_error):
                                continue
                
                if not found:
                    return None
            
            return current_folder
            
        except com_error:
            return None
    
    def _find_email_by_id(self, email_id: str):
        """Find email COM object by ID across all folders.
        
        Args:
            email_id: Email ID to search for
            
        Returns:
            COM email object or None if not found
        """
        # For now, implement basic search across common folders
        # This could be optimized by maintaining an ID-to-folder mapping
        common_folders = ['Inbox', 'Sent Items', 'Drafts', 'Deleted Items']
        
        for folder_name in common_folders:
            try:
                com_folder = self._find_folder_by_path(folder_name)
                if com_folder:
                    items = com_folder.Items
                    for i in range(1, items.Count + 1):
                        try:
                            item = items[i]
                            if hasattr(item, 'EntryID') and item.EntryID == email_id:
                                return item
                        except (IndexError, com_error):
                            continue
            except com_error:
                continue
        
        return None
    
    def _get_folder_path_for_email(self, email_item) -> str:
        """Get folder path for an email item.
        
        Args:
            email_item: COM email object
            
        Returns:
            Folder path string
        """
        try:
            if hasattr(email_item, 'Parent'):
                folder = email_item.Parent
                if hasattr(folder, 'Name'):
                    return folder.Name
        except com_error:
            pass
        
        return "Unknown"
    
    def _convert_com_email_to_model(self, com_email, folder_path: str) -> Optional[Email]:
        """Convert COM email object to Email model.
        
        Args:
            com_email: COM email object
            folder_path: Path of the folder containing this email
            
        Returns:
            Email model instance or None if conversion fails
        """
        try:
            # Extract basic email properties
            email_id = getattr(com_email, 'EntryID', '')
            subject = getattr(com_email, 'Subject', '')
            
            # Extract sender information with Exchange DN resolution
            sender_email = self._extract_sender_smtp(com_email)
            sender_name = getattr(com_email, 'SenderName', '')
            
            # Extract recipient information
            recipient_emails = self._extract_recipient_emails(com_email)
            cc_emails = self._extract_cc_emails(com_email)
            bcc_emails = []  # BCC not typically accessible in received emails
            
            # Extract dates and content
            received_date = getattr(com_email, 'ReceivedTime', datetime.now())
            body_text = getattr(com_email, 'Body', '')
            body_html = getattr(com_email, 'HTMLBody', None)
            
            # Extract attachment information
            has_attachments = getattr(com_email, 'Attachments', None) is not None
            attachment_count = 0
            if has_attachments:
                attachments = getattr(com_email, 'Attachments', None)
                if attachments:
                    attachment_count = attachments.Count
            
            # Extract other properties
            is_read = getattr(com_email, 'UnRead', True) == False
            importance_map = {0: "Low", 1: "Normal", 2: "High"}
            importance = importance_map.get(getattr(com_email, 'Importance', 1), "Normal")
            
            # Validate required fields
            if not email_id or not sender_email or not recipient_emails:
                self._logger.warning(f"Email missing required fields: id={bool(email_id)}, sender={bool(sender_email)}, recipients={bool(recipient_emails)}")
                return None
            
            return Email(
                id=email_id,
                subject=subject,
                sender_email=sender_email,
                sender_name=sender_name,
                recipient_emails=recipient_emails,
                cc_emails=cc_emails,
                bcc_emails=bcc_emails,
                received_date=received_date,
                body_text=body_text,
                body_html=body_html,
                has_attachments=has_attachments,
                attachment_count=attachment_count,
                folder_path=folder_path,
                is_read=is_read,
                importance=importance
            )
            
        except Exception as e:
            self._logger.error(f"Failed to convert COM email to model: {e}")
            return None
    
    def _extract_sender_smtp(self, com_email) -> str:
        """Extract sender SMTP address with Exchange DN resolution.
        
        Args:
            com_email: COM email object
            
        Returns:
            SMTP email address string
        """
        try:
            # Try direct SMTP address first
            sender_email = getattr(com_email, 'SenderEmailAddress', '')
            if sender_email and '@' in sender_email:
                return sender_email
            
            # Handle Exchange DN resolution
            if sender_email and sender_email.startswith('/O='):
                resolved_smtp = self._resolve_exchange_dn_to_smtp(sender_email)
                if resolved_smtp:
                    return resolved_smtp
            
            # Fallback to sender name if available
            sender_name = getattr(com_email, 'SenderName', '')
            if sender_name and '@' in sender_name:
                return sender_name
            
            # Final fallback
            return "unknown@unknown.com"
            
        except Exception as e:
            self._logger.warning(f"Failed to extract sender SMTP: {e}")
            return "unknown@unknown.com"
    
    def _resolve_exchange_dn_to_smtp(self, exchange_dn: str) -> Optional[str]:
        """Resolve Exchange Distinguished Name to SMTP address.
        
        Args:
            exchange_dn: Exchange DN like '/O=EXCHANGELABS/.../CN=user-id'
            
        Returns:
            SMTP address or None if resolution fails
        """
        try:
            # Use proven resolution method from research
            recipient = self._namespace.CreateRecipient(exchange_dn)
            if recipient and recipient.Resolve():
                if hasattr(recipient, 'AddressEntry') and recipient.AddressEntry:
                    address_entry = recipient.AddressEntry
                    if hasattr(address_entry, 'GetExchangeUser'):
                        exchange_user = address_entry.GetExchangeUser()
                        if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                            return exchange_user.PrimarySmtpAddress
            
            return None
            
        except com_error as e:
            self._logger.warning(f"Exchange DN resolution failed for {exchange_dn}: {e}")
            return None
    
    def _extract_recipient_emails(self, com_email) -> List[str]:
        """Extract recipient email addresses.
        
        Args:
            com_email: COM email object
            
        Returns:
            List of recipient SMTP addresses
        """
        recipients = []
        
        try:
            if hasattr(com_email, 'Recipients'):
                recipients_collection = com_email.Recipients
                for i in range(1, recipients_collection.Count + 1):
                    try:
                        recipient = recipients_collection[i]
                        # Check if this is a TO recipient (Type 1)
                        if getattr(recipient, 'Type', 1) == 1:
                            smtp_address = self._extract_recipient_smtp(recipient)
                            if smtp_address:
                                recipients.append(smtp_address)
                    except (IndexError, com_error):
                        continue
            
            # Ensure at least one recipient
            if not recipients:
                recipients.append("unknown@unknown.com")
            
        except Exception as e:
            self._logger.warning(f"Failed to extract recipients: {e}")
            recipients = ["unknown@unknown.com"]
        
        return recipients
    
    def _extract_cc_emails(self, com_email) -> List[str]:
        """Extract CC email addresses.
        
        Args:
            com_email: COM email object
            
        Returns:
            List of CC SMTP addresses
        """
        cc_recipients = []
        
        try:
            if hasattr(com_email, 'Recipients'):
                recipients_collection = com_email.Recipients
                for i in range(1, recipients_collection.Count + 1):
                    try:
                        recipient = recipients_collection[i]
                        # Check if this is a CC recipient (Type 2)
                        if getattr(recipient, 'Type', 1) == 2:
                            smtp_address = self._extract_recipient_smtp(recipient)
                            if smtp_address:
                                cc_recipients.append(smtp_address)
                    except (IndexError, com_error):
                        continue
            
        except Exception as e:
            self._logger.warning(f"Failed to extract CC recipients: {e}")
        
        return cc_recipients
    
    def _extract_recipient_smtp(self, recipient) -> Optional[str]:
        """Extract SMTP address from recipient object.
        
        Args:
            recipient: COM recipient object
            
        Returns:
            SMTP address or None if extraction fails
        """
        try:
            # Direct method for recipients
            if hasattr(recipient, 'AddressEntry') and recipient.AddressEntry:
                address_entry = recipient.AddressEntry
                if hasattr(address_entry, 'GetExchangeUser'):
                    exchange_user = address_entry.GetExchangeUser()
                    if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                        return exchange_user.PrimarySmtpAddress
            
            # Fallback to address property
            if hasattr(recipient, 'Address'):
                address = recipient.Address
                if address and '@' in address:
                    return address
            
            return None
            
        except com_error as e:
            self._logger.warning(f"Failed to extract recipient SMTP: {e}")
            return None