# Release signing

Future Contracts release tags use free Git/OpenSSH signing. This authenticates
the annotated tag and the commit it names. It does not sign separately edited
GitHub release notes or certify artifacts built by consumers. Existing tags
remain immutable and unsigned; this process does not retrofit them.

## Owner approval and public identity

The repository owner must approve a maintainer, an exact public key and its
SHA-256 fingerprint before the key is trusted. The proposed maintainer is
`jeremyjpj0916`, the existing solo maintainer and repository admin. The proposed
public principal is the account's existing public commit identity,
`31913027+jeremyjpj0916@users.noreply.github.com`; confirm it with the owner.
This proposal does not authorize a key. [allowed_signers](allowed_signers)
currently authorizes none, so verification fails until the owner approves and
merges a real public key. Do not substitute a test key or a GitHub web-flow key.

Read-only inspection on 2026-10-29 found no configured local Git signing key,
no local `.ssh/*.pub` files, no loaded SSH-agent identities, and no public SSH
signing or GPG keys on that maintainer's GitHub account. A key held elsewhere
may exist; ask the maintainer
before creating one. A GitHub-signed merge commit does not sign a release tag.

Prefer an existing suitable owner-controlled SSH signing key if the owner can
confirm its fingerprint and custody. Otherwise propose a dedicated,
passphrase-protected Ed25519 key on the maintainer's release machine:

- Private key: `~/.ssh/ferrum_contracts_release_ed25519`, mode `0600`, inside
  an owner-only `~/.ssh` directory (`0700`). The owner enters and retains the
  passphrase and handles any agent unlock prompt locally.
- Public key: the same path with `.pub`, mode `0644`. Only this public key and
  its `ssh-keygen -lf <public-key-path> -E sha256` fingerprint are published.
- GitHub registration: **Signing key** on the approved maintainer account,
  title `Ferrum Contracts release signing`. This key needs no SSH repository
  authentication, deploy-key permission, Actions secret, PAT, or paid service.
  Existing authenticated HTTPS access performs the normal tag push.

Obtain specific approval before generating or configuring a key, loading an
agent, registering a key, or changing any account/security setting. Never
request or transmit a private key or passphrase in chat, a PR or CI. This
document does not grant that approval. If the owner already has an established
GPG release-signing identity, review its public fingerprint and verification
policy explicitly rather than silently switching formats.

## Setup after specific approval

The maintainer handles key creation or selection and any passphrase prompts
locally. Register only the approved public key as a GitHub **Signing key**.
Record the owner-confirmed public key, principal and SHA-256 fingerprint in
the trust-policy PR. Independently compare the fingerprint with the owner;
discovery on GitHub alone does not establish trust.

If specifically approved to create the proposed dedicated key, the maintainer
can run the following locally, choose a nonempty passphrase at the prompt, and
retain it outside chat/CI. Use a new path; do not overwrite an existing key.

```sh
ssh-keygen -t ed25519 -a 100 \
  -C "31913027+jeremyjpj0916@users.noreply.github.com" \
  -f "$HOME/.ssh/ferrum_contracts_release_ed25519"
```

Confirm the private/public file modes and public fingerprint described above
before registration. The owner unlocks the corresponding key in their local
agent when signing an actual approved release.

Add one real line to `docs/allowed_signers` in this form, replacing the example
with the actual approved public key (the example is deliberately not a key):

```text
31913027+jeremyjpj0916@users.noreply.github.com namespaces="git" ssh-ed25519 <approved-public-key-base64>
```

Record its fingerprint and approval evidence alongside the real entry. Keep
the principal exact and the namespace restricted to `git`. The public key
itself confers no repository write access. Merge this trust-policy PR before
the next actual release, and publish its full commit SHA and the fingerprint
through an owner-confirmed channel for consumers to pin.

After approval, configure only the maintainer's actual release checkout:

```sh
git config --local gpg.format ssh
git config --local user.signingkey "$HOME/.ssh/ferrum_contracts_release_ed25519.pub"
git config --local tag.gpgSign true
git config --local user.email "31913027+jeremyjpj0916@users.noreply.github.com"
```

If the owner chose an existing key or another public identity, use the approved
public-key path and confirmed account email instead.
The corresponding private key must be available to the maintainer's local
SSH agent. These commands do not change global Git settings or commit signing.
Then follow [Tagging](release-process.md#tagging). An unavailable key or failed
verification stops the release; never retry as a lightweight or unsigned tag.

## Verify a downloaded tag

Use Git 2.34+ and OpenSSH 8.8+ (including the `ssh-keygen` signature verifier).
Verification uses public data only; no GitHub account, private key, SSH agent,
Python packages or paid features are needed.

First establish a trust root independently of the release being checked:

1. Obtain the owner's approved signer fingerprint and full trust-policy commit
   SHA through a channel you already trust. A key copied from the candidate
   tag or its release notes cannot bootstrap its own trust.
2. Export `docs/allowed_signers` and `docs/revoked_signers` from that reviewed
   policy commit into files outside the candidate checkout. Confirm the
   fingerprint of each entry's public-key fields (`ssh-ed25519 BASE64`), saved
   in a separate `.pub` file, with `ssh-keygen -lf KEY.pub -E sha256` and the
   owner-confirmed value. Set `TRUSTED_SIGNERS` and `TRUSTED_REVOKED_KEYS` to
   those files' absolute paths. Use the current owner-confirmed revocation
   policy; a cached old policy can miss a compromised key.
3. Obtain the actual authorized release tag, tag object SHA and full commit SHA
   from the maintainer's release evidence. Set `RELEASE_TAG`,
   `RELEASE_TAG_OBJECT` and `RELEASE_COMMIT` to those exact values. The two
   object SHAs are different for an annotated tag.

For example, after independently confirming `TRUST_POLICY_COMMIT`, export
the public files with `git show "$TRUST_POLICY_COMMIT:docs/allowed_signers"`
and `git show "$TRUST_POLICY_COMMIT:docs/revoked_signers"`. Do not replace
the pinned policy with the candidate tag's files after verification fails.

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
from using a consumer's unrelated local GPG or S/MIME trust store.

`ci/test_release_signing.py` executes this exact documentation block against
an inert public SSH-signed fixture. It tests success and rejection of altered
content, unsigned/lightweight tags, an untrusted key, a revoked key, a wrong
namespace, and mismatched release object/commit pins. It generates no keys and
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
Ask the owner separately before removing GitHub registration or changing any
account setting. Record affected releases and owner disposition publicly.
Never rewrite existing tags; any replacement release requires its own approval.

## Completion evidence

Keep [issue #30](https://github.com/ferrum-edge/ferrum-contracts/issues/30) open
until the next actual authorized release verifies from a clean consumer clone,
or the owner explicitly records another disposition. Record the real release
URL, tag object SHA, target commit SHA, approved principal/fingerprint,
trust-policy commit, successful verification output/exit status and required
CI results in the release evidence. A documentation PR or test fixture is not
proof of a signed Ferrum release. Do not create an artificial release to close
the issue.

References: [Git signing configuration](https://git-scm.com/docs/git-config#Documentation/git-config.txt-gpgsshallowedSignersFile),
[OpenSSH allowed signers](https://man.openbsd.org/ssh-keygen#ALLOWED_SIGNERS),
[GitHub signing tags](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-tags),
and [GitHub key registration](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
