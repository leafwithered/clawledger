# Tamper Detection Evidence

ClawLedger hashes each canonical event into a domain-separated Merkle tree.
Changing, deleting, or reordering an event changes the root and fails closed
before any wallet handoff.

The behavior is covered by the public test suite:

- `test_modified_event_is_detected`;
- `test_modified_manifest_leaf_is_detected`;
- `test_modified_manifest_memo_is_detected`;
- `test_tampered_leaf_fails`.

Reproduce the full check from a clean checkout:

```bash
export PYTHONPATH=src
python -m unittest discover -s tests -v
```

The final run reports `19 tests` passing. Raw event text is never written to
the manifest, Action response, or Solana Memo; only the Merkle root and event
count are public.

## Real three-event run

The sample trace was checkpointed, one character was changed from `200` to
`201`, and then the original trace was restored. The real CLI output was:

```text
ORIGINAL
valid: true
reason: ok
root: 7964a6898cc0e294baf7ff94dcf5dc4a4f180fdcc504172b5618dcab382a6f6b

AFTER_ONE_CHARACTER_CHANGE
valid: false
reason: event data was modified
expected_root: 7964a6898cc0e294baf7ff94dcf5dc4a4f180fdcc504172b5618dcab382a6f6b
actual_root: b54dbd175793f08e3ce3c91d2d23edc1571b43db00c847ddeedd4343068181a6
exit_code: 2

RESTORED
valid: true
reason: ok
root: 7964a6898cc0e294baf7ff94dcf5dc4a4f180fdcc504172b5618dcab382a6f6b
```
