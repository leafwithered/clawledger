# Security policy

ClawLedger is designed for ZeroClaw custody tier T1. It creates data that a
wallet may sign; it never signs or broadcasts.

## Invariants

- No private-key, seed-phrase, keystore, or signing-key input exists.
- Only the configured JSONL file is read.
- JSON fields are data. They are never evaluated, interpolated into a command,
  or used as a path.
- Duplicate event IDs, events over 1 MB, and ranges over 100,000 events fail
  closed instead of creating ambiguous or unbounded checkpoints.
- The Action creates exactly one instruction for the canonical Solana Memo
  program.
- Finalized verification requires the same exact transaction shape: one
  signature, two expected accounts, one account-free Memo instruction, the
  exact checkpoint bytes, and no trailing data. A transaction that only
  contains the Memo alongside another instruction fails.
- The fee payer is the public key supplied by the wallet.
- The Memo payload is derived from the already-written manifest, not from the
  HTTP request body.
- HTTP request bodies are capped and malformed requests fail closed.
- Raw event content never enters the Action response or the on-chain Memo.
- Verification recomputes and compares the root, every published leaf field,
  source timestamps, and the root-derived Memo; manifest metadata cannot drift
  independently of the selected source range.

## Reporting

Please open a private GitHub security advisory. Do not include real ZeroClaw
logs, credentials, wallet secrets, or unredacted prompts in a report.
