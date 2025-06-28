**Product Requirements Document (PRD)**

**Project Name:** Outlook CLI Manager (Phase 1)

**Prepared For:** Internal Use (Employer with Outlook Classic Desktop)

**Developer Notes:** Designed with Mac development, Windows runtime, TDD focus

---

### 1. **Objective**

Develop a Python application to manage Microsoft Outlook Classic Desktop via `pywin32`, providing core email management through a Command Line Interface (CLI). The application serves as the foundation for future enhancements, including LLM integration and web interface.

---

### 2. **Scope (Phase 1)**

**Included Features:**

* Read emails from Outlook folders
* Find emails by sender or subject
* Move emails between folders
* CLI interface with batch display (10 emails at a time)
* Ability to open full email content in CLI
* Search entire mailbox by default unless folder specified
* Modular, future-proof architecture for easy expansion
* Full TDD with mocked Outlook interactions for cross-platform development

**Excluded Features (Phase 1):**

* Persistent settings or configurations
* Web interface
* Natural language or LLM integration
* Calendar or contact management

---

### 3. **User Stories**

**CLI User**

* As a user, I can list emails in a folder (or entire mailbox) to quickly scan contents
* As a user, I can search emails by sender or subject keywords across my mailbox
* As a user, I can move selected emails to a different folder
* As a user, I can open an email to read its full content
* As a user, I see results 10 at a time to avoid overwhelming the display

**Developer**

* As a developer, I can run tests on a Mac without Outlook dependencies using mocks
* As a developer, I can isolate platform-specific (Windows `pywin32`) code

---

### 4. **System Requirements**

* **Development Environment:** Mac (TDD, code logic, mocks)
* **Target Runtime:** Windows with Outlook Classic Desktop installed
* **Dependencies:**

  * Python 3.x
  * `pywin32` for Outlook COM interface (Windows-only)
  * Standard libraries for CLI and file handling
  * Testing frameworks (e.g., `unittest`, `pytest`)

---

### 5. **Functional Requirements**

1. **Read Emails**

   * Command: `read [folder]`
   * Lists emails from specified folder or prompts user
   * Displays Subject, Sender, Date
   * Results paginated 10 at a time

2. **Find Emails**

   * Command: `find [--sender=""] [--subject=""] [--folder=""]`
   * Searches entire mailbox by default
   * Supports filtering by sender, subject keywords
   * Results paginated 10 at a time

3. **Move Emails**

   * Command: `move [email_id] [target_folder]`
   * Moves selected email to target folder
   * Prompts for folder if not provided

4. **View Full Email**

   * Command: `open [email_id]`
   * Displays full email body in CLI

5. **Cross-Platform Design**

   * Business logic separate from Outlook-specific code
   * Mocks for Outlook during tests

---

### 6. **Non-Functional Requirements**

* Maintainable, modular codebase
* Clean CLI output formatting
* Minimal hard-coded values
* Portable architecture with platform-specific isolation
* Unit tests with high coverage

---

### 7. **Future Considerations (Phase 2+)**

* Web-based interface
* Persistent settings and preferences
* Natural language queries via LLM
* Advanced search options (date range, attachments)
* Calendar and contacts integration

---

**End of PRD**

