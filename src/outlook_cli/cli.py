"""CLI entry point for Outlook CLI."""

import argparse
import os
import sys
from colorama import init, Fore, Style
from outlook_cli.services.email_reader import EmailReader
from outlook_cli.services.email_searcher import EmailSearcher
from outlook_cli.services.email_mover import EmailMover
from outlook_cli.services.folder_service import FolderService
from outlook_cli.services.paginator import Paginator
from outlook_cli.services.email_sorting_service import EmailSortingService
from outlook_cli.services.filter_parsing_service import FilterParsingService
from outlook_cli.services.command_processing_service import CommandProcessingService
from outlook_cli.config.adapter_factory import AdapterFactory
from outlook_cli.utils.logging_config import setup_logging, get_logger
from outlook_cli.utils.errors import OutlookError, get_error_suggestion
from outlook_cli.utils.performance_monitor import PerformanceMonitor
from outlook_cli.utils.audit_logger import AuditLogger
from outlook_cli.utils.resource_monitor import ResourceMonitor, ResourceExceededError
from outlook_cli.adapters.outlook_adapter import OutlookAdapter

# Initialize colorama for cross-platform color support
init(autoreset=True)


def add_date_filter_arguments(parser):
    """Add date filtering arguments to a command parser."""
    parser.add_argument(
        "--since",
        help="Start date (formats: 2025-06-01, 7d, 2w, 1M, 1y, 2h, 30m, yesterday, today, tomorrow, monday, last-friday, last-week, this-month)",
    )
    parser.add_argument("--until", help="End date (same formats as --since)")


def add_read_status_filter_arguments(parser):
    """Add mutually exclusive read status filter arguments to a command parser."""
    read_status_group = parser.add_mutually_exclusive_group()
    read_status_group.add_argument(
        "--is-read", action="store_true", help="Show only read emails"
    )
    read_status_group.add_argument(
        "--is-unread", action="store_true", help="Show only unread emails"
    )


def add_attachment_filter_arguments(parser):
    """Add attachment filtering arguments to a command parser."""
    attachment_group = parser.add_mutually_exclusive_group()
    attachment_group.add_argument(
        "--has-attachment",
        action="store_true",
        help="Show only emails with attachments",
    )
    attachment_group.add_argument(
        "--no-attachment",
        action="store_true",
        help="Show only emails without attachments",
    )
    parser.add_argument(
        "--attachment-type", help="Filter by file extension (pdf, doc, jpg, etc.)"
    )


def add_content_filter_arguments(parser):
    """Add content filtering arguments to a command parser."""
    parser.add_argument(
        "--importance",
        choices=["high", "normal", "low"],
        help="Filter by importance (high, normal, low)",
    )
    parser.add_argument("--not-sender", help="Exclude emails from specific sender")
    parser.add_argument("--not-subject", help="Exclude emails with subject keywords")


def add_sorting_arguments(parser):
    """Add sorting arguments to a command parser."""
    parser.add_argument(
        "--sort-by",
        choices=["received_date", "subject", "sender", "importance"],
        help="Field to sort by (received_date, subject, sender, importance)",
    )
    parser.add_argument(
        "--sort-order",
        choices=["desc", "asc"],
        default="desc",
        help="Sort order: desc (default) or asc",
    )


def add_common_filter_arguments(parser):
    """Add all common filtering arguments to a command parser."""
    add_date_filter_arguments(parser)
    add_read_status_filter_arguments(parser)
    add_attachment_filter_arguments(parser)
    add_content_filter_arguments(parser)
    add_sorting_arguments(parser)


# Setup logging
setup_logging()
logger = get_logger(__name__)

# Setup monitoring infrastructure
performance_monitor = PerformanceMonitor()
audit_logger = AuditLogger()
resource_monitor = ResourceMonitor()


def _validate_argument_security(args):
    """Validate CLI arguments for security issues like buffer overflow attacks.

    Args:
        args: Parsed command line arguments

    Raises:
        SystemExit: If arguments exceed security limits
    """
    # Maximum allowed length for string arguments (reasonable for email content)
    MAX_ARG_LENGTH = 1000

    # List of string arguments that need length validation
    string_args = [
        "sender",
        "subject",
        "keyword",
        "not_sender",
        "not_subject",
        "folder",
        "message_id",
        "destination",
    ]

    for arg_name in string_args:
        arg_value = getattr(args, arg_name, None)
        if arg_value and isinstance(arg_value, str) and len(arg_value) > MAX_ARG_LENGTH:
            print(
                f"{Fore.RED}Error: Argument '--{arg_name.replace('_', '-')}' exceeds maximum length of {MAX_ARG_LENGTH} characters.{Style.RESET_ALL}"
            )
            print(
                f"{Fore.YELLOW}Provided length: {len(arg_value)} characters{Style.RESET_ALL}"
            )
            sys.exit(1)

    # Validate folder lists (for --folders argument)
    folders_list = getattr(args, "folders", None)
    if folders_list:
        for folder in folders_list:
            if isinstance(folder, str) and len(folder) > MAX_ARG_LENGTH:
                print(
                    f"{Fore.RED}Error: Folder name exceeds maximum length of {MAX_ARG_LENGTH} characters.{Style.RESET_ALL}"
                )
                print(
                    f"{Fore.YELLOW}Folder length: {len(folder)} characters{Style.RESET_ALL}"
                )
                sys.exit(1)


def _create_adapter(args) -> OutlookAdapter:
    """Create adapter based on CLI arguments and configuration."""
    try:
        adapter_type = getattr(args, "adapter", None)
        return AdapterFactory.create_adapter(adapter_type)
    except ValueError as e:
        print(f"{Fore.RED}{str(e)}{Style.RESET_ALL}")
        sys.exit(1)


def _perform_keyword_search(searcher, keyword: str, folder: str) -> list:
    """Perform keyword search using OR logic on sender and subject fields.

    Args:
        searcher: EmailSearcher instance
        keyword: Search keyword
        folder: Folder to search in

    Returns:
        List of Email objects with duplicates removed
    """
    # Search both sender and subject fields
    sender_results = searcher.search_by_sender(keyword, folder)
    subject_results = searcher.search_by_subject(keyword, folder)

    # Combine results and remove duplicates (prioritize subject matches first)
    return _deduplicate_emails(subject_results + sender_results)


def _deduplicate_emails(emails: list) -> list:
    """Remove duplicate emails based on email ID, preserving order.

    Args:
        emails: List of Email objects that may contain duplicates

    Returns:
        List of Email objects with duplicates removed
    """
    seen_ids = set()
    deduplicated = []

    for email in emails:
        if email.id not in seen_ids:
            deduplicated.append(email)
            seen_ids.add(email.id)

    return deduplicated


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
                suggestion = get_error_suggestion(
                    "folder_not_found", {"message": message}
                )
                message += f" {suggestion}"

        print(f"{Fore.RED}Error: {message}{Style.RESET_ALL}")

        # For security-related ValueErrors, exit with error code
        if "suspicious characters" in message.lower():
            sys.exit(1)

    else:
        # Generic error handling
        print(f"{Fore.RED}Error {operation}: {str(error)}{Style.RESET_ALL}")


def _display_email_page(paginator, current_page):
    """Display paginated emails with consistent formatting."""
    page_info = paginator.get_page_info()

    # Display pagination info
    start_item = (page_info["current_page"] - 1) * page_info["items_per_page"] + 1
    end_item = min(start_item + len(current_page) - 1, page_info["total_items"])
    print(
        f"Page {page_info['current_page']} of {page_info['total_pages']}, showing {start_item}-{end_item} of {page_info['total_items']} emails"
    )
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
    print("\n" + "=" * 50)
    print("CONTENT:")
    print("=" * 50)
    print(email.body_text)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="""Outlook CLI for email management with powerful filtering capabilities

Common Examples:
  ocli read --folder Inbox --limit 20                    # Read 20 emails from Inbox
  ocli read --since 7d --is-unread                       # Read unread emails from last 7 days
  ocli find --keyword "meeting" --has-attachment         # Find meeting emails with attachments
  ocli find --sender "john@company.com" --since 1w       # Find emails from John in last week
  ocli find --importance high --folders Inbox Work       # Find high-priority emails in multiple folders
  ocli move <email-id> "Archive"                         # Move email to Archive folder
  ocli open <email-id>                                   # View full email content
  ocli folders --tree                                    # List all folders in tree format

Date Format Examples:
  --since 2025-06-01        # Absolute date (YYYY-MM-DD)
  --since 7d                # Relative: 7 days, 2w (weeks), 1M (months), 1y (years)
  --since yesterday         # Natural: yesterday, today, tomorrow
  --since monday            # Day names: monday, last-friday
  --since last-week         # Periods: last-week, this-month, last-month
        """,
        prog="ocli",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global adapter configuration argument
    parser.add_argument(
        "--adapter",
        choices=["mock", "real"],
        help="Outlook adapter type (default: real on Windows, mock elsewhere, or OUTLOOK_ADAPTER env var)",
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Read command
    read_parser = subparsers.add_parser(
        "read", help="Read and display emails from a folder with filtering options"
    )
    read_parser.add_argument(
        "--folder", default="Inbox", help="Folder to read emails from (default: Inbox)"
    )

    # Add all common filtering arguments
    add_common_filter_arguments(read_parser)

    # Result control
    read_parser.add_argument(
        "--limit", type=int, help="Number of emails to display (default: 10)"
    )

    # Find command
    find_parser = subparsers.add_parser(
        "find", help="Search emails with advanced filtering and criteria"
    )
    find_parser.add_argument(
        "--keyword", help="Search keyword in both subject and sender fields (OR logic)"
    )
    find_parser.add_argument("--sender", help="Filter by specific sender email address")
    find_parser.add_argument("--subject", help="Filter by subject text content")

    # Folder selection (mutually exclusive)
    folder_group = find_parser.add_mutually_exclusive_group()
    folder_group.add_argument(
        "--folder", default="Inbox", help="Single folder to search in (default: Inbox)"
    )
    folder_group.add_argument(
        "--folders", nargs="+", help="Multiple folders to search across"
    )

    # Add all common filtering arguments
    add_common_filter_arguments(find_parser)

    # Result control (mutually exclusive)
    result_control_group = find_parser.add_mutually_exclusive_group()
    result_control_group.add_argument(
        "--limit", type=int, help="Number of results per page (default: 10)"
    )
    result_control_group.add_argument(
        "--all",
        action="store_true",
        help="Return all matching results without pagination",
    )

    # Move command
    move_parser = subparsers.add_parser(
        "move", help="Move a specific email to a target folder"
    )
    move_parser.add_argument("email_id", help="Unique ID of the email to move")
    move_parser.add_argument("target_folder", help="Name of the destination folder")

    # Open command
    open_parser = subparsers.add_parser(
        "open", help="Display full content of a specific email"
    )
    open_parser.add_argument("email_id", help="Unique ID of the email to view")

    # Folders command
    folders_parser = subparsers.add_parser(
        "folders", help="List all available Outlook folders"
    )
    folders_parser.add_argument(
        "--tree",
        action="store_true",
        help="Display folders in hierarchical tree format (default: flat list)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Validate input arguments for security
    _validate_argument_security(args)

    # Route to command handlers
    if args.command == "read":
        handle_read(args)
    elif args.command == "find":
        handle_find(args)
    elif args.command == "move":
        handle_move(args)
    elif args.command == "open":
        handle_open(args)
    elif args.command == "folders":
        handle_folders(args)
    else:
        parser.print_help()


def handle_read(args):
    """Handle read command with filtering support."""
    logger.info(f"Starting read command for folder: {args.folder}")

    # Start performance monitoring
    performance_monitor.start_monitoring("read_command")

    try:
        # Check resource limits before processing
        resource_monitor.check_memory_usage()

        # Use FilterParsingService to parse date arguments
        filter_service = FilterParsingService()
        since_date, until_date = filter_service.parse_date_filters(args)

        # Build search parameters using FilterParsingService
        search_params = filter_service.build_search_params(args, since_date, until_date)

        # Use CommandProcessingService for common processing pattern
        adapter_factory = AdapterFactory()
        command_service = CommandProcessingService(adapter_factory)
        page_size = getattr(args, "limit", None)
        result = command_service.process_email_command(
            args, search_params, "reading emails", page_size
        )

        # Stop performance monitoring and log results
        metrics = performance_monitor.stop_monitoring("read_command")

        # Log audit entry for the operation
        audit_logger.log_filter_operation(
            operation="read",
            filters=search_params,
            user=os.environ.get("USER", "unknown"),
            result_count=len(result["emails"]),
        )

        # Log performance metrics
        audit_logger.log_performance_metrics(
            operation="read",
            duration_seconds=metrics.duration_seconds,
            memory_used_mb=metrics.memory_used_mb,
            result_count=len(result["emails"]),
        )

        logger.info(
            f"Successfully retrieved {len(result['emails'])} emails from {args.folder}"
        )

        # Handle empty results
        if not result["emails"]:
            print(f"No emails found in folder: {args.folder}")
            return

        # Display paginated emails
        _display_email_page(result["paginator"], result["current_page"])

    except ResourceExceededError as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        logger.error(f"Resource limit exceeded in read command: {str(e)}")
    except Exception as e:
        # Handle all errors with enhanced error handling
        _handle_enhanced_error(e, "reading emails")


def handle_find(args):
    """Handle find command."""
    logger.info(
        f"Starting find command with keyword={args.keyword}, sender={args.sender}, subject={args.subject}, folder={args.folder}"
    )

    # Start performance monitoring
    performance_monitor.start_monitoring("find_command")

    try:
        # Check resource limits before processing
        resource_monitor.check_memory_usage()
        # Validate at least one search criteria provided
        has_search_criteria = (
            args.keyword
            or args.sender
            or args.subject
            or args.since
            or args.until
            or args.is_read
            or args.is_unread
            or args.has_attachment
            or args.no_attachment
            or args.importance
            or args.not_sender
            or args.not_subject
        )

        if not has_search_criteria:
            print(
                "Error: Please specify at least one search criteria (--keyword, --sender, --subject, date filters, or other filters)"
            )
            return

        # Use FilterParsingService to parse date arguments
        filter_service = FilterParsingService()
        since_date, until_date = filter_service.parse_date_filters(args)

        # Build base search parameters using FilterParsingService
        base_search_params = filter_service.build_search_params(
            args, since_date, until_date
        )

        # Initialize EmailSearcher with configured adapter
        adapter = _create_adapter(args)
        searcher = EmailSearcher(adapter)

        # Perform search with provided criteria (including new filters)
        if args.keyword:
            # For keyword search, use OR logic: search by sender OR subject, then apply all filters
            sender_params = base_search_params.copy()
            sender_params["sender"] = args.keyword
            sender_results = searcher.search_emails(**sender_params)

            subject_params = base_search_params.copy()
            subject_params["subject"] = args.keyword
            subject_results = searcher.search_emails(**subject_params)

            # Combine results and remove duplicates
            results = _deduplicate_emails(subject_results + sender_results)
        else:
            # For specific sender/subject search, use AND logic with all filters
            specific_params = base_search_params.copy()
            if args.sender:
                specific_params["sender"] = args.sender
            if args.subject:
                specific_params["subject"] = args.subject
            results = searcher.search_emails(**specific_params)

        # Display search summary
        criteria = []
        if args.keyword:
            criteria.append(f"keyword '{args.keyword}' in subject and sender")
        if args.sender and not args.keyword:
            criteria.append(f"sender '{args.sender}'")
        if args.subject and not args.keyword:
            criteria.append(f"subject '{args.subject}'")
        print(
            f"Searching for emails with {' and '.join(criteria)} in folder '{args.folder}':"
        )
        print()

        # Handle empty results and apply common processing (sorting, pagination)
        if not results:
            print("No emails found matching your criteria.")
            return

        # Apply sorting if specified
        if args.sort_by:
            sorting_service = EmailSortingService()
            results = sorting_service.sort_emails(
                results, args.sort_by, args.sort_order
            )

        # Stop performance monitoring and log results
        metrics = performance_monitor.stop_monitoring("find_command")

        # Log audit entry for the operation
        filters = {
            "keyword": args.keyword,
            "sender": args.sender if not args.keyword else None,
            "subject": args.subject if not args.keyword else None,
            "folder": args.folder,
        }
        # Add any other active filters from base_search_params
        filters.update(base_search_params)

        audit_logger.log_filter_operation(
            operation="find",
            filters=filters,
            user=os.environ.get("USER", "unknown"),
            result_count=len(results),
        )

        # Log performance metrics
        audit_logger.log_performance_metrics(
            operation="find",
            duration_seconds=metrics.duration_seconds,
            memory_used_mb=metrics.memory_used_mb,
            result_count=len(results),
        )

        # Check if streaming (--all flag) or pagination (--limit flag)
        if args.all:
            # Use streaming display for --all flag
            from outlook_cli.services.streaming_display import StreamingResultDisplay
            from outlook_cli.services.streaming_paginator import StreamingPaginator
            
            streaming_display = StreamingResultDisplay()
            streaming_paginator = StreamingPaginator()
            
            # Show warning for large result sets
            if len(results) > 1000:
                streaming_display.show_large_result_warning(len(results))
            
            # Stream results in chunks
            streaming_display.stream_results(results, chunk_size=streaming_paginator.get_chunk_size())
        else:
            # Use existing pagination for --limit flag (backward compatibility)
            paginator = Paginator(results, page_size=10)
            current_page = paginator.get_current_page()

            # Display paginated emails
            _display_email_page(paginator, current_page)

    except ResourceExceededError as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        logger.error(f"Resource limit exceeded in find command: {str(e)}")
    except Exception as e:
        # Handle all errors with enhanced error handling
        _handle_enhanced_error(e, "searching emails")


def handle_move(args):
    """Handle move command."""
    logger.info(
        f"Starting move command: email_id={args.email_id}, target_folder={args.target_folder}"
    )
    try:
        # Initialize EmailMover service with configured adapter
        adapter = _create_adapter(args)
        mover = EmailMover(adapter)

        # Execute move operation
        result = mover.move_email_to_folder(args.email_id, args.target_folder)

        # Provide user feedback
        if result:
            print(
                f"{Fore.GREEN}Successfully moved email {args.email_id} to {args.target_folder}{Style.RESET_ALL}"
            )

    except Exception as e:
        # Handle all errors with enhanced error handling
        _handle_enhanced_error(e, "moving email")


def handle_open(args):
    """Handle open command."""
    logger.info(f"Starting open command for email_id: {args.email_id}")
    try:
        # Initialize EmailReader service with configured adapter
        adapter = _create_adapter(args)
        email_reader = EmailReader(adapter)

        # Get the specific email by ID
        email = email_reader.get_email_by_id(args.email_id)

        # Display full email content
        _display_full_email(email)

    except Exception as e:
        # Handle all errors with enhanced error handling
        _handle_enhanced_error(e, "opening email")


def handle_folders(args):
    """Handle folders command."""
    logger.info(f"Starting folders command with tree={args.tree}")
    try:
        # Initialize adapter to get folders with timeout protection
        adapter = _create_adapter(args)

        # Use timeout handler proven to work in Windows corporate environments
        # Based on Milestone 005C testing with 60-second timeouts
        from outlook_cli.utils.timeout_handler import timeout_operation

        with timeout_operation(60.0, "folder enumeration"):
            folders = adapter.get_folders()

        # Initialize folder service for formatting
        folder_service = FolderService()

        # Display folders based on tree flag
        if args.tree:
            print("Folders (tree view):")
            tree_output = folder_service.format_tree_view(folders)
            print(tree_output)
        else:
            print("Available folders:")
            flat_output = folder_service.format_flat_view(folders)
            print(flat_output)

    except Exception as e:
        # Handle all errors with enhanced error handling
        _handle_enhanced_error(e, "listing folders")


if __name__ == "__main__":
    main()
