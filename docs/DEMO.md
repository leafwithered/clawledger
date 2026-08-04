# Three-minute demo runbook

The committed `docs/clawledger-demo.mp4` is a 2:46 English-narrated
real-capture cut. It uses the real Telegram window and the real ZeroClaw
validation terminal; it contains no slide deck and no private channel trace.
The cut shows the 200-event response, stock ZeroClaw v0.8.3, Skill/SOP audit,
local `valid: true`, the finalized Memo verifier, and the test run.

Public video: https://youtu.be/CfBIr49QbJI

Repository backup: `docs/clawledger-demo.mp4`

The published signature is chain-verification evidence from a disposable
devnet signer. The video does not claim that this signature was approved in a
Phantom UI. The local Action is unsigned and the operator remains the only
component allowed to review and sign it.

## Recorded sequence

- **0:00-0:45:** Real Telegram conversation with the stable 200-event reply,
  Merkle root, and post-rotation health response.
- **0:45-1:15:** Stock ZeroClaw v0.8.3, Skill audit, and SOP validation.
- **1:15-1:55:** Independent local checkpoint verification with `valid: true`,
  matching root, and `event_count: 200`.
- **1:55-2:20:** Finalized Solana devnet Memo verification, slot, Memo text,
  and explicit no-transfer/no-account-creation checks.
- **2:20-2:46:** Tamper/transaction-shape test matrix and the reproducibility
  command path.

## Reproduce the live flow

```text
python -m clawledger checkpoint --input <trace> --output checkpoint.json
python -m clawledger verify --input <trace> --manifest checkpoint.json
python -m clawledger verify-anchor --manifest checkpoint.json --signature <DEVNET_SIGNATURE>
python -m unittest discover -s tests -v
```

For an operator wallet review, serve the unsigned Action, inspect the exact
one-instruction Memo in Phantom on devnet, and approve it only after the
preview matches `docs/ANCHOR_HANDOFF.md`. Never paste a recovery phrase or
private key into the project.

## Capture checklist

- Use devnet and a disposable wallet.
- Show the real Telegram channel; do not substitute a slide deck or a mock
  transcript in the final cut.
- Hide RPC keys, bearer tokens, local usernames, and unrelated event content.
- Keep the terminal font large enough to read.
- Show the public Solana signature and repository URL on screen.
- Keep the final cut below three minutes.
