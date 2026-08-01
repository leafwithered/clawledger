# Submission draft

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
- finalized on-chain Memo verifier;
- tests, threat model, ZeroClaw Skill, SOP, and three-minute runbook.

## Custody and trust

T1. The service never accepts a private key and never signs or broadcasts. The
wallet reviews a transaction containing one Memo instruction. Local ZeroClaw
and the filesystem are trusted before checkpoint creation; the Solana anchor
detects later modification, deletion, or reordering.

## Reproduction

Python 3.11+, ZeroClaw stock release, and a disposable devnet wallet. No plugin
host, Rust compiler, database, Docker, or paid RPC is required.

## Links to complete before posting

- Repository: `https://github.com/leafwithered/clawledger`
- Demo video: `<VIDEO_URL>`
- Devnet anchor: `<SOLANA_EXPLORER_URL>`
- Build-in-public log: `<X_POST_URL>`
