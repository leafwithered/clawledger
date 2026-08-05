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
