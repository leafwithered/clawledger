# Build log

Public showcase milestone: https://x.com/leafmyx/status/2084590054178181156

## Post 1 — problem selection

Most Solana agent submissions focus on payments, wallet monitoring, or
transaction firewalls. I am building a different ZeroClaw use case:
**ClawLedger**, a privacy-preserving durability layer for self-hosted agent
audit history.

ZeroClaw already produces structured events and ephemeral HMAC tool receipts.
ClawLedger Merkle-checkpoints the local event range and anchors only the root on
Solana—no prompts, results, or keys on-chain.

## Post 2 — custody and safety

ClawLedger is T1 by construction:

- no private-key input;
- one unsigned Memo instruction;
- wallet review is mandatory;
- log content is hashed as opaque data, never executed;
- prompt-injection strings cannot change the transaction.

## Post 3 — working evidence

The local loop now works end to end: checkpoint, recompute, single-event Merkle
proof, tamper detection, Solana Action GET/POST, and transaction decode. Seventeen
tests pass, and a live devnet RPC smoke test built a 249-byte unsigned
transaction containing the exact expected root.

## Post 4 — real ZeroClaw and fail-closed verification

The SHA-256-verified official ZeroClaw v0.8.3 binary now loads the Skill and
validates the four-step SOP. A real model turn checkpointed its own 64-event
information-level trace; an independent process and a second receipt-bearing
agent turn both reproduced root `54359c…0757f`.

The safety boundary also got stricter. Finalized verification now rejects a
transaction that contains the expected Memo plus any extra instruction, as
well as unexpected accounts, headers, or trailing bytes. The Action endpoint
was checked against the current Solana Actions metadata, CORS, routing, POST,
and error-response shapes.

Local verification now also binds every manifest leaf field, source timestamp,
and canonical Memo back to the recomputed event range instead of validating the
root alone.

This milestone was followed by the bound Telegram run, finalized devnet anchor,
and under-three-minute evidence demo documented below.

## Post 5 — real Telegram channel

A bound Telegram operator now drives the stock ZeroClaw v0.8.3 daemon end to
end. The first attempt exposed an important operational edge case: the rolling
trace changed between checkpoint and verification, so ClawLedger failed
closed. Repeating against a stable local snapshot produced a verified
200-event checkpoint with root `df25687e...4447e29`; the Telegram bot returned
the same count and root.

The Action now also advertises the Solana devnet CAIP-2 identifier and Action
v2.4 response header. The subsequent milestone finalized the exact Memo and
published the under-three-minute recording.

## Post 6 — finalized public proof

The fixed 200-event checkpoint is now finalized on Solana devnet at slot
`481112918`. The transaction contains exactly one account-free Memo
instruction, no transfer, and no account creation. ClawLedger's independent
verifier returned `valid: true` for signature
`N3mzTr1Y...PHSQviU`.

A privacy-safe 2:46 narrated evidence demo is included in the repository. It
shows the real channel result, trust boundary, finalized proof, test matrix,
and reproduction path without exposing the Telegram identity, bot token,
wallet key, or raw audit trace.
