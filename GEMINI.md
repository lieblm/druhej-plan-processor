# AGENT DIRECTIVES & SYSTEM CONTEXT (GEMINI.MD) - Base Template

CRITICAL: Read this FIRST at the start of EVERY session.

## 1. SESSION START PROTOCOL
When user instructs to start a session or read copilot instructions, IMMEDIATELY:
1. Search and read essential project documentation (e.g., README.md, architecture docs).
2. Confirm understanding of the current project state.
3. Ask for the task assignment and wait for user input.

## 2. COMMUNICATION & TOKEN ECONOMY
* **Communication Mode**: Absolute. Eliminate emojis, conversational filler, politeness, hype, and soft asks.
* **No Apologies**: When a rule is broken or a mistake is made, NEVER apologize. Instead, provide a clear, actionable correction plan.
* **Output Language**: Čeština (nebo jiný preferovaný jazyk projektu).
* **Format**: Markdown for structured data; clear code blocks for implementation.

## 3. CORE WORKFLOW: PROPOSE -> APPROVE -> IMPLEMENT
* **Approval Checkpoint**: Before executing ANY code/file modification, file creation, or git commit, the AI MUST propose the change and wait for the User's explicit approval.
* **Standard Sequence**:
  1. Inspect current state (read-only).
  2. Analyze impact of the change.
  3. Propose change / Implementation Plan.
  4. Wait for explicit approval (e.g., "OK", "Schváleno").
  5. Implement.
  6. Verify/Test.
* **Fast-Track Exception**: If the User explicitly instructs immediate implementation (e.g., "Implementuj rovnou", "Zapiš to"), bypass the approval checkpoint and execute directly.
* **Read-Only Autonomy**: The AI MUST execute safe, read-only context-gathering operations (ls, cat, grep, git log, etc.) autonomously without requesting User confirmation.

## 4. DEVELOPMENT INTEGRITY & STANDARDS
* **Anti-Fabulation**: NEVER invent certainty for external systems, APIs, or unverified facts. If a parameter or value is unknown, use an explicit placeholder (e.g., `<MISSING_API_KEY>`) rather than guessing.
* **Git History First**: Before implementing a feature or substantial fix, check `git status` and `git log` to understand existing context and avoid duplicating work.
* **Commit Discipline**: 
  * Commit only explicitly approved files and changes.
  * Use clear, concise commit messages (e.g., Conventional Commits format). 
  * NEVER use `git add .` blindly.
* **Code Integrity**: Deliver complete files when modifications are requested, unless a snippet is specifically asked for. Preserve existing imports, comments, and logic that are outside the scope of the change.
* **Secrets Management**: NEVER hard-code secrets, API keys, passwords, or credentials into source code. Always use environment variables or local config files ignored by Git.
* **Environment Awareness**: Always distinguish between local execution and server/production deployment.

## 5. SESSION END PROTOCOL
When user signals session end ("konec", "done", "finish"):
1. DO NOT automatically commit or push.
2. Inspect current git status and relevant diff.
3. Report:
   * Changed files
   * Executed tests (if any)
   * Outstanding issues / Next steps
   * Proposed commit message
4. Wait for explicit User approval before committing.

## 6. PROJECT-SPECIFIC RULES (BAND REHEARSAL AUDIO PROCESSOR)
* **Large Files & Caching**: The AI MUST respect local caching logic (`.pkl` files). When modifying analysis or thresholding logic, the AI MUST propose invalidating or renaming the cache file to prevent stale data usage. NEVER commit large audio (`.mp3`) or cache (`.pkl`) files to Git.
* **Public Repository Neutrality**: The AI MUST keep code, documentation, and CLI arguments generic and band-agnostic. NEVER hardcode the User's specific band name, private local absolute paths, or credentials into the source code.
* **Lightweight Dependencies**: The AI MUST prioritize lightweight mathematical solutions (e.g., `librosa`, `numpy`) over heavy machine-learning dependencies (e.g., PyTorch, Whisper) to ensure the project remains easily installable on standard hardware.
* **Portability & Colab Readiness**: The AI MUST ensure all new file operations and paths remain relative and OS-independent. Code modifications MUST NOT introduce interactive terminal prompts or OS-specific GUI dialogs, preserving the ability to run the script headlessly or via Google Colab.
