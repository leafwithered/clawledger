from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .checkpoint import (
    apply_anchor_signature,
    checkpoint_file,
    event_proof,
    load_manifest,
    verify_manifest,
)
from .server import serve
from .solana import transaction_base64, verify_anchor_signature


DEFAULT_DEVNET_RPC = "https://api.devnet.solana.com"


def _print(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="clawledger",
        description="Create and anchor tamper-evident ZeroClaw audit checkpoints.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    checkpoint = subparsers.add_parser("checkpoint", help="Hash a JSONL event range")
    checkpoint.add_argument("--input", required=True)
    checkpoint.add_argument("--output", required=True)
    checkpoint.add_argument("--after-id")
    checkpoint.add_argument("--network", default="devnet")

    verify = subparsers.add_parser("verify", help="Recompute and verify a checkpoint")
    verify.add_argument("--input", required=True)
    verify.add_argument("--manifest", required=True)

    proof = subparsers.add_parser("proof", help="Generate a Merkle inclusion proof")
    proof.add_argument("--manifest", required=True)
    proof.add_argument("--event-id", required=True)

    build = subparsers.add_parser("build-transaction", help="Build an unsigned Memo transaction")
    build.add_argument("--manifest", required=True)
    build.add_argument("--payer", required=True)
    build.add_argument("--blockhash", required=True)

    action = subparsers.add_parser("serve-action", help="Serve the wallet-signable Solana Action")
    action.add_argument("--manifest", required=True)
    action.add_argument("--rpc", default=DEFAULT_DEVNET_RPC)
    action.add_argument("--host", default="127.0.0.1")
    action.add_argument("--port", type=int, default=8787)

    verify_anchor = subparsers.add_parser("verify-anchor", help="Verify the on-chain Memo")
    verify_anchor.add_argument("--manifest", required=True)
    verify_anchor.add_argument("--signature", required=True)
    verify_anchor.add_argument("--rpc", default=DEFAULT_DEVNET_RPC)
    verify_anchor.add_argument("--write-signature", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "checkpoint":
            manifest = checkpoint_file(
                args.input,
                args.output,
                after_id=args.after_id,
                network=args.network,
            )
            _print(
                {
                    "ok": True,
                    "manifest": str(Path(args.output).resolve()),
                    "event_count": manifest["source"]["event_count"],
                    "root": manifest["merkle"]["root"],
                    "memo": manifest["anchor"]["memo"],
                }
            )
            return 0

        if args.command == "verify":
            result = verify_manifest(args.input, load_manifest(args.manifest))
            _print(result)
            return 0 if result["valid"] else 2

        if args.command == "proof":
            _print(event_proof(load_manifest(args.manifest), args.event_id))
            return 0

        if args.command == "build-transaction":
            manifest = load_manifest(args.manifest)
            _print(
                {
                    "transaction": transaction_base64(
                        args.payer, args.blockhash, manifest["anchor"]["memo"]
                    ),
                    "memo": manifest["anchor"]["memo"],
                    "custody": "T1: unsigned; wallet signature required",
                }
            )
            return 0

        if args.command == "serve-action":
            serve(args.manifest, args.rpc, args.host, args.port)
            return 0

        if args.command == "verify-anchor":
            manifest = load_manifest(args.manifest)
            result = verify_anchor_signature(
                args.rpc, args.signature, manifest["anchor"]["memo"]
            )
            if result["valid"] and args.write_signature:
                apply_anchor_signature(manifest, args.signature, args.manifest)
                result["manifest_updated"] = True
            _print(result)
            return 0 if result["valid"] else 2
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    return 1
