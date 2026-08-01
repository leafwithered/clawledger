from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from typing import Any


BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
BASE58_INDEX = {character: index for index, character in enumerate(BASE58_ALPHABET)}
MEMO_PROGRAM_ID = "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"


def b58decode(value: str) -> bytes:
    number = 0
    for character in value:
        try:
            digit = BASE58_INDEX[character]
        except KeyError as exc:
            raise ValueError(f"invalid base58 character: {character!r}") from exc
        number = number * 58 + digit
    raw = b"" if number == 0 else number.to_bytes((number.bit_length() + 7) // 8, "big")
    leading_zeroes = len(value) - len(value.lstrip("1"))
    return b"\x00" * leading_zeroes + raw


def b58encode(value: bytes) -> str:
    leading_zeroes = len(value) - len(value.lstrip(b"\x00"))
    number = int.from_bytes(value, "big")
    encoded = ""
    while number:
        number, remainder = divmod(number, 58)
        encoded = BASE58_ALPHABET[remainder] + encoded
    return "1" * leading_zeroes + encoded


def shortvec_encode(value: int) -> bytes:
    if value < 0:
        raise ValueError("shortvec cannot encode negative values")
    output = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            byte |= 0x80
        output.append(byte)
        if not value:
            return bytes(output)


def _shortvec_decode(data: bytes, offset: int) -> tuple[int, int]:
    result = 0
    shift = 0
    while True:
        if offset >= len(data) or shift > 28:
            raise ValueError("invalid shortvec")
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, offset
        shift += 7


def _pubkey(value: str, label: str) -> bytes:
    decoded = b58decode(value)
    if len(decoded) != 32:
        raise ValueError(f"{label} must decode to 32 bytes")
    return decoded


def build_memo_transaction(payer: str, recent_blockhash: str, memo: str) -> bytes:
    """Build an unsigned legacy transaction containing exactly one Memo instruction.

    The single required signature slot is zero-filled for the wallet to replace.
    No private key is accepted by this API.
    """

    payer_key = _pubkey(payer, "payer")
    memo_program = _pubkey(MEMO_PROGRAM_ID, "Memo program id")
    blockhash = _pubkey(recent_blockhash, "recent blockhash")
    memo_bytes = memo.encode("utf-8")
    if len(memo_bytes) > 566:
        raise ValueError("memo is too large for a safe Solana transaction")

    header = bytes((1, 0, 1))
    account_keys = shortvec_encode(2) + payer_key + memo_program
    instruction = bytes((1,)) + shortvec_encode(0) + shortvec_encode(len(memo_bytes)) + memo_bytes
    message = header + account_keys + blockhash + shortvec_encode(1) + instruction
    return shortvec_encode(1) + bytes(64) + message


def transaction_base64(payer: str, recent_blockhash: str, memo: str) -> str:
    return base64.b64encode(build_memo_transaction(payer, recent_blockhash, memo)).decode("ascii")


def inspect_legacy_transaction(transaction: bytes) -> dict[str, Any]:
    """Decode the bounded legacy-transaction shape used by ClawLedger.

    Every index and length is checked, and trailing bytes are rejected so an
    on-chain verifier cannot mistake a prefixed transaction for an exact one.
    """

    signature_count, offset = _shortvec_decode(transaction, 0)
    signatures_end = offset + signature_count * 64
    if signatures_end > len(transaction):
        raise ValueError("truncated signature list")
    offset = signatures_end
    if offset + 3 > len(transaction):
        raise ValueError("truncated transaction message")
    if transaction[offset] & 0x80:
        raise ValueError("versioned transactions are not supported by this verifier")

    required_signatures = transaction[offset]
    readonly_signed = transaction[offset + 1]
    readonly_unsigned = transaction[offset + 2]
    offset += 3
    account_count, offset = _shortvec_decode(transaction, offset)
    accounts: list[str] = []
    for _ in range(account_count):
        if offset + 32 > len(transaction):
            raise ValueError("truncated account key list")
        accounts.append(b58encode(transaction[offset : offset + 32]))
        offset += 32

    if required_signatures > account_count:
        raise ValueError("required signature count exceeds account count")
    if readonly_signed > required_signatures:
        raise ValueError("read-only signed account count is invalid")
    if readonly_unsigned > account_count - required_signatures:
        raise ValueError("read-only unsigned account count is invalid")
    if offset + 32 > len(transaction):
        raise ValueError("truncated recent blockhash")
    recent_blockhash = b58encode(transaction[offset : offset + 32])
    offset += 32
    instruction_count, offset = _shortvec_decode(transaction, offset)
    instructions: list[dict[str, Any]] = []
    for _ in range(instruction_count):
        if offset >= len(transaction):
            raise ValueError("truncated instruction")
        program_index = transaction[offset]
        offset += 1
        account_indices_count, offset = _shortvec_decode(transaction, offset)
        account_indices_end = offset + account_indices_count
        if account_indices_end > len(transaction):
            raise ValueError("truncated instruction account indices")
        account_indices = list(transaction[offset:account_indices_end])
        offset = account_indices_end
        data_length, offset = _shortvec_decode(transaction, offset)
        instruction_data = transaction[offset : offset + data_length]
        if len(instruction_data) != data_length:
            raise ValueError("truncated instruction data")
        offset += data_length
        if program_index >= len(accounts):
            raise ValueError("instruction program index is out of range")
        if any(index >= len(accounts) for index in account_indices):
            raise ValueError("instruction account index is out of range")
        instructions.append(
            {
                "program_id": accounts[program_index],
                "account_indices": account_indices,
                "data": instruction_data,
            }
        )

    if offset != len(transaction):
        raise ValueError("unexpected trailing transaction bytes")

    return {
        "signature_count": signature_count,
        "required_signatures": required_signatures,
        "readonly_signed": readonly_signed,
        "readonly_unsigned": readonly_unsigned,
        "accounts": accounts,
        "recent_blockhash": recent_blockhash,
        "instructions": instructions,
    }


def extract_memos(transaction: bytes) -> list[str]:
    decoded = inspect_legacy_transaction(transaction)
    return [
        instruction["data"].decode("utf-8")
        for instruction in decoded["instructions"]
        if instruction["program_id"] == MEMO_PROGRAM_ID
    ]


def rpc_request(rpc_url: str, method: str, params: list[Any]) -> Any:
    body = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    ).encode("utf-8")
    request = urllib.request.Request(
        rpc_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    transient_statuses = {429, 500, 502, 503, 504}
    payload: dict[str, Any] | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                payload = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            if exc.code not in transient_statuses or attempt == 2:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(0.5 * (2**attempt))

    if payload is None:
        raise RuntimeError("Solana RPC returned no response")
    if "error" in payload:
        raise RuntimeError(f"Solana RPC error: {payload['error']}")
    return payload.get("result")


def get_latest_blockhash(rpc_url: str) -> str:
    result = rpc_request(rpc_url, "getLatestBlockhash", [{"commitment": "confirmed"}])
    return result["value"]["blockhash"]


def verify_anchor_signature(rpc_url: str, signature: str, expected_memo: str) -> dict[str, Any]:
    result = rpc_request(
        rpc_url,
        "getTransaction",
        [signature, {"encoding": "base64", "commitment": "finalized", "maxSupportedTransactionVersion": 0}],
    )
    if result is None:
        return {"valid": False, "reason": "transaction not found or not finalized"}
    if result.get("meta", {}).get("err") is not None:
        return {"valid": False, "reason": "transaction failed on chain"}

    try:
        encoded = result["transaction"][0]
        decoded = inspect_legacy_transaction(base64.b64decode(encoded, validate=True))
        instructions = decoded["instructions"]
        exact_shape = (
            decoded["signature_count"] == 1
            and decoded["required_signatures"] == 1
            and decoded["readonly_signed"] == 0
            and decoded["readonly_unsigned"] == 1
            and len(decoded["accounts"]) == 2
            and decoded["accounts"][1] == MEMO_PROGRAM_ID
            and len(instructions) == 1
            and instructions[0]["program_id"] == MEMO_PROGRAM_ID
            and instructions[0]["account_indices"] == []
            and instructions[0]["data"] == expected_memo.encode("utf-8")
        )
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        return {"valid": False, "reason": f"malformed transaction: {exc}"}

    if not exact_shape:
        return {
            "valid": False,
            "reason": "transaction is not the exact one-instruction ClawLedger Memo",
        }
    return {
        "valid": True,
        "reason": "ok",
        "slot": result.get("slot"),
        "block_time": result.get("blockTime"),
        "memo": expected_memo,
    }
