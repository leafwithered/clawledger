import base64
import unittest
from unittest.mock import patch

from clawledger.solana import (
    MEMO_PROGRAM_ID,
    b58decode,
    b58encode,
    build_memo_transaction,
    extract_memos,
    inspect_legacy_transaction,
    transaction_base64,
    verify_anchor_signature,
)


PAYER = "11111111111111111111111111111111"
BLOCKHASH = "SysvarC1ock11111111111111111111111111111111"


class SolanaTests(unittest.TestCase):
    def test_base58_round_trip(self) -> None:
        raw = bytes(range(32))
        self.assertEqual(b58decode(b58encode(raw)), raw)
        self.assertEqual(len(b58decode(MEMO_PROGRAM_ID)), 32)

    def test_memo_transaction_round_trip(self) -> None:
        memo = "clawledger:v1:" + "ab" * 32 + ":2"
        transaction = build_memo_transaction(PAYER, BLOCKHASH, memo)
        self.assertEqual(extract_memos(transaction), [memo])
        self.assertEqual(base64.b64decode(transaction_base64(PAYER, BLOCKHASH, memo)), transaction)

    def test_invalid_payer_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_memo_transaction("bad", BLOCKHASH, "memo")

    def test_decoder_rejects_trailing_bytes(self) -> None:
        transaction = build_memo_transaction(PAYER, BLOCKHASH, "memo")
        with self.assertRaisesRegex(ValueError, "trailing"):
            inspect_legacy_transaction(transaction + b"extra")

    def test_anchor_verifier_rejects_extra_instruction(self) -> None:
        memo = "clawledger:v1:" + "ab" * 32 + ":2"
        transaction = bytearray(build_memo_transaction(PAYER, BLOCKHASH, memo))
        instruction_offset = 166
        original_instruction = transaction[instruction_offset:]
        transaction[instruction_offset - 1] = 2
        transaction.extend(original_instruction)
        rpc_result = {
            "transaction": [base64.b64encode(transaction).decode("ascii"), "base64"],
            "meta": {"err": None},
            "slot": 1,
            "blockTime": 1,
        }
        with patch("clawledger.solana.rpc_request", return_value=rpc_result):
            result = verify_anchor_signature("https://unused.invalid", "signature", memo)
        self.assertFalse(result["valid"])
        self.assertIn("one-instruction", result["reason"])

    def test_anchor_verifier_accepts_exact_transaction(self) -> None:
        memo = "clawledger:v1:" + "cd" * 32 + ":3"
        transaction = build_memo_transaction(PAYER, BLOCKHASH, memo)
        rpc_result = {
            "transaction": [base64.b64encode(transaction).decode("ascii"), "base64"],
            "meta": {"err": None},
            "slot": 42,
            "blockTime": 123,
        }
        with patch("clawledger.solana.rpc_request", return_value=rpc_result):
            result = verify_anchor_signature("https://unused.invalid", "signature", memo)
        self.assertTrue(result["valid"])
        self.assertEqual(result["slot"], 42)


if __name__ == "__main__":
    unittest.main()
