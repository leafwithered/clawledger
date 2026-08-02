# Bounty alignment

Checked against the live Superteam listing on 2026-08-01.

## Eligibility

ClawLedger is deliberately a **Tier 1** submission: stock ZeroClaw, a focused
Skill, a daily cron SOP with a human checkpoint, and a Solana Action. The
listing says correct layering is scored and that a Tier 1 solution should not
be padded into WASM. No plugin host build is required for this use case.

The daily job is concrete: create a durable timestamp for private agent audit
history, notify the operator on a real channel, and let a human optionally
anchor the commitment from a wallet. The agent never sees a signing key.

## Rubric map

| Criterion | Weight | Evidence | Remaining gap |
|---|---:|---|---|
| Use case | 30% | Daily SOP, durable incident evidence, real ZeroClaw model run, bound Telegram run, real privacy problem | Show the recurring workflow in the final recording |
| Safety | 25% | T1 custody, exact one-instruction Memo enforcement, fail-closed verification, no key input | Capture wallet preview and finalized devnet signature |
| Craft | 20% | Canonical JSON, domain-separated Merkle tree, proofs, Action serializer, 17 tests, stock-binary Skill/SOP validation, real tool receipt | Capture the validation output in the demo |
| Reproducibility | 15% | Dependency-free Python, fixtures, safe config template, runbooks, operator checklist, clean-clone pass | Capture the clean-clone result in the final recording |
| Showcase | 10% | Three-minute no-slides script and architecture graphic | Record phone + terminal video |

## Required submission artifacts

1. A real ZeroClaw agent on a real channel doing the job.
2. A public GitHub repository.
3. A video no longer than three minutes.
4. A write-up covering user, ZeroClaw features, custody tier, threat model,
   configuration, SOP, Skill, and reproduction.
5. A showcase post in ZeroClaw Discord `#solana-bounty`.
6. Superteam links for the demo and supporting material.

## Scope decisions

- No WASM: deterministic local hashing and a wallet-signable Action already fit
  the stock release; extra plugin code would be unnecessary layering.
- No raw key: the wallet owns signing and broadcasting.
- No raw logs on-chain: only a 32-byte root and event count are public.
- No thin RPC wrapper: the value is canonicalization, Merkle proofs, privacy,
  human approval, and independent finalized-transaction verification.

## Deadline

The listing deadline is `2026-08-07T02:59:59Z`, which is **2026-08-07 10:59
Asia/Shanghai**. Winner announcement is scheduled for 2026-08-21.
