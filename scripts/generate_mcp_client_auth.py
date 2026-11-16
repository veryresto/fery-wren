"""Generate one Caddy Basic-auth password without printing it.

Run once as root: sudo .venv/bin/python scripts/generate_mcp_client_auth.py
"""

from pathlib import Path
import secrets
import subprocess


ROOT = Path("/etc/fery-wren")
CLIENT = ROOT / "client.env"
CADDY = ROOT / "caddy.env"


def main() -> None:
    if CLIENT.exists() or CADDY.exists():
        raise SystemExit("MCP authentication files already exist; refusing to rotate them")
    ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    password = secrets.token_urlsafe(36)
    result = subprocess.run(
        ["/usr/bin/caddy", "hash-password"],
        input=password + "\n", text=True, capture_output=True, check=True,
    )
    hashed = result.stdout.strip()
    CLIENT.write_text(f"WREN_MCP_USER=wren\nWREN_MCP_PASSWORD={password}\n", encoding="utf-8")
    CADDY.write_text(f"WREN_MCP_PASSWORD_HASH={hashed}\n", encoding="utf-8")
    CLIENT.chmod(0o600)
    CADDY.chmod(0o600)
    print("Generated client.env and caddy.env under /etc/fery-wren with root-only permissions")


if __name__ == "__main__":
    main()
