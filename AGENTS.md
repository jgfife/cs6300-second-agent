# AGENTS.md

Build & Run: `make install` (creates `.virtual_environment`), then activate: `. .virtual_environment/bin/activate`.
Primary Agent: `python src/adventure_agent.py` (sets up smolagents + tools).
Tests: `make test` or `pytest -v`.
Single Test File: `pytest tests/test_adventure_agent.py::TestAdventureAgent::test_some_case -v` (replace with real name).
List Tests: `pytest --collect-only -q`.
Python: 3.12+. Keep code compatible with standard library first.
Imports Order: stdlib, third-party, local (grouped, no blank lines inside group).
Dependencies: managed via `requirements.txt`; do NOT pin ad‑hoc in code.
Env Vars: load with `python-dotenv`; Gemini key as `GEMINI_API_KEY` in `.env` (never commit secrets).
Types: Use annotations for functions, class attributes (e.g., `name: str = "..."`). Prefer explicit `Optional[T]`, `List[T]`, etc.
Docstrings: Triple-quoted; include short summary + Args/Returns; public tools clearly describe side effects and output format.
Functions: pure where possible; keep network calls wrapped in `try/except RequestException` returning clear error strings (pattern in `visit_webpage`).
Error Handling: Validate inputs early; return informative error messages (do not swallow unexpected exceptions silently—either re-raise or stringify consistently as shown).
Style: snake_case for functions/vars, PascalCase for classes, UPPER_CASE for constants; avoid one-letter names except loop indices.
Formatting: Follow existing spacing; keep lines reasonably short (<100 chars); no trailing whitespace; no unused imports.
Testing Conventions: Files `test_*.py`, classes `Test*`, functions `test_*` (see `pytest.ini`). Use `pytest-mock` for external API isolation.
Network Calls: Consider mocking external HTTP for deterministic tests; truncate large payloads (>5k chars) like `visit_webpage`.
Logging/Tracing: Phoenix instrumentation auto-registered; avoid excessive prints—prefer structured summaries returned by tools.
No Cursor/Copilot rule files present; this document is authoritative for agents.
