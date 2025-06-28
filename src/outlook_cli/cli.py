"""CLI entry point for Outlook CLI."""

import argparse


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
    print(f"Reading emails from folder: {args.folder}")


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