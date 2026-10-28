---
name: token-tracker
description: >-
  Displays token consumption analytics and real-time usage statistics for the
  current conversation or all conversations. Renders an interactive Generative UI
  card directly in chat and provides access to the auxiliary pane dashboard.
  Trigger with /tokens, /tokens-all, /tokens-update, or questions about token usage.
---

# Token Tracker Skill

Use this skill when the user runs `/tokens`, `/tokens-all`, `/tokens-update`, or asks about token usage across conversations.

## Available Commands

- `/tokens`: Displays real-time token metrics and ratio for the **current** conversation.
- `/tokens-all`: Generates and displays an interactive dashboard with a **chart** of top consumers and a **sortable table** of all conversations (including conversation titles and IDs).
- `/tokens-update`: Updates the plugin to the latest release from the GitHub repository (`maa3x/agy-token-tracker`).

## Workflow for `/tokens-update` (Self-Update)

1. **Run Update Script**:
   Execute the update script located in the plugin directory:
   ```bash
   bash ~/.gemini/config/plugins/token-tracker/scripts/update.sh
   ```

2. **Confirm Status**:
   Report the git pull result and confirm that the plugin is updated to the latest commit.

## Workflow for `/tokens-all` (All Conversations)

1. **Generate Interactive Report**:
   ```bash
   python3 ~/.gemini/config/plugins/token-tracker/scripts/generate_report.py --output <artifactDirectoryPath>/all_tokens_report.html
   ```

2. **Render Inline Widget in Chat**:
   Embed the generated HTML report inline:
   ```html
   <agent-embed src="file:///<artifactDirectoryPath>/all_tokens_report.html"></agent-embed>
   ```

3. **Auxiliary Pane Dashboard**:
   Offer the side pane toggle link:
   ```markdown
   [Open Token Tracker Dashboard](sidecar://token-tracker/dashboard/)
   ```

## Workflow for `/tokens` (Current Conversation)

1. **Calculate Stats**:
   ```bash
   python3 ~/.gemini/config/plugins/token-tracker/scripts/get_tokens.py -c <CONVERSATION_ID> --json
   ```

2. **Generate Widget**:
   Save interactive HTML card at `<artifactDirectoryPath>/token_widget.html` and embed with `<agent-embed>`.
