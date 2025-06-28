"""CLI entry point for Outlook CLI."""

import argparse
from outlook_cli.services.email_reader import EmailReader
from outlook_cli.services.paginator import Paginator
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter


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
            
    except ValueError:
        # Handle folder not found errors
        print(f"Error: Folder '{args.folder}' not found")
    except Exception as e:
        # Handle other errors
        print(f"Error reading emails: {str(e)}")


def handle_find(args):
    """Handle find command."""
    filters = []
    if args.sender:
        filters.append(f"sender={args.sender}")
    if args.subject:
        filters.append(f"subject={args.subject}")
    filters.append(f"folder={args.folder}")
    print(f"Searching emails with filters: {', '.join(filters)}")


def handle_move(args):
    """Handle move command."""
    print(f"Moving email {args.email_id} to folder: {args.target_folder}")


def handle_open(args):
    """Handle open command."""
    print(f"Opening email: {args.email_id}")