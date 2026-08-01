import hashlib
import unittest

from clawledger.merkle import merkle_proof, merkle_root, verify_proof


class MerkleTests(unittest.TestCase):
    def test_proofs_for_odd_leaf_count(self) -> None:
        leaves = [hashlib.sha256(value).digest() for value in (b"a", b"b", b"c")]
        root = merkle_root(leaves)
        for index, leaf in enumerate(leaves):
            proof = merkle_proof(leaves, index)
            self.assertTrue(verify_proof(leaf, proof, root))

    def test_tampered_leaf_fails(self) -> None:
        leaves = [hashlib.sha256(value).digest() for value in (b"a", b"b")]
        proof = merkle_proof(leaves, 0)
        self.assertFalse(verify_proof(hashlib.sha256(b"evil").digest(), proof, merkle_root(leaves)))

    def test_empty_tree_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            merkle_root([])


if __name__ == "__main__":
    unittest.main()
