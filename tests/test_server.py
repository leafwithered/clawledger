import base64
import hashlib
import json
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path

from clawledger.server import make_handler
from clawledger.solana import extract_memos


PAYER = "11111111111111111111111111111111"
BLOCKHASH = "SysvarC1ock11111111111111111111111111111111"


class ActionServerTests(unittest.TestCase):
    def test_get_and_post_action(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "checkpoint.json"
            memo = "clawledger:v1:" + "cd" * 32 + ":3"
            manifest_path.write_text(
                json.dumps(
                    {
                        "schema": "clawledger.checkpoint/v1",
                        "source": {"event_count": 3},
                        "merkle": {"root": "cd" * 32},
                        "anchor": {"memo": memo},
                    }
                ),
                encoding="utf-8",
            )
            handler = make_handler(
                str(manifest_path),
                "http://unused.invalid",
                blockhash_provider=lambda _url: BLOCKHASH,
            )
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base_url = f"http://127.0.0.1:{server.server_port}"
                with urllib.request.urlopen(base_url + "/api/actions/anchor") as response:
                    get_payload = json.loads(response.read())
                    self.assertEqual(response.headers["Access-Control-Allow-Origin"], "*")
                    self.assertIn("Accept-Encoding", response.headers["Access-Control-Allow-Headers"])
                    self.assertIn(
                        "X-Blockchain-Ids",
                        response.headers["Access-Control-Expose-Headers"],
                    )
                    self.assertEqual(response.headers["X-Action-Version"], "2.4")
                    self.assertEqual(
                        response.headers["X-Blockchain-Ids"],
                        "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1",
                    )
                self.assertEqual(get_payload["label"], "Review and anchor")
                self.assertEqual(get_payload["type"], "action")

                with urllib.request.urlopen(base_url + "/anchor") as response:
                    signer_html = response.read().decode("utf-8")
                    self.assertEqual(response.headers["Content-Type"], "text/html; charset=utf-8")
                    self.assertIn("default-src 'none'", response.headers["Content-Security-Policy"])
                self.assertIn(memo, signer_html)
                self.assertIn("Connect Phantom", signer_html)
                self.assertIn("integrity=\"sha384-", signer_html)
                self.assertNotIn("https://unpkg.com", signer_html)

                with urllib.request.urlopen(
                    base_url + "/vendor/solana-web3-1.98.4.iife.min.js"
                ) as response:
                    web3_asset = response.read()
                    self.assertEqual(
                        response.headers["Content-Type"],
                        "text/javascript; charset=utf-8",
                    )
                self.assertEqual(
                    base64.b64encode(hashlib.sha384(web3_asset).digest()).decode(),
                    "I45YF+S0YGWIolUyTksLk9TNtTqaDgZg8e6T1OoBoJvvFmphqYNIPZw3Kl0TkZNN",
                )

                with urllib.request.urlopen(base_url + "/anchor.js") as response:
                    signer_js = response.read().decode("utf-8")
                    self.assertEqual(
                        response.headers["Content-Type"],
                        "text/javascript; charset=utf-8",
                    )
                self.assertIn("transaction.instructions.length !== 1", signer_js)
                self.assertIn("provider.signAndSendTransaction(transaction)", signer_js)
                self.assertIn('updateLocalSession("broadcast"', signer_js)

                with urllib.request.urlopen(base_url + "/api/local-session") as response:
                    self.assertEqual(json.loads(response.read()), {"status": "ready"})
                session_request = urllib.request.Request(
                    base_url + "/api/local-session",
                    data=json.dumps({"status": "connected", "account": PAYER}).encode(),
                    headers={"Content-Type": "application/json", "Origin": base_url},
                    method="POST",
                )
                with urllib.request.urlopen(session_request) as response:
                    self.assertEqual(json.loads(response.read()), {"stored": True})
                with urllib.request.urlopen(base_url + "/api/local-session") as response:
                    session_payload = json.loads(response.read())
                self.assertEqual(session_payload, {"status": "connected", "account": PAYER})

                cross_origin_request = urllib.request.Request(
                    base_url + "/api/local-session",
                    data=json.dumps({"status": "forged"}).encode(),
                    headers={"Content-Type": "application/json", "Origin": "https://example.com"},
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    urllib.request.urlopen(cross_origin_request)
                with raised.exception as error_response:
                    self.assertEqual(error_response.code, 400)

                with urllib.request.urlopen(base_url + "/actions.json") as response:
                    routes_payload = json.loads(response.read())
                self.assertEqual(routes_payload["rules"][0]["apiPath"], "/api/actions/anchor")

                request = urllib.request.Request(
                    base_url + "/api/actions/anchor",
                    data=json.dumps({"account": PAYER}).encode(),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(request) as response:
                    post_payload = json.loads(response.read())
                self.assertEqual(extract_memos(base64.b64decode(post_payload["transaction"])), [memo])

                bad_request = urllib.request.Request(
                    base_url + "/api/actions/anchor",
                    data=b"{}",
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    urllib.request.urlopen(bad_request)
                with raised.exception as error_response:
                    error_payload = json.loads(error_response.read())
                self.assertIn("message", error_payload)
                self.assertNotIn("error", error_payload)
            finally:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
