"""Create the narrowly scoped PostgreSQL login used by the public MCP service.

Run once as root: sudo .venv/bin/python scripts/provision_reader.py
The generated password is written only to /etc/fery-wren/wren.env.
"""

from pathlib import Path
import secrets

from dotenv import dotenv_values
import psycopg
from psycopg import sql


ROLE = "wren_sakura_reader"
PROJECT_REF = "cycloiewvrajoeosahtd"
ENV_PATH = Path("/etc/fery-wren/wren.env")


def main() -> None:
    if ENV_PATH.exists():
        raise SystemExit(f"{ENV_PATH} already exists; refusing to rotate credentials")

    admin = dotenv_values(Path(__file__).resolve().parents[1] / ".env")
    keys = ("SAKURA_DB_HOST", "SAKURA_DB_PORT", "SAKURA_DB_NAME", "SAKURA_DB_USER", "SAKURA_DB_PASSWORD")
    if any(not admin.get(key) for key in keys):
        raise SystemExit("The local .env is missing a SAKURA_DB_* setting")

    password = secrets.token_urlsafe(36)
    with psycopg.connect(
        host=admin["SAKURA_DB_HOST"], port=admin["SAKURA_DB_PORT"],
        dbname=admin["SAKURA_DB_NAME"], user=admin["SAKURA_DB_USER"],
        password=admin["SAKURA_DB_PASSWORD"], sslmode="require", connect_timeout=10,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (ROLE,))
            if cur.fetchone():
                raise SystemExit(f"Role {ROLE} already exists; refusing to change it")

            cur.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS").format(sql.Identifier(ROLE), sql.Literal(password)))
            cur.execute(sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(sql.Identifier(ROLE)))
            for table, columns in {
                "profiles": ("id", "full_name", "approval_status"),
                "analytics_events": ("id", "user_id", "event_name", "created_at"),
                "governance_events": ("id", "target_user_id", "action", "created_at"),
            }.items():
                cur.execute(sql.SQL("GRANT SELECT ({}) ON public.{} TO {}").format(
                    sql.SQL(", ").join(map(sql.Identifier, columns)),
                    sql.Identifier(table), sql.Identifier(ROLE),
                ))
            # The existing admin policies depend on auth.uid() and user_roles.
            # They apply to PUBLIC even though only signed-in app users can
            # satisfy them. Scope them to Supabase's authenticated role so
            # this independent database login evaluates only its own policies.
            cur.execute(sql.SQL(
                "ALTER POLICY {} ON public.analytics_events TO authenticated"
            ).format(sql.Identifier("Admins can view all analytics events")))
            cur.execute(sql.SQL(
                "ALTER POLICY {} ON public.governance_events TO authenticated"
            ).format(sql.Identifier("Admins and verifiers can view governance events")))
            cur.execute(sql.SQL(
                "CREATE POLICY wren_reader_submissions ON public.analytics_events "
                "FOR SELECT TO {} USING (event_name = 'profile_completed')"
            ).format(sql.Identifier(ROLE)))
            cur.execute(sql.SQL(
                "CREATE POLICY wren_reader_approvals ON public.governance_events "
                "FOR SELECT TO {} USING (action = 'APPROVAL_GRANTED')"
            ).format(sql.Identifier(ROLE)))

    ENV_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    ENV_PATH.write_text(
        f"WREN_DB_HOST={admin['SAKURA_DB_HOST']}\n"
        f"WREN_DB_PORT={admin['SAKURA_DB_PORT']}\n"
        f"WREN_DB_NAME={admin['SAKURA_DB_NAME']}\n"
        f"WREN_DB_USER={ROLE}.{PROJECT_REF}\n"
        f"WREN_DB_PASSWORD={password}\n",
        encoding="utf-8",
    )
    ENV_PATH.chmod(0o600)
    print(f"Created {ROLE} with column-limited SELECT and event RLS policies")
    print(f"Saved its connection settings to {ENV_PATH} (root-only)")


if __name__ == "__main__":
    main()
