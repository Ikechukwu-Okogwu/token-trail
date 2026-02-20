# Contributing to Token Trail

## Branching Strategy

- **main** — stable branch; never push directly.
- Feature branches: `feature/<short-name>` (e.g. `feature/auth-signup`)
- Bug-fix branches: `fix/<short-name>` (e.g. `fix/zip-traversal`)

## Pull Requests

- Keep PRs small and focused (ideally ≤ 300 changed lines).
- Write a short description of *what* changed and *why*.
- Link any related issues.
- At least **1 approval** is required before merging.
- Squash-merge into `main`.

## Code Style

- **Python:** follow PEP 8; use type hints where practical.
- **JavaScript / React:** use functional components.
- Add short comments to explain non-obvious logic.
- Never commit `.env` files or secrets.

## Commit Messages

Use present-tense imperative mood:

- "Add signup endpoint"
- "Fix ZIP path traversal check"
- "Update SETUP.md with Docker troubleshooting"
