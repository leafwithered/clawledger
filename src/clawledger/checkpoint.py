from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canonical import EventRecord, load_jsonl
from .merkle import merkle_proof, merkle_root, verify_proof


SCHEMA = "clawledger.checkpoint/v1"
MEMO_PREFIX = "clawledger:v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def anchor_memo(root_hex: str, count: int) -> str:
    memo = f"{MEMO_PREFIX}:{root_hex}:{count}"
    if len(memo.encode("utf-8")) > 200:
        raise ValueError("anchor memo unexpectedly exceeds the safe size budget")
    return memo


def build_manifest(
    records: list[EventRecord],
    source_name: str,
    network: str = "devnet",
) -> dict[str, Any]:
    if not records:
        raise ValueError("no records supplied")

    leaves = [record.leaf_hash for record in records]
    root_hex = merkle_root(leaves).hex()
    return {
        "schema": SCHEMA,
        "created_at": _utc_now(),
        "source": {
            "name": Path(source_name).name,
            "event_count": len(records),
            "first_event_id": records[0].event_id,
            "last_event_id": records[-1].event_id,
            "first_timestamp": records[0].timestamp,
            "last_timestamp": records[-1].timestamp,
        },
        "merkle": {
            "algorithm": "sha256-domain-separated-duplicate-last",
            "root": root_hex,
            "leaves": [
                {
                    "index": index,
                    "event_id": record.event_id,
                    "timestamp": record.timestamp,
                    "hash": record.leaf_hash.hex(),
                }
                for index, record in enumerate(records)
            ],
        },
        "anchor": {
            "network": network,
            "memo": anchor_memo(root_hex, len(records)),
            "signature": None,
        },
        "privacy": {
            "raw_events_in_manifest": False,
            "onchain_data": "root,count only",
        },
    }


def checkpoint_file(
    input_path: str | Path,
    output_path: str | Path,
    *,
    after_id: str | None = None,
    network: str = "devnet",
) -> dict[str, Any]:
    records = load_jsonl(input_path, after_id=after_id)
    manifest = build_manifest(records, str(input_path), network=network)
    Path(output_path).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def load_manifest(path: str | Path) -> dict[str, Any]:
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA:
        raise ValueError("unsupported checkpoint manifest schema")
    return manifest


def verify_manifest(input_path: str | Path, manifest: dict[str, Any]) -> dict[str, Any]:
    try:
        source = manifest["source"]
        merkle = manifest["merkle"]
        anchor = manifest["anchor"]
        first_id = source["first_event_id"]
        last_id = source["last_event_id"]
        expected_count = int(source["event_count"])
        expected_root = merkle["root"]
        if not isinstance(first_id, str) or not isinstance(last_id, str):
            raise ValueError("event boundary IDs must be strings")
        if expected_count <= 0:
            raise ValueError("event count must be positive")
        if not isinstance(expected_root, str) or len(expected_root) != 64:
            raise ValueError("Merkle root must be 32-byte hex")
        bytes.fromhex(expected_root)
        if merkle.get("algorithm") != "sha256-domain-separated-duplicate-last":
            raise ValueError("unsupported Merkle algorithm")
        if anchor.get("memo") != anchor_memo(expected_root, expected_count):
            raise ValueError("anchor Memo does not match root and event count")
    except (KeyError, TypeError, ValueError) as exc:
        return {"valid": False, "reason": f"invalid manifest: {exc}"}

    records = load_jsonl(input_path)

    selected: list[EventRecord] = []
    active = False
    for record in records:
        if record.event_id == first_id:
            active = True
        if active:
            selected.append(record)
        if active and record.event_id == last_id:
            break

    if len(selected) != expected_count or not selected or selected[-1].event_id != last_id:
        return {
            "valid": False,
            "reason": "checkpoint event range is missing or reordered",
        }

    actual_root = merkle_root(record.leaf_hash for record in selected).hex()
    if actual_root != expected_root:
        return {
            "valid": False,
            "reason": "event data was modified",
            "expected_root": expected_root,
            "actual_root": actual_root,
            "event_count": len(selected),
        }

    expected_leaves = [
        {
            "index": index,
            "event_id": record.event_id,
            "timestamp": record.timestamp,
            "hash": record.leaf_hash.hex(),
        }
        for index, record in enumerate(selected)
    ]
    expected_source_metadata = {
        "first_timestamp": selected[0].timestamp,
        "last_timestamp": selected[-1].timestamp,
    }
    if manifest["merkle"].get("leaves") != expected_leaves:
        return {"valid": False, "reason": "manifest leaf metadata was modified"}
    if any(source.get(key) != value for key, value in expected_source_metadata.items()):
        return {"valid": False, "reason": "manifest source metadata was modified"}

    return {
        "valid": True,
        "reason": "ok",
        "expected_root": expected_root,
        "actual_root": actual_root,
        "event_count": len(selected),
    }


def event_proof(manifest: dict[str, Any], event_id: str) -> dict[str, Any]:
    leaves = manifest["merkle"]["leaves"]
    for leaf in leaves:
        if leaf["event_id"] == event_id:
            index = int(leaf["index"])
            hashes = [bytes.fromhex(item["hash"]) for item in leaves]
            proof = merkle_proof(hashes, index)
            return {
                "schema": "clawledger.proof/v1",
                "event_id": event_id,
                "leaf_hash": leaf["hash"],
                "root": manifest["merkle"]["root"],
                "proof": [step.__dict__ for step in proof],
                "valid": verify_proof(
                    bytes.fromhex(leaf["hash"]),
                    proof,
                    bytes.fromhex(manifest["merkle"]["root"]),
                ),
            }
    raise KeyError(f"event id not present in checkpoint: {event_id}")


def apply_anchor_signature(
    manifest: dict[str, Any], signature: str, output_path: str | Path
) -> dict[str, Any]:
    if not signature or any(character.isspace() for character in signature):
        raise ValueError("signature must be a non-empty base58 string")
    manifest["anchor"]["signature"] = signature
    Path(output_path).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest
