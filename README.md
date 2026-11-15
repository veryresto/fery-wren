# Sakura users Wren MVP

This project answers: **Show users, their submission date, and their verifier approval date.** It is a separate learning project; the existing `../wren-mcp/` deployment is unchanged.

## Semantic layer, step by step

1. `models/profiles/metadata.yml` maps `public.profiles` to the business object `profiles` and exposes only ID, name, and current approval status.
2. `models/profile_events/metadata.yml` maps `public.analytics_events`. `models/governance_events/metadata.yml` maps `public.governance_events`. Their event names and timestamps are the evidence for the two dates.
3. `views/users_with_review_dates/metadata.yml` combines those objects. `MIN(created_at)` selects the first matching event per user; left joins retain users who lack one or both events.
4. `knowledge/rules/user_review_dates.md` explains what the dates mean, how current status differs from event history, and how to interpret nulls. These rules guide an AI client; the SQL view enforces the date calculation.

No database objects are created by these files. Wren reads the existing PostgreSQL tables through a connection profile.

## Review checkpoint

Before using this with an AI client, verify that `profile_completed` is the submission event, `APPROVAL_GRANTED` is verifier approval, and the first event is the desired timestamp when repeats occur. Current production counts from read-only inspection: 39 profiles; 28 approved, 1 pending, 2 suspended, and 8 unsubmitted. Among approved profiles, 28 have a submission event and 27 have an approval event. Missing events remain null.

## Next setup steps

1. Create a Python environment and install `requirements.txt`. This workspace uses `.venv/` and Wren 0.18.0. On this machine, `python3 -m venv .venv` fails because `ensurepip` is absent, so the working setup was:

   ```bash
   python3 -m venv --without-pip .venv
   curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/fery-wren-get-pip.py
   .venv/bin/python /tmp/fery-wren-get-pip.py
   .venv/bin/pip install -r requirements.txt
   ```
2. Run `.venv/bin/wren docs connection-info postgres` to inspect the exact connection fields for this version.
3. Copy `.env.example` to `.env`. Fill in a PostgreSQL role with SELECT access to `public.profiles`, `public.analytics_events`, and `public.governance_events`. Do not commit `.env` or paste its password into chat. If the direct host is unreachable, use the host and port from Supabase's connection string for your network.
4. Run `.venv/bin/wren profile add sakura3-prod-readonly --from-file connection.example.yml`, then `.venv/bin/wren context set-profile sakura3-prod-readonly`. The profile stores `${...}` references; Wren loads the project `.env` when connecting.
5. Run `.venv/bin/wren context build` and `.venv/bin/wren context validate`. To inspect generated SQL without a connection, run `.venv/bin/wren dry-plan --datasource postgres --sql "SELECT * FROM users_with_review_dates LIMIT 5"`.
6. Run `.venv/bin/wren --read-only --sql "SELECT * FROM users_with_review_dates LIMIT 5"` to verify live results.
7. Start the local stdio server with `.venv/bin/wren serve mcp`. Register that command and this project path in your chosen AI client's MCP configuration. Keep an HTTP MCP server local unless you add authentication separately.

The MCP server does not enable `store_query` unless explicitly requested. Use `--read-only` for manual CLI queries. Database permissions are the lasting enforcement boundary, so use a dedicated SELECT-only role for the connection.

The current [Wren OSS modeling guide](https://docs.getwren.ai/oss/guides/model), [MDL reference](https://docs.getwren.ai/oss/reference/mdl), and [MCP guide](https://docs.getwren.ai/oss/guides/mcp) describe these commands and file formats.
