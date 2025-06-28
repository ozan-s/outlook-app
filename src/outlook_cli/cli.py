"""CLI entry point for Outlook CLI."""

import argparse
from outlook_cli.services.email_reader import EmailReader
from outlook_cli.services.email_searcher import EmailSearcher
from outlook_cli.services.email_mover import EmailMover
from outlook_cli.services.paginator import Paginator
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter


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
        print(f"{i}. {status} Subject: {email.subject}")
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
        description="Outlook CLI for email management",
        prog="outlook-cli"
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
    try:
        # Initialize services with MockOutlookAdapter
        adapter = MockOutlookAdapter()
        reader = EmailReader(adapter)
        
        # Get emails from specified folder
        emails = reader.get_emails_from_folder(args.folder)
        
        # Handle empty folder
        if not emails:
            print(f"No emails found in folder: {args.folder}")
            return
            
        # Paginate emails (10 per page)
        paginator = Paginator(emails, page_size=10)
        current_page = paginator.get_current_page()
        
        # Display paginated emails
        _display_email_page(paginator, current_page)
            
    except ValueError:
        # Handle folder not found errors
        print(f"Error: Folder '{args.folder}' not found")
    except Exception as e:
        # Handle other errors
        print(f"Error reading emails: {str(e)}")


def handle_find(args):
    """Handle find command."""
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
            
    except ValueError:
        print(f"Error: Folder '{args.folder}' not found")
    except Exception as e:
        print(f"Error searching emails: {str(e)}")


def handle_move(args):
    """Handle move command."""
    try:
        # Initialize EmailMover service with adapter
        adapter = MockOutlookAdapter()
        mover = EmailMover(adapter)
        
        # Execute move operation
        result = mover.move_email_to_folder(args.email_id, args.target_folder)
        
        # Provide user feedback
        if result:
            print(f"Successfully moved email {args.email_id} to {args.target_folder}")
            
    except ValueError as e:
        # Handle service-specific errors (invalid IDs/folders)
        print(f"Error: {str(e)}")
    except Exception as e:
        # Handle unexpected errors
        print(f"Error moving email: {str(e)}")


def handle_open(args):
    """Handle open command."""
    try:
        # Initialize EmailReader service with adapter
        adapter = MockOutlookAdapter()
        email_reader = EmailReader(adapter)
        
        # Get the specific email by ID
        email = email_reader.get_email_by_id(args.email_id)
        
        # Display full email content
        _display_full_email(email)
        
    except ValueError as e:
        # Handle email not found errors
        print(f"Error: {str(e)}")
    except Exception as e:
        # Handle other errors
        print(f"Error opening email: {str(e)}")