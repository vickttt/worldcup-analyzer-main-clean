# Startup Recovery

Use this when `http://localhost:8502/` cannot open.

## Standard Recovery Flow

1. Open the project launcher:

   `/Users/zijianchen/Documents/Codex/2026-06-14/1-vs-2-polymarket-3-4/worldcup-analyzer/START_APP.command`

2. Wait up to 90 seconds.

3. Check:

   `http://localhost:8502/`

4. If still unavailable, inspect:

   `logs/streamlit_8502.log`

## Codex Rule

When the user says the webpage cannot open, Codex should first run:

`open -a Terminal START_APP.command`

Then verify:

`lsof -i :8502`

`curl -I http://localhost:8502/`

## Important

Do not use macOS LaunchAgent while this project remains inside `Documents`.

Reason:

macOS blocks background services from reading the local virtual environment at `.venv/pyvenv.cfg`.
