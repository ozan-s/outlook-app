# 📄 PRD#1: "Find 2.0" – Powerful Filtering & Folder Listing

---

## tl;dr

Supercharge the `find` (and `read`) commands with precise, programmatic filtering: date (absolute + relative), attachments, read/unread, importance, multi-folder, exclusions, flexible sorting, and result count control.
**PLUS:** Add a new `folders` command to enumerate *all available folders*—flat and as a tree.
Every feature is CLI-native and designed for agent/LLM use.

---

## 1. Problem Statement

The current CLI lets users search by keyword or simple fields, but is missing fine-grained filters and, crucially, any way to discover all Outlook folders.
This blocks agentic workflows (LLMs, automations) and makes scripting less reliable.
**Key product questions resolved in this release:**

* How do users/script/LLMs discover which folders exist?
* How should conflicting or ambiguous CLI flags be handled?
* What’s the best way to balance speed, accuracy, and output manageability for huge mailboxes?

---

## 2. Goals

**Business:**

* Make the CLI the best tool for programmatic Outlook automation (LLMs, scripts, advanced users).

**User:**

* Find emails using precise, composable CLI flags: date (absolute/relative), attachment presence/type, read status, importance, folders, exclusion logic, sender/subject, and result count/order.
* List all accessible folders in Outlook, in both flat and tree view, to empower automation and correct scripting.
* Get explicit feedback/warnings about ambiguous input, for maximum transparency and debuggability.

**Non-goals:**

* No interactive UI/TUI/graphical output.
* No natural language input (that’s PRD#3).

---

## 3. User Stories

* As a user/LLM, I want to **list all Outlook folders** so I can build valid `find`, `read`, or `move` commands—*without guessing* folder names or structures.
* As a user/LLM, I want to **find all unread "Invoice" emails** from the last 2 weeks, sorted newest first, in any folder.
* As a user/LLM, I want to **exclude emails** from certain senders or subjects, and filter for those with specific attachment types, so I can automate business processes.
* As a power user, I want to control paging and sorting, fetching as many results as I need in the order I want.

---

## 4. User Experience & Features

### 4.1 **New Command: Folder Listing**

#### `ocli folders`

**Motivation:**
Scripts, agents, and users need to know *exactly* what folders are available in Outlook to avoid failed commands, typos, or missed messages.
*There is no reliable way to automate email workflows without programmatic folder discovery!*

**CLI Usage:**

```bash
# List all folders, flat (default)
ocli folders

# List all folders as a tree
ocli folders --tree
```

**Sample Output (flat):**

```
Inbox
Inbox/2025
Inbox/2025/June
Sent Items
Archive
Drafts
Inbox/Receipts
```

**Sample Output (tree):**

```
Inbox
  2025
    June
  Receipts
Sent Items
Archive
Drafts
```

**Design Notes:**

* All folder names/paths use the exact names expected by `find`, `read`, or `move`.
* Tree mode is for visual clarity; default output is one folder path per line, for easy parsing.
* Command returns only folders the user/account can access.
* This command will be clearly mentioned in all onboarding/docs as the *canonical way to discover folders*.

---

### 4.2 **Enhanced: Filtering, Sorting, and Paging in `find` and `read`**

#### Supported Filters (all as CLI flags):

* `--since`: Start date, supports `YYYY-MM-DD`, `yesterday`, and relative values (`7d`, `2w`, `1m`)
* `--until`: End date, same format as `--since`
* `--is-unread` / `--is-read`: Filter by read status
* `--has-attachment` / `--no-attachment`: Filter by attachment presence
* `--attachment-type`: Only include emails with given file extension(s)
* `--importance`: `high`, `normal`, `low`
* `--folders`: Space-separated list of folders
* `--not-sender`: Exclude emails by sender (email or display name)
* `--not-subject`: Exclude emails by subject keyword(s)
* `--limit`: Number of results per page (default 10)
* `--all`: Return all matching emails, no paging (warning if >1,000)
* `--sort-by`: Field to sort by (`received_date`, `subject`, `sender`, `importance`)
* `--sort-order`: `desc` (default, newest first), `asc` (oldest first)

**Examples:**

```bash
# Find all unread emails from Alice in June with PDF attachments, sorted oldest first
ocli find --sender alice@company.com --is-unread --since 2025-06-01 --until 2025-06-30 --has-attachment --attachment-type pdf --sort-order asc

# Find all emails from the last 7 days, limit 50 per page
ocli find --since 7d --limit 50

# Show all emails in Inbox, oldest to newest
ocli read --folder Inbox --all --sort-order asc

# List unread, high-importance emails in Inbox and Archive, excluding boss
ocli find --is-unread --importance high --folders Inbox Archive --not-sender boss@evil.com
```

**Design Notes & Decisions:**

* **Conflicting flags:**
  If mutually exclusive flags are provided (e.g., `--is-read` and `--is-unread`), the CLI will select the *first* flag encountered, issue a *warning* about the conflict and the flag used, and proceed.
  *(This is better than silent errors or hard failure, but ensures users/agents are aware of ambiguous input.)*
* **Relative dates:**
  Dates like `7d` (last 7 days), `2w` (last 2 weeks), and `yesterday` are supported for `--since` and `--until`, in addition to explicit `YYYY-MM-DD`.
  *(Relative dates are parsed and converted on the CLI side for reliability.)*
* **Sorting:**
  Results are sorted by `received_date` descending (newest first) by default.
  The user can override sorting with `--sort-by` and `--sort-order`.
  *(This makes result sets more manageable and aligns with typical email review workflows.)*
* **Result control:**
  `--limit` (default 10) and `--all` (no paging) are supported on all commands that return lists, for CLI consistency and easy scripting.
  If `--all` would return more than 1,000 emails, a warning is printed before output, and results stream in order.
* **Exclusion flags:**
  Exclusion filters (e.g., `--not-sender`, `--not-subject`) are always applied after inclusions, for clear and predictable logic.

---

## 5. Narrative

With these improvements, both power users and LLM-based agents can discover every folder in the mailbox and craft precise, stateless CLI queries for any email scenario—*with zero guesswork*.
Ambiguous input is flagged clearly, so automations are safe and debuggable.
This enables everything from daily digests to advanced agentic workflows (summarize unread PDFs from HR last week, etc.), using nothing but the command line.

---

## 6. Success Metrics

* [ ] `ocli folders` command lists *all* user-visible folders reliably (tested on deeply nested folder trees).
* [ ] `find` and `read` support all new filters and sort options, with comprehensive test coverage.
* [ ] Ambiguous/conflicting flags are always warned, with clear messaging.
* [ ] Date filters accept both explicit and relative input, parsing correctly.
* [ ] All relevant commands accept `--limit` and `--all`.
* [ ] Features are fully documented with usage samples.
* [ ] Performance: sub-2s for 1,000 emails; streaming mode handles large sets without crash.

---

## 7. Technical Considerations

* **Flag parsing:**
  Detect conflicts in mutually exclusive flags, warn (stdout/stderr), and pick the first one.
  Relative date parsing handled in CLI arg parser, then passed to services as ISO datetimes.
* **Sorting:**
  Implemented in the service/adapters; respects all sort and order flags, default is newest first.
* **Output streaming:**
  For `--all` with large sets, results are streamed; CLI outputs warning if returning over 1,000 results.
* **Folders:**
  New folder service recurses all accessible folders/subfolders; outputs in flat and tree format as requested.
* **Testing:**
  Add explicit cases for flag conflict, date parsing, large output, and deeply nested folder structures.

---

## 8. Milestones & Sequencing

* Add `folders` command, flat output first → \[\~1 week]
* CLI parser: all new filter/sort/limit flags, flag conflict handling, and relative date support → \[\~2 weeks]
* Service/adapter updates: filtering, sorting, and folder awareness → \[\~2 weeks]
* Tests and docs for all features → \[\~1 week]
* (Optional) Add `folders --tree` for tree output → \[\~2 days]