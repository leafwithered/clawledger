# Three-minute demo runbook

The demo uses a real ZeroClaw trace, a real Telegram or Discord turn, and a
wallet-signed Solana devnet Memo. No slides are used. The preferred story is a
nightly operational control: the agent reports that yesterday's private audit
history has been checkpointed and asks whether the operator wants to anchor it.

## 0:00–0:25 — The problem

Show ZeroClaw's Logs page and the local `runtime-trace.jsonl` path.

Say: "ZeroClaw tool receipts stop an LLM fabricating successful tool results,
but the keys are intentionally ephemeral and durable receipt storage is still
planned. An operator needs a public proof that yesterday's local history did
not change."

## 0:25–0:55 — Real agent action

From a phone, ask the ZeroClaw agent: "Checkpoint today's audit history and
tell me only the event count and root." Show the channel reply, resulting tool
event, and receipt block. Do not reveal secrets or full prompts.

## 0:55–1:25 — Local checkpoint

Run:

```text
python -m clawledger checkpoint --input <trace> --output checkpoint.json
python -m clawledger verify --input <trace> --manifest checkpoint.json
```

Point out the event count, Merkle root, and the fact that no raw event appears
in the manifest's leaf list or Memo.

## 1:25–1:55 — Human approval and Solana

Open the Action, connect a devnet wallet, and show the wallet preview. Emphasize
that the service receives only the public address and the transaction contains
one Memo instruction—no transfer and no agent-held key. Sign and broadcast.

## 1:55–2:25 — Independent verification

Run `verify-anchor` with the signature. Open the transaction in Solana Explorer
and match the Memo root. Generate an inclusion proof for one event.

## 2:25–2:50 — Tamper demonstration

Copy the trace, change one `event.outcome` value, and run `verify` again. Show
`event data was modified` and the mismatched root.

## 2:50–3:00 — Reproduce

Show the repository tree, `python -m unittest discover -s tests -v`, and the
ZeroClaw Skill/SOP. End with: "One Python process, no dependencies, no private
keys, and another operator can reproduce it in an evening."

## Capture checklist

- Use devnet and a disposable wallet.
- Show the real phone channel; do not substitute the CLI in the final cut.
- Hide RPC keys, bearer tokens, local usernames, and unrelated event content.
- Keep the terminal font large enough to read.
- Show the Solana signature and repository URL on screen.
- Keep the final cut below three minutes.
