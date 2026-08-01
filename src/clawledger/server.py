from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable
from urllib.parse import urlparse

from .checkpoint import load_manifest
from .solana import get_latest_blockhash, transaction_base64


SOLANA_ICON = "https://solana.com/src/img/branding/solanaLogoMark.svg"


def _json_bytes(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def make_handler(
    manifest_path: str,
    rpc_url: str,
    blockhash_provider: Callable[[str], str] = get_latest_blockhash,
) -> type[BaseHTTPRequestHandler]:
    class ActionHandler(BaseHTTPRequestHandler):
        server_version = "ClawLedgerAction/0.1"

        def _headers(self, status: int = 200, content_length: int | None = None) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers",
                "Content-Type,Authorization,Content-Encoding,Accept-Encoding",
            )
            if content_length is not None:
                self.send_header("Content-Length", str(content_length))
            self.end_headers()

        def _send(self, payload: object, status: int = 200) -> None:
            body = _json_bytes(payload)
            self._headers(status, len(body))
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self._headers(204)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/actions.json":
                self._send(
                    {
                        "rules": [
                            {"pathPattern": "/anchor", "apiPath": "/api/actions/anchor"},
                            {"pathPattern": "/api/actions/**", "apiPath": "/api/actions/**"},
                        ]
                    }
                )
                return
            if path != "/api/actions/anchor":
                self._send({"message": "not found"}, 404)
                return

            manifest = load_manifest(manifest_path)
            count = manifest["source"]["event_count"]
            root = manifest["merkle"]["root"]
            self._send(
                {
                    "type": "action",
                    "icon": SOLANA_ICON,
                    "title": "Anchor a ZeroClaw audit checkpoint",
                    "description": (
                        f"Publish one Merkle root covering {count} local ZeroClaw events. "
                        "No log content or private key leaves the operator's machine. "
                        f"Root: {root[:16]}…"
                    ),
                    "label": "Review and anchor",
                }
            )

        def do_POST(self) -> None:  # noqa: N802
            if urlparse(self.path).path != "/api/actions/anchor":
                self._send({"message": "not found"}, 404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 16_384:
                    raise ValueError("invalid request size")
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                payer = payload.get("account")
                if not isinstance(payer, str):
                    raise ValueError("missing wallet account")
                manifest = load_manifest(manifest_path)
                memo = manifest["anchor"]["memo"]
                blockhash = blockhash_provider(rpc_url)
                transaction = transaction_base64(payer, blockhash, memo)
                self._send(
                    {
                        "transaction": transaction,
                        "message": "Sign to anchor this ClawLedger checkpoint on Solana.",
                    }
                )
            except (ValueError, KeyError, json.JSONDecodeError) as exc:
                self._send({"message": str(exc)}, 400)
            except Exception as exc:  # fail closed at the HTTP boundary
                self._send({"message": f"unable to build transaction: {exc}"}, 502)

        def log_message(self, format: str, *args: object) -> None:
            return

    return ActionHandler


def serve(manifest_path: str, rpc_url: str, host: str, port: int) -> None:
    handler = make_handler(manifest_path, rpc_url)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"ClawLedger Action listening on http://{host}:{port}/api/actions/anchor")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
