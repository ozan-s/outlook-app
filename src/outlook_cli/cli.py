"""CLI entry point for Outlook CLI."""

import argparse
import sys
from colorama import init, Fore, Style
from outlook_cli.services.email_reader import EmailReader
from outlook_cli.services.email_searcher import EmailSearcher
from outlook_cli.services.email_mover import EmailMover
from outlook_cli.services.paginator import Paginator
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter
from outlook_cli.utils.logging_config import setup_logging, get_logger
from outlook_cli.utils.errors import (
    OutlookError, OutlookConnectionError, OutlookValidationError, 
    OutlookTimeoutError, get_error_suggestion
)

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Setup logging
setup_logging()
logger = get_logger(__name__)


def _handle_enhanced_error(error: Exception, operation: str) -> None:
    """
    Handle enhanced errors with proper logging and user-friendly messages.
    
    Args:
        error: The exception that occurred
        operation: Description of the operation that failed
    """
    logger.error(f"Error in {operation}: {error}")
    
    if isinstance(error, OutlookError):
        # Enhanced error with suggestion
        message = f"Error: {str(error)}"
        if error.suggestion:
            message += f" {error.suggestion}"
        print(f"{Fore.RED}{message}{Style.RESET_ALL}")
        
        # Log additional context for debugging
        if error.context:
            logger.debug(f"Error context: {error.context}")
    
    elif isinstance(error, ValueError):
        # Backward compatibility for existing ValueError patterns
        message = str(error)
        
        # Try to enhance with suggestions based on message content
        if "not found" in message.lower():
            if "folder" in message.lower():
                suggestion = get_error_suggestion("folder_not_found", {"message": message})
                message += f" {suggestion}"
        
        print(f"{Fore.RED}Error: {message}{Style.RESET_ALL}")
    
    else:
        # Generic error handling
        print(f"{Fore.RED}Error {operation}: {str(error)}{Style.RESET_ALL}")


def _display_email_page(paginator, current_page):
    """Display paginated emails with consistent formatting."""
    page_info = paginator.get_page_info()
    
    # Display pagination info
    start_item = (page_info["current_page"] - 1) * page_info["items_per_page"] + 1
    end_item = min(start_item + len(current_page) - 1, page_info["total_items"])
    print(f"Page {page_info['current_page']} of {page_info['total_pages']}, showing {start_item}-{end_item} of {page_info['total_items']} emails")
    print()
    
    # Display emails
    for i, email in enumerate(current_page, start=start_item):
        status = "[UNREAD]" if not email.is_read else "[READ]"
        print(f"{i}. [{email.id}] {status} Subject: {email.subject}")
        print(f"   From: {email.sender_name} <{email.sender_email}>")
        print(f"   Date: {email.received_date.strftime('%Y-%m-%d %H:%M')}")
        if email.has_attachments:
            print("   📎 Has attachments")
        print()


def _display_full_email(email):
    """Display complete email content with professional formatting."""
    status = "[UNREAD]" if not email.is_read else "[READ]"
    print(f"Email ID: {email.id} {status}")
    print(f"Subject: {email.subject}")
    print(f"From: {email.sender_name} <{email.sender_email}>")
    print(f"To: {', '.join(email.recipient_emails)}")
    if email.cc_emails:
        print(f"CC: {', '.join(email.cc_emails)}")
    if email.bcc_emails:
        print(f"BCC: {', '.join(email.bcc_emails)}")
    print(f"Date: {email.received_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"Importance: {email.importance}")
    if email.has_attachments:
        print(f"📎 Attachments: {email.attachment_count}")
    print(f"Folder: {email.folder_path}")
    print("\n" + "="*50)
    print("CONTENT:")
    print("="*50)
    print(email.body_text)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="""Outlook CLI for email management

Examples:
  outlook-cli read Inbox              # Read emails from Inbox folder
  outlook-cli find "meeting"          # Search for emails containing "meeting"
  outlook-cli move inbox-001 "Sent Items"  # Move email to Sent Items folder
  outlook-cli open inbox-001          # Open email for full content view
        """,
        prog="outlook-cli",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Read command
    read_parser = subparsers.add_parser('read', help='Read emails from folder')
    read_parser.add_argument('--folder', default='Inbox', help='Folder to read emails from (default: Inbox)')
    
    # Find command
    find_parser = subparsers.add_parser('find', help='Search emails with filters')
    find_parser.add_argument('--sender', help='Filter by sender email address')
    find_parser.add_argument('--subject', help='Filter by subject text')
    find_parser.add_argument('--folder', default='Inbox', help='Folder to search in (default: Inbox)')
    
    # Move command
    move_parser = subparsers.add_parser('move', help='Move email to target folder')
    move_parser.add_argument('email_id', help='ID of the email to move')
    move_parser.add_argument('target_folder', help='Target folder to move email to')
    
    # Open command
    open_parser = subparsers.add_parser('open', help='Open email for full content view')
    open_parser.add_argument('email_id', help='ID of the email to open')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Route to command handlers
    if args.command == 'read':
        handle_read(args)
    elif args.command == 'find':
        handle_find(args)
    elif args.command == 'move':
        handle_move(args)
    elif args.command == 'open':
        handle_open(args)
    else:
        parser.print_help()


def handle_read(args):
    """Handle read command."""
    logger.info(f"Starting read command for folder: {args.folder}")
    try:
        # Initialize services with MockOutlookAdapter
        adapter = MockOutlookAdapter()
        reader = EmailReader(adapter)
        
        # Get emails from specified folder
        emails = reader.get_emails_from_folder(args.folder)
        logger.info(f"Successfully retrieved {len(emails)} emails from {args.folder}")
        
        # Handle empty folder
        if not emails:
            print(f"No emails found in folder: {args.folder}")
            return
            
        # Paginate emails (10 per page)
        paginator = Paginator(emails, page_size=10)
        current_page = paginator.get_current_page()
        
        # Display paginated emails
        _display_email_page(paginator, current_page)
            
    except Exception as e:
        # Handle all errors with enhanced error handling
        _handle_enhanced_error(e, "reading emails")


def handle_find(args):
    """Handle find command."""
    logger.info(f"Starting find command with sender={args.sender}, subject={args.subject}, folder={args.folder}")
    try:
        # Validate at least one search criteria provided
        if not args.sender and not args.subject:
            print("Error: Please specify --sender and/or --subject to search")
            return
            
        # Initialize EmailSearcher with adapter
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Perform search with provided criteria
        results = searcher.search_emails(
            sender=args.sender,
            subject=args.subject, 
            folder_path=args.folder
        )
        
        # Display search summary
        criteria = []
        if args.sender:
            criteria.append(f"sender '{args.sender}'")
        if args.subject:
            criteria.append(f"subject '{args.subject}'")
        print(f"Searching for emails with {' and '.join(criteria)} in folder '{args.folder}':")
        print()
        
        # Handle empty results
        if not results:
            print("No emails found matching your criteria.")
            return
            
        # Paginate and display results
        paginator = Paginator(results, page_size=10)
        current_page = paginator.get_current_page()
        
        # Display paginated emails
        _display_email_page(paginator, current_page)
            
    except Exception as e:
        # Handle all errors with enhanced error handling
        _handle_enhanced_error(e, "searching emails")


def handle_move(args):
    """Handle move command."""
    logger.info(f"Starting move command: email_id={args.email_id}, target_folder={args.target_folder}")
    try:
        # Initialize EmailMover service with adapter
        adapter = MockOutlookAdapter()
        mover = EmailMover(adapter)
        
        # Execute move operation
        result = mover.move_email_to_folder(args.email_id, args.target_folder)
        
        # Provide user feedback
        if result:
            print(f"{Fore.GREEN}Successfully moved email {args.email_id} to {args.target_folder}{Style.RESET_ALL}")
            
    except Exception as e:
        # Handle all errors with enhanced error handling
        _handle_enhanced_error(e, "moving email")


def handle_open(args):
    """Handle open command."""
    logger.info(f"Starting open command for email_id: {args.email_id}")
    try:
        # Initialize EmailReader service with adapter
        adapter = MockOutlookAdapter()
        email_reader = EmailReader(adapter)
        
        # Get the specific email by ID
        email = email_reader.get_email_by_id(args.email_id)
        
        # Display full email content
        _display_full_email(email)
        
    except Exception as e:
        # Handle all errors with enhanced error handling
        _handle_enhanced_error(e, "opening email")