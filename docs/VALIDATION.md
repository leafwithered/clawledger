# Validation evidence

Validation date: 2026-08-01 (Asia/Shanghai)

## Automated tests

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

Result: **17 passed**.

Covered properties:

- checkpoint/recompute round trip;
- duplicate event-ID rejection;
- modified event detection;
- modified manifest leaf and root-derived Memo detection;
- untrusted event text never copied to the manifest;
- valid inclusion proofs for odd leaf counts;
- tampered inclusion proof rejection;
- base58 round trip and key-length enforcement;
- Solana Memo transaction encode/decode round trip;
- invalid public key rejection;
- strict finalized-anchor acceptance for the exact one-instruction Memo;
- rejection of extra instructions and trailing transaction bytes;
- Action descriptor and unsigned POST transaction flow.
- current Solana Actions metadata, route manifest, CORS, and `ActionError`
  response shape.

## Sample checkpoint

Input: `fixtures/runtime-trace.sample.jsonl` (3 schema-v2 events)

```text
root   = 7964a6898cc0e294baf7ff94dcf5dc4a4f180fdcc504172b5618dcab382a6f6b
memo   = clawledger:v1:7964a6898cc0e294baf7ff94dcf5dc4a4f180fdcc504172b5618dcab382a6f6b:3
verify = valid
```

## Live Solana devnet RPC smoke test

```powershell
$env:PYTHONPATH = "src"
python scripts/live_action_smoke.py
```

Observed result:

```json
{
  "ok": true,
  "rpc": "https://api.devnet.solana.com",
  "transaction_bytes": 249,
  "memo": "clawledger:v1:7964a6898cc0e294baf7ff94dcf5dc4a4f180fdcc504172b5618dcab382a6f6b:3",
  "signed": false,
  "broadcast": false
}
```

This exercised a real `getLatestBlockhash` call and decoded the constructed
transaction back to the exact manifest Memo. It did not sign, broadcast, spend
funds, or mutate chain state. Read-only RPC calls retry a small bounded set of
transient HTTP failures so a brief public-devnet 429/5xx does not make clean
reproduction flaky.

## ZeroClaw compatibility boundary

The Skill frontmatter, log schema, default trace path, observability config,
tool receipt behavior, SOP trigger fields, and cron expression field were
checked against `zeroclaw-labs/zeroclaw` current official documentation/source.

The official v0.8.3 Windows archive was downloaded from the ZeroClaw GitHub
release. Its SHA-256 matched the published `SHA256SUMS` value:

```text
00da56062ff3f96f7dae20d9cc471e8e63e569dabffea6fda45793f5728a4db5
```

Observed stock-binary results:

```text
zeroclaw 0.8.3
Skill installed and audited successfully (4 files scanned)
clawledger-anchor — valid
Mode: supervised  Steps: 4  Triggers: cron:0 5 0 * * *, manual
```

`zeroclaw sop graph clawledger-anchor` produced the expected linear flow:
checkpoint and verify -> human gate -> serve Action -> verify finalized anchor.

## Real ZeroClaw agent and tool receipt

The official binary loaded the ClawLedger Skill in a supervised,
workspace-only agent and used a real model turn to checkpoint its own
information-level runtime trace. A separate process and a second agent turn
both verified the same 64-event checkpoint:

```text
valid         = true
reason        = ok
expected_root = 54359cb618358a6bf58c32d20dc5ccffa52f405f4539485521e2936851e0757f
actual_root   = 54359cb618358a6bf58c32d20dc5ccffa52f405f4539485521e2936851e0757f
event_count   = 64
```

The second turn returned the shell result through ZeroClaw's enabled tool
receipt path. See `docs/REAL_RUNTIME_VALIDATION.md`; raw traces and local auth
remain ignored.

## Remaining proof before submission

- Produce one operator-signed devnet Memo.
- Verify the finalized signature with `clawledger verify-anchor`.
- Connect Telegram or Discord and record the three-minute real-channel demo.

## Visual artifact check

`docs/architecture.svg` was rendered headlessly at 1200 x 520 and inspected.
The checked render is committed as `docs/architecture.png` for README and
submission use.
