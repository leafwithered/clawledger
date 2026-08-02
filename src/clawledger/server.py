from __future__ import annotations

import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from .checkpoint import load_manifest
from .solana import get_latest_blockhash, transaction_base64


SOLANA_ICON = "https://solana.com/src/img/branding/solanaLogoMark.svg"
SOLANA_DEVNET_CHAIN_ID = "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1"
ACTION_VERSION = "2.4"
MEMO_PROGRAM_ID = "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"
WEB3_URL = "/vendor/solana-web3-1.98.4.iife.min.js"
WEB3_SRI = "sha384-I45YF+S0YGWIolUyTksLk9TNtTqaDgZg8e6T1OoBoJvvFmphqYNIPZw3Kl0TkZNN"
WEB3_ASSET = Path(__file__).with_name("vendor") / "solana-web3-1.98.4.iife.min.js"


SIGNER_JS = r"""
"use strict";

const app = document.querySelector("main");
const connectButton = document.querySelector("#connect");
const anchorButton = document.querySelector("#anchor");
const statusBox = document.querySelector("#status");
const accountBox = document.querySelector("#account");
const explorerLink = document.querySelector("#explorer");
const expectedMemo = app.dataset.memo;
const memoProgram = app.dataset.memoProgram;
let provider;
let account;

function setStatus(message, kind = "info") {
  statusBox.textContent = message;
  statusBox.dataset.kind = kind;
}

function decodeBase64(value) {
  const binary = atob(value);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

function validateTransaction(transaction) {
  if (transaction.signatures.length !== 1) {
    throw new Error("Expected exactly one signature slot.");
  }
  if (transaction.signatures[0].publicKey.toString() !== account) {
    throw new Error("Wallet is not the transaction signer.");
  }
  if (transaction.feePayer?.toString() !== account) {
    throw new Error("Wallet is not the transaction fee payer.");
  }
  if (transaction.instructions.length !== 1) {
    throw new Error("Expected exactly one transaction instruction.");
  }
  const instruction = transaction.instructions[0];
  if (instruction.programId.toString() !== memoProgram) {
    throw new Error("The only instruction is not the Solana Memo program.");
  }
  if (instruction.keys.length !== 0) {
    throw new Error("Memo instruction unexpectedly references accounts.");
  }
  const actualMemo = new TextDecoder().decode(instruction.data);
  if (actualMemo !== expectedMemo) {
    throw new Error("Memo does not match the verified local checkpoint.");
  }
}

async function connectWallet() {
  connectButton.disabled = true;
  try {
    provider = window.phantom?.solana;
    if (!provider?.isPhantom) {
      throw new Error("Phantom is not available in this browser profile.");
    }
    const result = await provider.connect();
    account = (result.publicKey || provider.publicKey).toString();
    accountBox.textContent = account;
    anchorButton.disabled = false;
    setStatus("Connected. The transaction will be checked locally before Phantom sees it.", "ok");
  } catch (error) {
    connectButton.disabled = false;
    setStatus(error.message || String(error), "error");
  }
}

connectButton.addEventListener("click", connectWallet);

anchorButton.addEventListener("click", async () => {
  anchorButton.disabled = true;
  explorerLink.hidden = true;
  try {
    setStatus("Building a fresh unsigned devnet transaction…");
    const response = await fetch("/api/actions/anchor", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({account}),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.message || "Unable to build transaction.");
    }
    const transaction = solanaWeb3.Transaction.from(decodeBase64(payload.transaction));
    validateTransaction(transaction);
    setStatus("Checks passed. Review the one-Memo devnet transaction in Phantom.", "ok");
    const result = await provider.signAndSendTransaction(transaction);
    const signature = result.signature;
    explorerLink.href = `https://explorer.solana.com/tx/${encodeURIComponent(signature)}?cluster=devnet`;
    explorerLink.textContent = signature;
    explorerLink.hidden = false;
    setStatus("Broadcast submitted. Open the public devnet transaction below.", "ok");
  } catch (error) {
    anchorButton.disabled = false;
    setStatus(error.message || String(error), "error");
  }
});
""".strip()


def _signer_html(manifest: dict[str, object]) -> bytes:
    source = manifest["source"]
    merkle = manifest["merkle"]
    anchor = manifest["anchor"]
    count = html.escape(str(source["event_count"]))
    root = html.escape(str(merkle["root"]))
    memo = html.escape(str(anchor["memo"]), quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>ClawLedger devnet anchor</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, system-ui, sans-serif; }}
    body {{ margin: 0; background: #071016; color: #eaf7ff; }}
    main {{ max-width: 760px; margin: 48px auto; padding: 32px; background: #10202a; border: 1px solid #294352; border-radius: 18px; }}
    h1 {{ margin-top: 0; }}
    .warning {{ color: #ffd285; }}
    dl {{ display: grid; grid-template-columns: 110px 1fr; gap: 10px; }}
    dt {{ color: #9eb9c8; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    code {{ color: #92f5ce; }}
    button {{ margin: 20px 12px 0 0; padding: 12px 18px; border: 0; border-radius: 10px; background: #ab9ff2; color: #11151a; font-weight: 700; cursor: pointer; }}
    button:disabled {{ opacity: .45; cursor: not-allowed; }}
    #status {{ margin-top: 22px; padding: 14px; border-radius: 10px; background: #09151c; }}
    #status[data-kind="ok"] {{ color: #92f5ce; }}
    #status[data-kind="error"] {{ color: #ff9c9c; }}
    a {{ display: block; margin-top: 14px; color: #ab9ff2; overflow-wrap: anywhere; }}
  </style>
  <script defer src="{WEB3_URL}" integrity="{WEB3_SRI}" crossorigin="anonymous"></script>
  <script defer src="/anchor.js"></script>
</head>
<body>
  <main data-memo="{memo}" data-memo-program="{MEMO_PROGRAM_ID}">
    <h1>ClawLedger devnet anchor</h1>
    <p class="warning">Use a disposable wallet with devnet SOL only. This transaction must contain no transfer.</p>
    <dl>
      <dt>Network</dt><dd>Solana devnet</dd>
      <dt>Events</dt><dd>{count}</dd>
      <dt>Merkle root</dt><dd><code>{root}</code></dd>
      <dt>Memo</dt><dd><code>{html.escape(str(anchor["memo"]))}</code></dd>
      <dt>Wallet</dt><dd id="account">Not connected</dd>
    </dl>
    <button id="connect" type="button">Connect Phantom</button>
    <button id="anchor" type="button" disabled>Review and anchor on devnet</button>
    <div id="status">The wallet stays in control of signing and broadcasting.</div>
    <a id="explorer" hidden rel="noreferrer" target="_blank"></a>
  </main>
</body>
</html>""".encode("utf-8")


def _json_bytes(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def make_handler(
    manifest_path: str,
    rpc_url: str,
    blockhash_provider: Callable[[str], str] = get_latest_blockhash,
) -> type[BaseHTTPRequestHandler]:
    class ActionHandler(BaseHTTPRequestHandler):
        server_version = "ClawLedgerAction/0.1"

        def _headers(
            self,
            status: int = 200,
            content_length: int | None = None,
            content_type: str = "application/json",
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers",
                "Content-Type,Authorization,Content-Encoding,Accept-Encoding",
            )
            self.send_header(
                "Access-Control-Expose-Headers",
                "X-Action-Version,X-Blockchain-Ids",
            )
            self.send_header("X-Action-Version", ACTION_VERSION)
            self.send_header("X-Blockchain-Ids", SOLANA_DEVNET_CHAIN_ID)
            if content_length is not None:
                self.send_header("Content-Length", str(content_length))
            self.end_headers()

        def _send(self, payload: object, status: int = 200) -> None:
            body = _json_bytes(payload)
            self._headers(status, len(body))
            self.wfile.write(body)

        def _send_asset(self, body: bytes, content_type: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; script-src 'self'; "
                "style-src 'unsafe-inline'; connect-src 'self'; img-src data:; "
                "base-uri 'none'; frame-ancestors 'none'",
            )
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self) -> None:  # noqa: N802
            self._headers(204)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path in {"/", "/anchor"}:
                self._send_asset(
                    _signer_html(load_manifest(manifest_path)),
                    "text/html; charset=utf-8",
                )
                return
            if path == "/anchor.js":
                self._send_asset(
                    SIGNER_JS.encode("utf-8"),
                    "text/javascript; charset=utf-8",
                )
                return
            if path == WEB3_URL:
                self._send_asset(
                    WEB3_ASSET.read_bytes(),
                    "text/javascript; charset=utf-8",
                )
                return
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
            path = urlparse(self.path).path
            if path != "/api/actions/anchor":
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
    print(f"ClawLedger signer: http://{host}:{port}/anchor")
    print(f"ClawLedger Action: http://{host}:{port}/api/actions/anchor")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
