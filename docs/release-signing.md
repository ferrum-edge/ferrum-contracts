# Release signing

Future Contracts release tags use free Git/OpenSSH signing. This authenticates
the annotated tag and the commit it names. It does not sign separately edited
GitHub release notes or certify artifacts built by consumers. Existing tags
remain immutable and unsigned; this process does not retrofit them.

## Signer identity and trust policy

[allowed_signers](allowed_signers) is the only authority for which keys may
sign a release. A key is trusted only after the repository owner approves its
exact public key and SHA-256 fingerprint and that entry merges in a reviewed
PR. An empty policy authorizes nobody, so verification fails closed. Never add
a test key, a GitHub web-flow key, a wildcard principal or a CA. A GitHub-signed
merge commit does not sign a release tag.

Release tags are signed by the maintainer `jeremyjpj0916` under the principal
`31913027+jeremyjpj0916@users.noreply.github.com`, the account's public commit
identity. The signing key is a dedicated, passphrase-protected Ed25519 key on
the maintainer's release machine (an owner-controlled hardware-backed
`ed25519-sk` key is an acceptable alternative):

- Private key: `~/.ssh/ferrum_contracts_release_ed25519`, mode `0600`, inside
  an owner-only `~/.ssh` directory (`0700`). The maintainer chooses and keeps
  the passphrase and unlocks the key locally.
- Public key: the same path with `.pub`, mode `0644`. Only this public key and
  its `ssh-keygen -lf <public-key-path> -E sha256` fingerprint are published.
- GitHub registration: **Signing key** on the maintainer account, title
  `Ferrum Contracts release signing`. This key needs no SSH repository
  authentication, deploy-key permission, Actions secret, PAT, or paid service.
  Existing authenticated HTTPS access performs the normal tag push.

A private key or passphrase never appears in an issue, PR, CI log or any other
shared channel. Switching to a GPG identity is a policy change: review its
public fingerprint and verification steps in its own PR.

## Signer setup

The maintainer creates the key and answers passphrase prompts locally,
registers only the public key as a GitHub **Signing key**, and records the
public key, principal and SHA-256 fingerprint in the trust-policy PR. Discovery
on GitHub alone does not establish trust; the owner confirms the fingerprint.

To create the dedicated key, run the following and choose a nonempty
passphrase at the prompt. Use a new path; do not overwrite an existing key.

```sh
ssh-keygen -t ed25519 -a 100 \
  -C "31913027+jeremyjpj0916@users.noreply.github.com" \
  -f "$HOME/.ssh/ferrum_contracts_release_ed25519"
```

Confirm the private/public file modes and public fingerprint described above
before registration. The maintainer unlocks the key in their local agent only
when signing a release.

Add one line to `docs/allowed_signers` in this form, with the approved public
key in place of the placeholder (the placeholder is deliberately not a key):

```text
31913027+jeremyjpj0916@users.noreply.github.com namespaces="git" ssh-ed25519 <approved-public-key-base64>
```

Record its fingerprint in a comment above the entry; consumers compare it with
the GitHub signing key as described in
[Verify a downloaded tag](#verify-a-downloaded-tag). Keep the principal exact and the
namespace restricted to `git`. The public key itself confers no repository
write access. The trust-policy PR merges before the release it signs.

Configure only the maintainer's release checkout:

```sh
git config --local gpg.format ssh
git config --local user.signingkey "$HOME/.ssh/ferrum_contracts_release_ed25519.pub"
git config --local tag.gpgSign true
git config --local user.email "31913027+jeremyjpj0916@users.noreply.github.com"
```

For an approved hardware-backed key, use its public-key path instead.
The corresponding private key must be available to the maintainer's local
SSH agent. These commands do not change global Git settings or commit signing.
Then follow [Tagging](release-process.md#tagging). An unavailable key or failed
verification stops the release; never retry as a lightweight or unsigned tag.

## Verify a downloaded tag

Use Git 2.35+ and OpenSSH 8.8+ (including the `ssh-keygen` signature verifier).
Git 2.34 verifies SSH signatures but ignores `valid-before` and `valid-after`,
so a retired key would still verify. Verification uses public data only; no
GitHub account, private key, SSH agent, Python packages or paid features are
needed.

First establish a trust root independently of the release being checked:

1. Obtain the approved signer fingerprint from two independent sources and
   confirm they agree:
   - the fingerprint comment above the entry in `docs/allowed_signers` at the
     trust-policy commit on `main` (the commit that added or last changed the
     entry); record that full commit SHA as `TRUST_POLICY_COMMIT`;
   - the maintainer's public GitHub signing keys at
     `https://api.github.com/users/jeremyjpj0916/ssh_signing_keys`. The
     `https://github.com/<user>.keys` listing shows authentication keys and is
     not a substitute.

   A key copied from the downloaded tag or its release notes cannot bootstrap
   its own trust.
2. Export `docs/allowed_signers` and `docs/revoked_signers` from that reviewed
   policy commit into files outside the consumer checkout. Confirm the
   fingerprint of each entry's public-key fields (`ssh-ed25519 BASE64`), saved
   in a separate `.pub` file, with `ssh-keygen -lf KEY.pub -E sha256` against
   the fingerprint from step 1. Set `TRUSTED_SIGNERS` and
   `TRUSTED_REVOKED_KEYS` to those files' absolute paths. Use the current
   revocation policy from `main`; a cached old policy can miss a compromised
   key.
3. Obtain the actual authorized release tag, tag object SHA and full commit SHA
   from the maintainer's release evidence. Set `RELEASE_TAG`,
   `RELEASE_TAG_OBJECT` and `RELEASE_COMMIT` to those exact values. The two
   object SHAs are different for an annotated tag.

For example, after independently confirming `TRUST_POLICY_COMMIT`, export
the public files with `git show "$TRUST_POLICY_COMMIT:docs/allowed_signers"`
and `git show "$TRUST_POLICY_COMMIT:docs/revoked_signers"`. Do not replace
the pinned policy with the downloaded tag's files after verification fails.

From a clean clone, download the actual tag without checking out its contents:

```sh
git clone --no-checkout https://github.com/ferrum-edge/ferrum-contracts.git contracts-consumer
cd contracts-consumer
git fetch --no-tags origin "refs/tags/$RELEASE_TAG:refs/tags/$RELEASE_TAG"
```

The following is the verification test. It also runs offline once the objects
and trusted public policy files are available. Run it in a shell with the five
variables above exported. Accept only exit status zero; the Git output must
identify the approved principal and fingerprint.

<!-- consumer-verification-test -->
```sh
set -eu
: "${RELEASE_TAG:?Set the actual authorized release tag}"
: "${RELEASE_TAG_OBJECT:?Set its independently recorded tag object SHA}"
: "${RELEASE_COMMIT:?Set its independently recorded full commit SHA}"
: "${TRUSTED_SIGNERS:?Set the independently trusted allowed_signers path}"
: "${TRUSTED_REVOKED_KEYS:?Set the current trusted revoked_signers path}"
test -f "$TRUSTED_SIGNERS"
test -r "$TRUSTED_SIGNERS"
test -f "$TRUSTED_REVOKED_KEYS"
test -r "$TRUSTED_REVOKED_KEYS"
test "$(git rev-parse "refs/tags/$RELEASE_TAG")" = "$RELEASE_TAG_OBJECT"
test "$(git cat-file -t "$RELEASE_TAG_OBJECT")" = tag
test "$(git cat-file tag "$RELEASE_TAG_OBJECT" | sed -n '/^$/q;s/^tag //p')" = "$RELEASE_TAG"
git -c gpg.ssh.allowedSignersFile="$TRUSTED_SIGNERS" \
    -c gpg.ssh.revocationFile="$TRUSTED_REVOKED_KEYS" \
    -c gpg.openpgp.program=false -c gpg.x509.program=false \
    verify-tag "$RELEASE_TAG_OBJECT"
test "$(git rev-parse "$RELEASE_TAG_OBJECT^{commit}")" = "$RELEASE_COMMIT"
```
<!-- /consumer-verification-test -->

Only after success, use `git checkout --detach "$RELEASE_TAG_OBJECT^{commit}"`
or copy contract data from that commit. GitHub's
Verified badge and tag protection are useful separate signals; neither replaces
this test. The format-specific overrides prevent a different signature format
from using a consumer's unrelated local GPG or S/MIME trust store. The tag-name
check rejects a validly signed tag for one release published under another
release's name.

`ci/test_release_signing.py` executes this exact documentation block against
an inert public SSH-signed fixture. It tests success and rejection of altered
content, unsigned/lightweight tags, an untrusted key, a revoked key, a wrong
namespace, a tag published under another name, and mismatched release
object/commit pins. It generates no keys and
does not authorize the fixture signer for Ferrum. Run it with
`python3 -I -m unittest discover -s ci -p 'test_release_signing.py' -v`.

## Rotation and revocation

For routine rotation, have the owner approve the replacement public key and
fingerprint. Merge a reviewed policy change before using it for a release.
Keep the old public key for historical verification, limiting its signing
interval with OpenSSH `valid-before="YYYYMMDDHHMMSSZ"`; add a corresponding
`valid-after` for the new key if appropriate. Publish the new policy commit,
fingerprints and cutover time through the established trusted channel. A tag's
claimed signing time is not an independent timestamp.

For a compromised or unapproved key, add its full public key, without a
principal prefix, to [revoked_signers](revoked_signers) and remove its active
authorization in a reviewed PR. Consumers must refresh their trusted revocation
file; revocation makes even older signatures by that key fail verification.
Removing the key's GitHub registration is a separate account change. Record
affected releases and the owner's disposition publicly. Never rewrite existing
tags; any replacement release requires its own approval.

## Release evidence

Each signed release records, in its GitHub release notes: the release URL, tag
object SHA, target commit SHA, signer principal and fingerprint, trust-policy
commit, the verification output and exit status from a clean consumer clone,
and the required CI results. A documentation change or test fixture is not
proof of a signed Ferrum release.

References: [Git signing configuration](https://git-scm.com/docs/git-config#Documentation/git-config.txt-gpgsshallowedSignersFile),
[OpenSSH allowed signers](https://man.openbsd.org/ssh-keygen#ALLOWED_SIGNERS),
[GitHub signing tags](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-tags),
and [GitHub key registration](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
