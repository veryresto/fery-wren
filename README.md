# Sakura users Wren MVP

This project models users in `sakura3Prod` with their first submission event and first verifier approval event. It reads existing Supabase PostgreSQL tables; it creates no database objects.

**Start with the [grounded tutorial](docs/building-the-user-review-semantic-layer.md).** It diagrams the source tables and explains how and why the models, view, and knowledge rule were built.

## Current state

- Wren 0.18.0 compiled and validated 3 models and 1 view.
- A live Wren query and an authenticated remote MCP client both returned the expected 39-profile result.
- The remote endpoint is `https://konteks.veryresto.com/mcp`; deployment and client setup are explained in [the remote MCP guide](docs/deploy-remote-mcp.md).

For a local setup, use [.env.example](.env.example) and [connection.example.yml](connection.example.yml). Keep real credentials in ignored `.env`.
