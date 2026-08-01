from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


EVENT_DOMAIN = b"clawledger:v1:event\x00"
MAX_EVENT_BYTES = 1_000_000
MAX_EVENTS = 100_000


class EventFormatError(ValueError):
    """Raised when a ZeroClaw JSONL event cannot be checkpointed safely."""


@dataclass(frozen=True)
class EventRecord:
    position: int
    event_id: str
    timestamp: str
    payload: dict[str, Any]
    leaf_hash: bytes


def canonical_json(value: Any) -> bytes:
    """Return a deterministic UTF-8 JSON encoding.

    Canonicalization makes checkpoints independent of harmless whitespace and
    object-key ordering changes while preserving every JSON value.
    """

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def hash_event(payload: dict[str, Any]) -> bytes:
    return hashlib.sha256(EVENT_DOMAIN + canonical_json(payload)).digest()


def _record(payload: Any, position: int) -> EventRecord:
    if not isinstance(payload, dict):
        raise EventFormatError(f"line {position}: expected a JSON object")

    event_id = payload.get("id")
    timestamp = payload.get("@timestamp")
    if not isinstance(event_id, str) or not event_id.strip():
        raise EventFormatError(f"line {position}: missing non-empty string 'id'")
    if not isinstance(timestamp, str) or not timestamp.strip():
        raise EventFormatError(
            f"line {position}: missing non-empty string '@timestamp'"
        )

    return EventRecord(
        position=position,
        event_id=event_id,
        timestamp=timestamp,
        payload=payload,
        leaf_hash=hash_event(payload),
    )


def parse_jsonl(lines: Iterable[str], after_id: str | None = None) -> list[EventRecord]:
    records: list[EventRecord] = []
    seen_event_ids: set[str] = set()
    found_cursor = after_id is None

    for line_number, raw_line in enumerate(lines, start=1):
        if not raw_line.strip():
            continue
        if len(raw_line.encode("utf-8")) > MAX_EVENT_BYTES:
            raise EventFormatError(
                f"line {line_number}: event exceeds {MAX_EVENT_BYTES} bytes"
            )
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise EventFormatError(
                f"line {line_number}: invalid JSON ({exc.msg})"
            ) from exc

        record = _record(payload, line_number)
        if record.event_id in seen_event_ids:
            raise EventFormatError(f"line {line_number}: duplicate event id")
        seen_event_ids.add(record.event_id)
        if not found_cursor:
            if record.event_id == after_id:
                found_cursor = True
            continue
        records.append(record)
        if len(records) > MAX_EVENTS:
            raise EventFormatError(
                f"checkpoint exceeds {MAX_EVENTS} events; split the range"
            )

    if not found_cursor:
        raise EventFormatError(f"cursor event id not found: {after_id}")
    if not records:
        raise EventFormatError("no new events to checkpoint")
    return records


def load_jsonl(path: str | Path, after_id: str | None = None) -> list[EventRecord]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return parse_jsonl(handle, after_id=after_id)
