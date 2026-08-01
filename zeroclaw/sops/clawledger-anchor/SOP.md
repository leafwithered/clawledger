# ClawLedger daily anchor

Create one privacy-preserving checkpoint of the local ZeroClaw trace. Do not
read event bodies into the model and do not handle wallet secrets.

## Steps

1. **Create and verify checkpoint** — Use the clawledger skill to checkpoint only the configured JSONL trace, then recompute the root locally. Return root, count, first/last timestamp, and Memo only.
   - tools: shell
   - allow-tools: shell
   - on_failure: fail

2. **Human anchor gate** — Show the verified root, count, and Memo. Ask the operator to approve serving a wallet-signable Solana Action. Approval authorizes serving only; it never authorizes signing or broadcasting.
   - kind: checkpoint
   - requires_confirmation: true
   - next: 3

3. **Serve Action** — Start the local ClawLedger Action for the approved manifest. Tell the operator the URL and wait for a public transaction signature; never request wallet secrets.
   - tools: shell
   - allow-tools: shell
   - on_failure: fail

4. **Verify finalized anchor** — After the operator supplies a public signature, verify the exact Memo on a finalized Solana transaction. Record it only after verification succeeds.
   - tools: shell
   - allow-tools: shell
   - requires_confirmation: true
   - on_failure: fail
