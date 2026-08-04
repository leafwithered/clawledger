# Final submission brief

## What it does

ClawLedger gives a self-hosted ZeroClaw operator a durable public timestamp for
private agent activity. It checkpoints ZeroClaw's structured JSONL events into
a SHA-256 Merkle root and asks the operator's wallet—not the agent—to anchor the
root through Solana's Memo program.

## Who it is for

Teams running autonomous agents for infrastructure, finance, customer support,
or compliance who need to prove that a historical action record was not edited
after an incident.

## ZeroClaw features used

- structured rotating observability logs;
- tool receipts as in-scope execution evidence;
- a ZeroClaw Skill for the operator flow;
- SOP scheduling and a human approval checkpoint;
- built-in shell execution with a narrow command surface.

## What was built

- dependency-free Python checkpoint/proof verifier;
- domain-separated Merkle tree and event inclusion proofs;
- pure-Python Solana legacy transaction serializer and decoder;
- wallet-signable Solana Action;
- fail-closed local Phantom signer with a pinned, vendored browser dependency;
- finalized on-chain Memo verifier;
- tests, threat model, ZeroClaw Skill, SOP, and three-minute runbook.

## Live evidence

A real Telegram message reached an official ZeroClaw v0.8.3 daemon, invoked the
reviewed ClawLedger Skill, and returned a stable 200-event checkpoint. The
published root is
`df25687ed19a6ec87a4ee025ce8d0d9b03e4809d6257a215865e0f17a4447e29`;
an independent local CLI verification returned `valid: true`. Tokens, account
identifiers, and raw log contents are deliberately excluded.

## Custody and trust

T1. The service never accepts a private key and never signs or broadcasts. The
wallet reviews a transaction containing one Memo instruction. Local ZeroClaw
and the filesystem are trusted before checkpoint creation; the Solana anchor
detects later modification, deletion, or reordering.

## Reproduction

Python 3.11+, ZeroClaw stock release, and a disposable devnet wallet. No plugin
host, Rust compiler, database, Docker, or paid RPC is required.

## Final submission links

- Repository: `https://github.com/leafwithered/clawledger`
- Demo video: `https://github.com/leafwithered/clawledger/blob/main/docs/clawledger-demo.mp4`
- Devnet anchor: `https://explorer.solana.com/tx/N3mzTr1YAWw84b2irzd9Cr4cmPd9JHZSmZaUq3PPTr9xYPLfbJZZEqCMP417164U6exTiBA9kjXZ7pf4PHSQviU?cluster=devnet`
- Showcase posts: add the published ZeroClaw Discord and X URLs before the
  Superteam form is submitted.
