# Sakura users Wren MVP

This project models users in `sakura3Prod` with their first submission event and first verifier approval event. It reads existing Supabase PostgreSQL tables; it creates no database objects.

**Start with the [grounded tutorial](docs/building-the-user-review-semantic-layer.md).** It diagrams the source tables and explains how and why the models, view, and knowledge rule were built.

## Current state

- Wren 0.18.0 compiled and validated 3 models and 1 view.
- Offline SQL planning and knowledge-rule retrieval passed.
- A PostgreSQL connection profile, live Wren query, and connected MCP test remain to be done.

For those next steps, use [.env.example](.env.example) and [connection.example.yml](connection.example.yml) with a SELECT-only database role. Keep real credentials in ignored `.env`.
