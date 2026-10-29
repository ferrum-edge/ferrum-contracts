"""Execute the documented consumer check using public, inert Git objects.

No network, key generation, signing operation, private key, or SSH agent is
used. Only Git, OpenSSH's signature verifier, and the Python stdlib are needed.
"""

from __future__ import annotations

import base64
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "ci" / "testdata" / "release-signing"
TAG_OBJECT = "42ebad84b0585498c0413b0967cf4e80ec0e1d19"
COMMIT_OBJECT = "ac638b010cf58a27ee6c972d7336334ccaf61c96"


class ConsumerVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        doc = (ROOT / "docs" / "release-signing.md").read_text()
        blocks = re.findall(
            r"<!-- consumer-verification-test -->\n```sh\n(.*?)\n```\n"
            r"<!-- /consumer-verification-test -->",
            doc,
            re.DOTALL,
        )
        if len(blocks) != 1:
            raise AssertionError("Expected exactly one documented verification test")
        cls.script = blocks[0]

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "consumer"
        self.repo.mkdir()
        self.signers = Path(self.temp.name) / "allowed_signers"
        self.revoked = Path(self.temp.name) / "revoked_signers"
        self.public_key = (FIXTURE / "signer.pub").read_text().strip()
        self.signers.write_text(f'fixture@example.invalid namespaces="git" {self.public_key}\n')
        self.revoked.write_text("# No revoked test keys.\n")
        # Do not inherit any local signing program, trust store or SSH agent.
        self.env = {
            "PATH": os.defpath + os.pathsep + os.environ.get("PATH", ""),
            "LANG": "C",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "RELEASE_TAG": "v4.4.1",
            "RELEASE_TAG_OBJECT": TAG_OBJECT,
            "RELEASE_COMMIT": COMMIT_OBJECT,
            "TRUSTED_SIGNERS": str(self.signers),
            "TRUSTED_REVOKED_KEYS": str(self.revoked),
        }
        self.git("init", "-q", "--object-format=sha1")
        commit = base64.b64decode((FIXTURE / "commit.b64").read_bytes())
        self.assertEqual(self.write_object("commit", commit), COMMIT_OBJECT)
        self.assertEqual(self.write_object("tag", (FIXTURE / "tag.txt").read_bytes()), TAG_OBJECT)
        self.git("update-ref", "refs/tags/v4.4.1", TAG_OBJECT)

    def git(self, *args: str, data: bytes | None = None) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.repo, env=self.env, input=data,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
        )
        return result.stdout.decode().strip()

    def write_object(self, kind: str, data: bytes) -> str:
        return self.git("hash-object", "-w", "-t", kind, "--stdin", data=data)

    def replace_tag(self, data: bytes) -> None:
        oid = self.write_object("tag", data)
        self.git("update-ref", "refs/tags/v4.4.1", oid)
        self.env["RELEASE_TAG_OBJECT"] = oid

    def verify(self, accepted: bool) -> None:
        result = subprocess.run(
            ["sh", "-c", self.script], cwd=self.repo, env=self.env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        output = result.stdout + result.stderr
        if accepted:
            self.assertEqual(result.returncode, 0, output)
            self.assertIn("Good", output)
            self.assertIn("fixture@example.invalid", output)
        else:
            self.assertNotEqual(result.returncode, 0, output)

    def test_trusted_ssh_signed_tag_passes_without_private_key(self) -> None:
        self.verify(accepted=True)

    def test_ferrum_policy_does_not_trust_the_fixture_signer(self) -> None:
        self.signers.write_bytes((ROOT / "docs" / "allowed_signers").read_bytes())
        self.verify(accepted=False)

    def test_empty_trust_store_rejects_a_valid_signature(self) -> None:
        self.signers.write_text("")
        self.verify(accepted=False)

    def test_revoked_key_is_rejected(self) -> None:
        self.revoked.write_text(self.public_key + "\n")
        self.verify(accepted=False)

    def test_non_git_namespace_is_rejected(self) -> None:
        self.signers.write_text(f'fixture@example.invalid namespaces="file" {self.public_key}\n')
        self.verify(accepted=False)

    def test_expired_signing_interval_is_rejected(self) -> None:
        self.signers.write_text(
            'fixture@example.invalid namespaces="git",valid-before="20200101000000Z" '
            + self.public_key + "\n"
        )
        self.verify(accepted=False)

    def test_historical_signature_in_approved_interval_passes(self) -> None:
        self.signers.write_text(
            'fixture@example.invalid namespaces="git",valid-after="20250101000000Z",'
            'valid-before="20260101000000Z" ' + self.public_key + "\n"
        )
        self.verify(accepted=True)

    def test_tampered_annotation_is_rejected(self) -> None:
        original = (FIXTURE / "tag.txt").read_bytes()
        altered = original.replace(b"\n\nv4.4.1\n", b"\n\naltered annotation\n", 1)
        self.assertNotEqual(original, altered)
        self.replace_tag(altered)
        self.verify(accepted=False)

    def test_unsigned_annotated_tag_is_rejected(self) -> None:
        unsigned = (FIXTURE / "tag.txt").read_bytes().split(b"-----BEGIN SSH SIGNATURE-----")[0]
        self.replace_tag(unsigned)
        self.verify(accepted=False)

    def test_lightweight_tag_is_rejected(self) -> None:
        self.git("update-ref", "refs/tags/v4.4.1", COMMIT_OBJECT)
        self.env["RELEASE_TAG_OBJECT"] = COMMIT_OBJECT
        self.verify(accepted=False)

    def test_wrong_tag_object_pin_is_rejected(self) -> None:
        self.env["RELEASE_TAG_OBJECT"] = COMMIT_OBJECT
        self.verify(accepted=False)

    def test_wrong_target_commit_pin_is_rejected(self) -> None:
        self.env["RELEASE_COMMIT"] = "0" * 40
        self.verify(accepted=False)

    def test_missing_public_trust_file_is_rejected(self) -> None:
        self.signers.unlink()
        self.verify(accepted=False)

    def test_missing_revocation_file_is_rejected(self) -> None:
        self.revoked.unlink()
        self.verify(accepted=False)

    def test_missing_release_input_is_rejected(self) -> None:
        for name in (
            "RELEASE_TAG", "RELEASE_TAG_OBJECT", "RELEASE_COMMIT",
            "TRUSTED_SIGNERS", "TRUSTED_REVOKED_KEYS",
        ):
            with self.subTest(name=name):
                saved = self.env.pop(name)
                try:
                    self.verify(accepted=False)
                finally:
                    self.env[name] = saved


if __name__ == "__main__":
    unittest.main()
