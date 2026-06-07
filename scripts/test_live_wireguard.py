#!/usr/bin/env python3
"""Live test for FritzWireguard (requires reachable Fritz!Box).

Run it locally (on your machine) against a reachable FRITZ!Box.

Environment (or scripts/.env in repo root):
  FRITZ_HOST, FRITZ_USER, FRITZ_PASS
Optional:
  FRITZ_USE_TLS=1 for https (default)
  FRITZ_TOGGLE=1 to toggle first VPN
"""

from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path


def _load_env() -> None:
    for path in (
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parents[2] / "fritzbox-vpn" / ".env",
    ):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("\r"))


def main() -> int:
    _load_env()
    parser = argparse.ArgumentParser(description="Live test for FritzWireguard")
    parser.add_argument("--host", default=os.environ.get("FRITZ_HOST", "192.168.178.1"))
    parser.add_argument("--user", default=os.environ.get("FRITZ_USER", ""))
    parser.add_argument("--password", default=os.environ.get("FRITZ_PASS", ""))
    parser.add_argument(
        "--use-tls",
        action="store_true",
        default=os.environ.get("FRITZ_USE_TLS", "1").lower() in ("1", "true", "yes"),
        help="Use HTTPS (default: enabled)",
    )
    parser.add_argument("--uid", default=None, help="WireGuard connection uid")
    parser.add_argument(
        "--name",
        default=None,
        help="Match a connection by case-insensitive substring of its name.",
    )
    parser.add_argument(
        "--set-active",
        choices=["0", "1"],
        default=None,
        help="Explicitly set desired activated state (0/1) for the selected VPN.",
    )
    parser.add_argument(
        "--toggle-first",
        action="store_true",
        default=os.environ.get("FRITZ_TOGGLE", "").lower() in ("1", "true", "yes"),
        help="Toggle the first VPN connection (default: off unless FRITZ_TOGGLE=1).",
    )
    parser.add_argument(
        "--toggle",
        action="store_true",
        default=False,
        help="Toggle (flip) current active state for the selected VPN.",
    )
    parser.add_argument(
        "--no-restore",
        action="store_true",
        default=False,
        help="Do not revert the connection to its original active state after the test.",
    )
    parser.add_argument(
        "--show-import-path",
        action="store_true",
        default=False,
        help="Print where `fritzconnection` was imported from.",
    )
    args = parser.parse_args()

    host = str(args.host).strip("\r")
    user = str(args.user).strip("\r")
    password = str(args.password).strip("\r")
    use_tls = bool(args.use_tls)

    if not password:
        print("SKIP: FRITZ_PASS not set (no live test)", file=sys.stderr)
        return 0

    # Ensure we test the local checkout (current git working tree), not an
    # unrelated installed `fritzconnection` from site-packages.
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from fritzconnection import FritzConnection
    from fritzconnection.lib.fritzwireguard import FritzWireguard
    import fritzconnection as fritzconnection_pkg

    fc = FritzConnection(
        address=host,
        user=user or None,
        password=password,
        use_tls=use_tls,
    )
    fwg = FritzWireguard(fc=fc)

    if args.show_import_path:
        print(
            f"Using fritzconnection from: {fritzconnection_pkg.__file__} "
            f"(version={getattr(fritzconnection_pkg, '__version__', 'unknown')})"
        )

    print(f"Model: {fc.modelname}, FRITZ!OS: {fc.system_version}")
    connections = fwg.get_vpn_connections()
    if not connections:
        print("FAIL: no VPN connections (empty dict)")
        return 1

    print(f"OK: {len(connections)} VPN connection(s)")
    for uid, conn in connections.items():
        print(
            f"  {uid}: name={conn.get('name')!r} "
            f"active={conn.get('active')} connected={conn.get('connected')}"
        )

    target_uid: str
    if args.uid is not None:
        target_uid = str(args.uid)
    elif args.name is not None:
        needle = str(args.name).strip().lower()
        matches = [
            uid
            for uid, conn in connections.items()
            if str(conn.get("name", "")).lower().find(needle) != -1
        ]
        if not matches:
            print(
                f"FAIL: no VPN connection matches name substring: {args.name}"
            )
            return 1
        target_uid = matches[0]
    else:
        target_uid = next(iter(connections))
    if target_uid not in connections:
        print(f"FAIL: uid not found: {target_uid}")
        return 1

    current = connections[target_uid].get("active", False)
    action = None
    if args.set_active is not None:
        action = "set-active"
    elif args.toggle_first:
        action = "toggle-first"
    elif args.toggle:
        action = "toggle"

    if action is None:
        print("INFO: nothing to do (set --toggle-first, --toggle, or --set-active).")
        return 0

    if args.set_active is not None:
        target = args.set_active == "1"
        print(f"Set {target_uid}: active -> {target}")
    else:
        target = not current
        reason = "first" if args.toggle_first else "selected"
        print(f"Toggle {reason} {target_uid}: {current} -> {target}")

    if not fwg.toggle_vpn(target_uid, enable=target):
        print("FAIL: toggle_vpn returned False")
        return 1

    after = fwg.get_vpn_connections()
    new_active = after.get(target_uid, {}).get("active")
    if new_active != target:
        print(f"FAIL: expected active={target}, got {new_active}")
        return 1
    print("OK: toggle verified")
    # Best-practice: revert to the original state unless disabled.
    if not args.no_restore:
        fwg.toggle_vpn(target_uid, enable=current)
    return 0


if __name__ == "__main__":
    sys.exit(main())

