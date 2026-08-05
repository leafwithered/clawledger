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
- fail-closed local transaction guard and Phantom handoff page with a pinned,
  vendored browser dependency;
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
detects later modification, deletion, or reordering. The published devnet
signature is chain-verification evidence from a disposable devnet signer, not
a claim of Phantom UI approval; the Action remains unsigned until an operator
reviews it in Phantom.

## Reproduction

Python 3.11+, ZeroClaw stock release, and a disposable devnet wallet. No plugin
host, Rust compiler, database, Docker, or paid RPC is required.

Operator package:

- [safe ZeroClaw config](../zeroclaw/config.example.toml);
- [daily SOP](../zeroclaw/sops/clawledger-anchor/SOP.md);
- [reviewed Skill](../zeroclaw/skills/clawledger/SKILL.md);
- [official-protocol skill-only bundle](../plugins/clawledger/README.md);
- [official ZeroClaw Skill installation evidence](SKILL_INSTALLATION_EVIDENCE.md);
- [tamper detection evidence](TAMPER_DETECTION.md);
- [threat model](THREAT_MODEL.md);
- [cross-platform validation commands](VALIDATION.md).

## Final submission links

- Repository: `https://github.com/leafwithered/clawledger`
- 90-second judge guide: `https://github.com/leafwithered/clawledger/blob/main/JUDGE.md`
- Final successful CI validation: `https://github.com/leafwithered/clawledger/actions/runs/30972885165`
- Demo video: `https://youtu.be/CfBIr49QbJI`
  (GitHub backup: `https://github.com/leafwithered/clawledger/blob/main/docs/clawledger-demo.mp4`)
- Devnet anchor: `https://explorer.solana.com/tx/N3mzTr1YAWw84b2irzd9Cr4cmPd9JHZSmZaUq3PPTr9xYPLfbJZZEqCMP417164U6exTiBA9kjXZ7pf4PHSQviU?cluster=devnet`
- X showcase: `https://x.com/leafmyx/status/2084590054178181156`
- ZeroClaw Discord showcase: `https://discord.com/channels/1472154792351760419/1527427886410109029/1534230225951523038`
- Fixed release: `https://github.com/leafwithered/clawledger/releases/tag/v0.1.3-bounty-submission`
- Python wheel: `https://github.com/leafwithered/clawledger/releases/download/v0.1.3-bounty-submission/clawledger-0.1.3-py3-none-any.whl`
- Downloadable ZIP: `https://github.com/leafwithered/clawledger/releases/download/v0.1.3-bounty-submission/clawledger-v0.1.3-bounty-submission.zip`
- SHA-256 checksums: `https://github.com/leafwithered/clawledger/releases/download/v0.1.3-bounty-submission/SHA256SUMS`
