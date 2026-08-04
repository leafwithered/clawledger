# Showcase copy

Use this reviewed copy for the public ZeroClaw Discord and X posts. Never
include a bot token, wallet recovery phrase, raw ZeroClaw trace, model
credential, or operator identifier.

## ZeroClaw Discord `#solana-bounty`

**ClawLedger — tamper-evident private agent audit history**

ClawLedger turns ZeroClaw's rotating local JSONL audit events into a canonical
SHA-256 Merkle checkpoint, then asks a human wallet to anchor only the root and
event count through Solana's Memo program. Raw prompts, logs, tool arguments,
and wallet keys remain local.

The demo uses stock ZeroClaw v0.8.3, a real Telegram channel, a reviewed Skill,
a daily SOP, a fail-closed local Phantom signer, and an independent finalized
transaction verifier. The real run covers 200 events with root
`df25687ed19a6ec87a4ee025ce8d0d9b03e4809d6257a215865e0f17a4447e29`.

- Repository: https://github.com/leafwithered/clawledger
- Demo: https://youtu.be/CfBIr49QbJI
- Devnet anchor: https://explorer.solana.com/tx/N3mzTr1YAWw84b2irzd9Cr4cmPd9JHZSmZaUq3PPTr9xYPLfbJZZEqCMP417164U6exTiBA9kjXZ7pf4PHSQviU?cluster=devnet
- Architecture and threat model: repository `docs/`

Custody tier: **T1**. The agent can construct but cannot sign or broadcast.
The published devnet signature is chain-verification evidence from a disposable
signer; it is not presented as a Phantom UI capture. The Action remains
unsigned until an operator reviews it in Phantom.

## X post

Built ClawLedger for the ZeroClaw × Solana bounty: a privacy-preserving audit
checkpoint for autonomous agents.

Real Telegram → stock ZeroClaw → canonical Merkle root → human-reviewed Solana
Memo. No raw logs on-chain. No agent-held wallet key. Exact-transaction
verification fails closed.

Repo: https://github.com/leafwithered/clawledger
Demo: https://youtu.be/CfBIr49QbJI
Devnet: https://explorer.solana.com/tx/N3mzTr1YAWw84b2irzd9Cr4cmPd9JHZSmZaUq3PPTr9xYPLfbJZZEqCMP417164U6exTiBA9kjXZ7pf4PHSQviU?cluster=devnet

## Superteam short description

ClawLedger gives self-hosted ZeroClaw operators durable public evidence that a
private agent audit history was not edited after an incident. A reviewed Skill
canonicalizes rotating JSONL events into a domain-separated Merkle tree. A
local Phantom signer independently decodes the unsigned transaction and opens
the wallet only when it contains the expected signer and exactly one
account-free Memo instruction. A separate verifier checks the finalized devnet
transaction against the local event range. The submission includes a real
Telegram-driven 200-event run, daily SOP, threat model, tests, and a
three-minute reproduction path.

## Superteam links

- Repository: https://github.com/leafwithered/clawledger
- Pull request: https://github.com/leafwithered/clawledger/pull/1
- Demo: https://youtu.be/CfBIr49QbJI
- Devnet Explorer: https://explorer.solana.com/tx/N3mzTr1YAWw84b2irzd9Cr4cmPd9JHZSmZaUq3PPTr9xYPLfbJZZEqCMP417164U6exTiBA9kjXZ7pf4PHSQviU?cluster=devnet
- X showcase: https://x.com/leafmyx/status/2084590054178181156
- ZeroClaw Discord showcase: https://discord.com/channels/1472154792351760419/1527427886410109029/1534230225951523038
- Fixed release: https://github.com/leafwithered/clawledger/releases/tag/v0.1.2-bounty-submission
