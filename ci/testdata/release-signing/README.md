# Public verification fixture

These are inert public data, not an authorized Ferrum signer or release:

- `tag.txt`: exact raw SSH-signed `gradle/actions` tag `v4.4.1`, Git tag
  object `42ebad84b0585498c0413b0967cf4e80ec0e1d19`.
- `commit.b64`: base64-encoded exact raw target commit
  `ac638b010cf58a27ee6c972d7336334ccaf61c96`. Its tree is unnecessary for
  tag signature and target-identity verification; no source is executed.
  Base64 preserves the original armored signature's whitespace without
  introducing trailing whitespace into this repository's text files.
- `signer.pub`: public Ed25519 key decoded from the public SSH signature's
  key field. This is a test-only trust root, not an independent assertion
  about the upstream signer or authorization to release Ferrum Contracts.

Source: [Gradle Actions v4.4.1 tag](https://github.com/gradle/actions/releases/tag/v4.4.1)
and [target commit](https://github.com/gradle/actions/commit/ac638b010cf58a27ee6c972d7336334ccaf61c96),
retrieved 2026-10-29 with a shallow fetch of that tag. Object hashes are checked
by the tests before verification. No private key was accessed, copied or
generated; the tests cannot sign anything and require no network or SSH agent.
Never copy this test key into `docs/allowed_signers`.
