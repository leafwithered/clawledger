# Build-in-public log draft

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

Next: one operator-signed devnet anchor and the real three-minute phone-channel
demo.
