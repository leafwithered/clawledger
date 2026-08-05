# Bounty alignment

Checked against the live Superteam listing on 2026-08-05. The listing still
shows a 5,000 USDG pool: 1,800 first, 1,200 second, 1,000 third, and four 250
USDG bonus awards.

## Eligibility

ClawLedger is deliberately a **Tier 1** submission: stock ZeroClaw, a focused
Skill, a daily cron SOP with a human checkpoint, and a Solana Action. The
listing says correct layering is scored and that a Tier 1 solution should not
be padded into WASM. No plugin host build is required for this use case.

The daily job is concrete: create a durable timestamp for private agent audit
history, notify the operator on a real channel, and let a human optionally
anchor the commitment from a wallet. The agent never sees a signing key.

## Rubric map

| Criterion | Weight | Evidence | Final status |
|---|---:|---|---|
| Use case | 30% | Daily SOP, durable incident evidence, real ZeroClaw model run, bound Telegram run, real privacy problem | Completed: the 200-event Telegram workflow and independently reproduced root are documented in `CHANNEL_VALIDATION.md` |
| Safety | 25% | T1 custody, exact one-instruction Memo enforcement, fail-closed verification, no key input | Completed: the finalized transaction contains one account-free Memo, no transfer, and no account creation |
| Craft | 20% | Canonical JSON, domain-separated Merkle tree, proofs, Action serializer, 19 tests, stock-binary Skill/SOP validation, real tool receipt | Completed: tests, CI, strict verifier, and narrated demo are public |
| Reproducibility | 15% | Dependency-free Python, fixtures, safe config template, runbooks, operator checklist, clean-clone pass | Completed: Windows and macOS/Linux commands plus full validation scripts are included |
| Showcase | 10% | Under-three-minute English-narrated real-capture demo, architecture graphic, public Discord post, and public X post | Completed: the YouTube demo and both showcase posts are published |

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
- Skill-only plugin packaging: the optional `plugins/clawledger` bundle follows
  ZeroClaw's official `capabilities = ["skill"]` protocol shape without
  claiming that the stock v0.8.3 binary loads the optional plugin host.
- No raw key: the wallet owns signing and broadcasting. The published devnet
  signature is chain-verification evidence from a disposable signer and is not
  represented as a Phantom UI capture.
- No raw logs on-chain: only a 32-byte root and event count are public.
- No thin RPC wrapper: the value is canonicalization, Merkle proofs, privacy,
  human approval, and independent finalized-transaction verification.

## Deadline

The listing deadline is `2026-08-07T02:59:59Z`, which is **2026-08-07 10:59
Asia/Shanghai**. Winner announcement is scheduled for 2026-08-21.
