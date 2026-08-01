# Architecture

```text
ZeroClaw runtime
      |
      | rotating JSONL, mode 0600 on Unix
      v
runtime-trace.jsonl
      |
      | canonical JSON + SHA-256 (local only)
      v
domain-separated Merkle tree -------> local checkpoint manifest
      |                                      |
      | root + count                         | inclusion proofs
      v                                      v
Solana Action (unsigned)              independent local verifier
      |
      | explicit wallet review/signature
      v
Solana Memo program
```

## Components

### Canonical event hashing

Each JSON object is encoded with sorted object keys, no insignificant
whitespace, UTF-8, and no NaN/Infinity values. The leaf is:

```text
SHA256("clawledger:v1:event\\0" || canonical_event_json)
```

This preserves every event field while making the commitment independent of
whitespace or key order.

### Merkle tree

Parent nodes use a different domain:

```text
SHA256("clawledger:v1:node\\0" || left || right)
```

An unpaired last node is duplicated. The algorithm identifier is written into
the manifest so future versions cannot silently change semantics.

### Anchor

The on-chain Memo is:

```text
clawledger:v1:<64-char-root-hex>:<event-count>
```

The count prevents ambiguity about a tree containing a duplicated final node.
Timestamps and event identifiers remain in the local manifest only.

### Solana Action

The POST handler accepts one `account` public key, fetches a confirmed recent
blockhash, and serializes a legacy transaction with:

- one required signer: the wallet account;
- one read-only unsigned account: the Memo program;
- one instruction: the checkpoint Memo;
- one zero-filled signature slot for the wallet.

The server cannot sign or change the manifest root through the request body.

### Verification

Local verification finds the manifest's first/last event IDs in the source
log, recomputes every leaf and the root, and fails if the range is missing,
reordered, or modified. On-chain verification fetches the finalized
transaction, decodes the binary message, and checks for the exact expected
Memo and successful execution. It also rejects extra instructions, unexpected
accounts, non-canonical signature/header counts, and trailing transaction data;
merely including the expected Memo is not sufficient.
