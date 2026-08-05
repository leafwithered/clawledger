# Validation evidence

Last validated: 2026-08-05 (Asia/Shanghai)

On 2026-08-02, public commit `ac8e0d442cbd85b8a2e438812373f77ca0065f50`
was fetched through a new shallow clone from
`https://github.com/leafwithered/clawledger`. The complete validation command
passed from that clone, including the 17 tests present at that historical
commit, live devnet RPC smoke test,
official ZeroClaw Skill audit, and SOP validation.

The final submission head adds the protocol-shaped skill-only bundle and two
structure tests; the current suite passes **19 tests**.

GitHub Actions also runs the dependency-free test suite on Python 3.11 and
3.14. Third-party Actions are pinned to immutable commit SHAs.

The manual `submission-validation` workflow additionally builds and installs
the wheel, reproduces checkpoint creation and verification through the
installed CLI, runs the read-only public Devnet smoke test, and scans tracked
files for secret-shaped values. It never signs or broadcasts.

Workflow: https://github.com/leafwithered/clawledger/actions/workflows/submission-validation.yml

## Automated tests

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

Result: **19 passed** on the final submission head.

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
- Action descriptor and unsigned POST transaction flow;
- current Solana Actions metadata, route manifest, CORS, and `ActionError`
  response shape;
- Solana devnet CAIP-2 and Action v2.4 response headers.

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

## Real Telegram channel

A bound Telegram operator drove the official ZeroClaw daemon through the
reviewed Skill. The stable run covered 200 events and returned root
`df25687ed19a6ec87a4ee025ce8d0d9b03e4809d6257a215865e0f17a4447e29`.
An independent CLI verification returned `valid: true`. A post-rotation health
message also completed end to end. See `docs/CHANNEL_VALIDATION.md`.

## Final public-branch reproducibility check

On 2026-08-04, a fresh clone of the public `main` branch
passed `scripts/validate_all.ps1` with the official ZeroClaw v0.8.3 Windows
binary. The run compiled the Python sources, passed all 17 unit tests, completed
the live Solana devnet RPC smoke test without signing or broadcasting, passed
the ZeroClaw Skill audit, and validated the `clawledger-anchor` SOP.

A submission-tree scan excluding `.git/` and ignored local runtime artifacts
found no Telegram-token, OpenAI-key, PEM-private-key, recovery-phrase, or
serialized-private-key patterns. The devnet signature and Explorer URL are
recorded in `docs/FINALIZED_ANCHOR.json`. The 2:46 English-narrated
real-capture video is published at https://youtu.be/CfBIr49QbJI, with
`docs/clawledger-demo.mp4` retained as the repository backup. The public X
showcase is https://x.com/leafmyx/status/2084590054178181156.

The final 200-event manifest was re-verified immediately before the wallet
handoff. A live unsigned Action response decoded to one required signature and
exactly one account-free instruction for Solana's Memo program, containing the
fixed `clawledger:v1:df25687e...:200` Memo. The published chain signature was
broadcast by a disposable devnet signer for verification; no Phantom UI capture
was recorded and no wallet secret was committed.

## Finalized proof and submission status

The 200-event Memo finalized at slot `481112918`. `clawledger verify-anchor`
returned `valid: true`, confirmed the exact Memo, and recorded the public
signature in the local manifest. A 2:46 English-narrated real-capture demo is
included in the repository. The technical evidence and public showcases are
complete. The ZeroClaw Discord `#solana-bounty` post is published at
https://discord.com/channels/1472154792351760419/1527427886410109029/1534230225951523038.

## Visual artifact check

`docs/architecture.svg` was rendered headlessly at 1200 x 520 and inspected.
The checked render is committed as `docs/architecture.png` for README and
submission use.
