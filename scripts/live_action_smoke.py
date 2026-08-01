"""Read-only live smoke test for the devnet-backed Solana Action."""

from __future__ import annotations

import base64
import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from clawledger.server import make_handler
from clawledger.solana import b58encode, extract_memos


def main() -> int:
    project = Path(__file__).resolve().parents[1]
    manifest_path = project / "sample-checkpoint.json"
    if not manifest_path.exists():
        raise SystemExit("run the sample checkpoint command first")

    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        make_handler(str(manifest_path), "https://api.devnet.solana.com"),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        payer = b58encode(bytes(range(32)))
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/api/actions/anchor",
            data=json.dumps({"account": payer}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        transaction = base64.b64decode(payload["transaction"])
        memos = extract_memos(transaction)
        expected = json.loads(manifest_path.read_text(encoding="utf-8"))["anchor"]["memo"]
        if memos != [expected]:
            raise SystemExit(f"unexpected transaction Memo: {memos!r}")
        print(
            json.dumps(
                {
                    "ok": True,
                    "rpc": "https://api.devnet.solana.com",
                    "transaction_bytes": len(transaction),
                    "memo": memos[0],
                    "signed": False,
                    "broadcast": False,
                },
                indent=2,
            )
        )
        return 0
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
