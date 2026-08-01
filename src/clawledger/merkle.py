from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Sequence


NODE_DOMAIN = b"clawledger:v1:node\x00"


@dataclass(frozen=True)
class ProofStep:
    side: str
    hash_hex: str


def _node(left: bytes, right: bytes) -> bytes:
    if len(left) != 32 or len(right) != 32:
        raise ValueError("Merkle nodes must be 32-byte SHA-256 hashes")
    return hashlib.sha256(NODE_DOMAIN + left + right).digest()


def _validate_leaves(leaves: Iterable[bytes]) -> list[bytes]:
    values = list(leaves)
    if not values:
        raise ValueError("cannot build a Merkle tree without leaves")
    if any(len(value) != 32 for value in values):
        raise ValueError("every Merkle leaf must be a 32-byte SHA-256 hash")
    return values


def merkle_root(leaves: Iterable[bytes]) -> bytes:
    level = _validate_leaves(leaves)
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [_node(level[i], level[i + 1]) for i in range(0, len(level), 2)]
    return level[0]


def merkle_proof(leaves: Sequence[bytes], index: int) -> list[ProofStep]:
    level = _validate_leaves(leaves)
    if index < 0 or index >= len(level):
        raise IndexError("leaf index out of range")

    cursor = index
    proof: list[ProofStep] = []
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        sibling = cursor ^ 1
        proof.append(
            ProofStep(
                side="left" if sibling < cursor else "right",
                hash_hex=level[sibling].hex(),
            )
        )
        level = [_node(level[i], level[i + 1]) for i in range(0, len(level), 2)]
        cursor //= 2
    return proof


def verify_proof(leaf: bytes, proof: Sequence[ProofStep], expected_root: bytes) -> bool:
    if len(leaf) != 32 or len(expected_root) != 32:
        return False
    current = leaf
    try:
        for step in proof:
            sibling = bytes.fromhex(step.hash_hex)
            if step.side == "left":
                current = _node(sibling, current)
            elif step.side == "right":
                current = _node(current, sibling)
            else:
                return False
    except (ValueError, TypeError):
        return False
    return current == expected_root
