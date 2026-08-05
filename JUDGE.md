# Judge ClawLedger in 90 seconds

## One sentence

ClawLedger lets a real ZeroClaw agent checkpoint private audit history and
anchor only a Merkle root and event count on Solana.

## Fast path

1. Watch the [2:46 real-capture demo](https://youtu.be/CfBIr49QbJI).
2. Open the [finalized Devnet Memo](https://explorer.solana.com/tx/N3mzTr1YAWw84b2irzd9Cr4cmPd9JHZSmZaUq3PPTr9xYPLfbJZZEqCMP417164U6exTiBA9kjXZ7pf4PHSQviU?cluster=devnet).
3. Read the [real Telegram validation](docs/CHANNEL_VALIDATION.md).
4. Run the [successful CI job](https://github.com/leafwithered/clawledger/actions/runs/30930440544).

The final head also provides a manual `submission-validation` workflow covering
wheel build/install, installed-CLI reproduction, public Devnet construction,
and a tracked-file secret scan.

## Why this is ZeroClaw

- Stock ZeroClaw v0.8.3 runtime trace and tool receipts;
- a reviewed ClawLedger Skill and daily human-gated SOP;
- a real Telegram channel run covering 200 events;
- built-in shell used through a fixed, audited wrapper.

## Why this is Solana

Solana Memo provides a cheap public timestamp. Only the SHA-256 Merkle root and
event count leave the operator's machine. A local Action creates an unsigned
transaction, and the human wallet owns review, signing, and broadcasting.

## Three safety guarantees

- No private-key input or agent-held signing secret;
- one allowlisted account-free Memo instruction, checked before wallet review;
- raw prompts, results, identifiers, and trace content never go on-chain.

## Plugin scope, stated precisely

The bounty explicitly lists “Tier 1 — Stock release, zero plugins” as a valid
path and judges working use cases rather than standalone components. ClawLedger
therefore uses the correct T1 composition: stock ZeroClaw + Skill + SOP + local
Python verifier + Solana Action. The repository also includes the official
protocol-shaped [skill-only bundle](plugins/clawledger), declared as
`capabilities = ["skill"]` with no WASM and no permissions. The stock v0.8.3
Windows release does not expose the optional `plugin` command, so the bundle is
documented for plugin-enabled source builds without misrepresenting the stock
runtime evidence.

## Reproduce

```bash
git clone https://github.com/leafwithered/clawledger.git
cd clawledger
export PYTHONPATH=src
python -m clawledger checkpoint --input fixtures/runtime-trace.sample.jsonl --output checkpoint.json
python -m clawledger verify --input fixtures/runtime-trace.sample.jsonl --manifest checkpoint.json
python -m unittest discover -s tests -v
```

Full evidence and operator setup are in [SUBMISSION.md](docs/SUBMISSION.md) and
[VALIDATION.md](docs/VALIDATION.md).
