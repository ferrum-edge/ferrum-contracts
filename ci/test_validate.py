"""Tests for ci/validate.py: the bounded --fetch-openapi download, the
schema provenance check, the gateway-headers availability check, the
unpublished Edge tag check, the vocabulary x-contract.instance check, the
diagnostic-ref values copied from gateway-errors, the PluginConfigBase
parser and catalog parity check, the cross-contract fixture check, and the
qualification case check.

Run with: python -I -m unittest discover -s ci -p 'test_*.py'
Every request goes to a loopback server this test starts; nothing leaves the
runner. Cross-check tests build synthetic schema and fixture trees in a
temporary directory, plus one read-only pass over this repository.
"""

from __future__ import annotations

import contextlib
import hashlib
import http.server
import importlib.util
import io
import json
import tempfile
import threading
import unittest
import unittest.mock
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "contracts_validate", Path(__file__).resolve().parent / "validate.py"
)
validate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate)
ROOT = Path(__file__).resolve().parent.parent

LIMIT = 4096


class _Handler(http.server.BaseHTTPRequestHandler):
    # HTTP/1.0: a body without Content-Length runs until the connection closes.
    protocol_version = "HTTP/1.0"
    hits: list[str] = []

    def log_message(self, *args) -> None:
        pass

    def do_GET(self) -> None:
        type(self).hits.append(self.path)
        try:
            if self.path == "/ok":
                body = b"a" * LIMIT
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif self.path == "/stream":
                # No Content-Length: the client only learns the size by reading.
                self.send_response(200)
                self.end_headers()
                for _ in range(64):
                    self.wfile.write(b"b" * 1024)
            elif self.path == "/declared":
                self.send_response(200)
                self.send_header("Content-Length", str(LIMIT * 1024))
                self.end_headers()
                self.wfile.write(b"c" * 1024)
            elif self.path == "/redirect":
                self.send_response(302)
                self.send_header("Location", "/target")
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header("Content-Length", "6")
                self.end_headers()
                self.wfile.write(b"target")
        except (BrokenPipeError, ConnectionResetError):
            # The client stops reading once it refuses the response.
            pass


class BoundedDownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self) -> None:
        _Handler.hits.clear()

    def test_a_body_at_the_limit_is_returned(self) -> None:
        self.assertEqual(validate.download_capped(f"{self.base}/ok", LIMIT), b"a" * LIMIT)

    def test_an_undeclared_body_over_the_limit_is_abandoned(self) -> None:
        with self.assertRaisesRegex(validate.DownloadError, "exceeds the 4096 byte limit"):
            validate.download_capped(f"{self.base}/stream", LIMIT)

    def test_an_endless_body_is_abandoned_after_one_chunk_past_the_limit(self) -> None:
        # The response never ends and counts what is read: reading it whole,
        # or past the limit plus one chunk, fails the test instead of passing.
        chunk = validate.DOWNLOAD_CHUNK_BYTES
        limit = 3 * chunk + 1

        class EndlessResponse:
            headers: dict[str, str] = {}
            consumed = 0

            def __enter__(self):
                return self

            def __exit__(self, *exc) -> None:
                return None

            def read(self, amount: int = -1) -> bytes:
                if amount is None or amount < 0:
                    raise AssertionError("unbounded read")
                type(self).consumed += amount
                if type(self).consumed > limit + chunk:
                    raise AssertionError(f"read {type(self).consumed} bytes past the cap")
                return b"z" * amount

        class Opener:
            def open(self, url, timeout=None):
                return EndlessResponse()

        with unittest.mock.patch.object(
            validate.urllib.request, "build_opener", lambda *handlers: Opener()
        ):
            with self.assertRaisesRegex(validate.DownloadError, "byte limit"):
                validate.download_capped("https://example.invalid/openapi.yaml", limit)
        self.assertLessEqual(EndlessResponse.consumed, limit + chunk)

    def test_a_declared_length_over_the_limit_is_refused_before_reading(self) -> None:
        with self.assertRaisesRegex(validate.DownloadError, "declares 4194304 bytes"):
            validate.download_capped(f"{self.base}/declared", LIMIT)

    def test_a_redirect_is_refused_and_not_followed(self) -> None:
        with self.assertRaisesRegex(validate.DownloadError, "refusing HTTP 302 redirect"):
            validate.download_capped(f"{self.base}/redirect", LIMIT)
        self.assertEqual(_Handler.hits, ["/redirect"])

    def test_download_errors_are_os_errors_for_the_existing_report_path(self) -> None:
        self.assertTrue(issubclass(validate.DownloadError, OSError))

    def test_a_local_openapi_over_the_limit_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "openapi.yaml"
            path.write_bytes(b"x" * LIMIT)
            self.assertEqual(validate.read_capped(path, LIMIT), b"x" * LIMIT)
            path.write_bytes(b"x" * (LIMIT + 1))
            with self.assertRaisesRegex(validate.DownloadError, "exceeds the 4096 byte limit"):
                validate.read_capped(path, LIMIT)

    def test_the_pinned_document_cap_is_32_mib(self) -> None:
        self.assertEqual(validate.MAX_OPENAPI_BYTES, 32 * 1024 * 1024)


def _write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _schema(name: str, version: int, body: dict) -> dict:
    return {
        "$schema": validate.META,
        "$id": f"{validate.BASE}/{name}/v{version}.schema.json",
        "x-contract": {
            "name": name,
            "version": version,
            "status": "proposed",
            "owner": "test",
            "provenance": [{"repo": "test", "path": "schema.json", "commit": "0" * 40}],
        },
        **body,
    }


class ProvenanceTests(unittest.TestCase):
    """A schema owned by another repository records repo, path and commit."""

    def check(self, contract: dict) -> list[str]:
        report = validate.Report()
        validate.check_provenance(Path("schema.json"), contract, report)
        return report.errors

    def test_a_full_provenance_entry_passes(self) -> None:
        entry = {"repo": "ferrum-edge/ferrum-edge", "path": "openapi.yaml", "commit": "a" * 40}
        contract = {"owner": "ferrum-edge/ferrum-edge", "provenance": [entry]}
        self.assertEqual(self.check(contract), [])

    def test_this_repository_needs_no_provenance(self) -> None:
        self.assertEqual(self.check({"owner": validate.CONTRACTS_REPO}), [])

    def test_another_owner_without_provenance_fails(self) -> None:
        for provenance in (None, [], {}):
            with self.subTest(provenance=provenance):
                contract = {"owner": "ferrum-edge/ferrum-alloy"}
                if provenance is not None:
                    contract["provenance"] = provenance
                self.assertEqual(
                    self.check(contract),
                    ["schema.json: x-contract.provenance must be a non-empty list"],
                )

    def test_an_incomplete_entry_fails(self) -> None:
        cases = {
            "repo": ({"path": "p", "commit": "a" * 40}, "repo is required"),
            "path": ({"repo": "r", "path": "", "commit": "a" * 40}, "path is required"),
            "short commit": ({"repo": "r", "path": "p", "commit": "a" * 12}, "commit must be"),
            "tag as commit": ({"repo": "r", "path": "p", "commit": "v0.9.20"}, "commit must be"),
            "uppercase commit": ({"repo": "r", "path": "p", "commit": "A" * 40}, "commit must be"),
            "not an object": ("r/p@" + "a" * 40, "must be an object"),
        }
        for label, (entry, message) in cases.items():
            with self.subTest(label):
                errors = self.check({"owner": "ferrum-edge/ferrum-edge", "provenance": [entry]})
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("x-contract.provenance[0]", errors[0])
                self.assertIn(message, errors[0])

    def test_every_repository_schema_passes(self) -> None:
        report = validate.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            schemas = validate.load_schemas(ROOT, report)
        self.assertEqual(report.errors, [])
        owners = {
            versions[version]["x-contract"]["owner"]
            for versions in schemas.values()
            for version in versions
        }
        self.assertGreater(len(owners - {validate.CONTRACTS_REPO}), 0)


class HeaderAvailabilityTests(unittest.TestCase):
    """A gateway-headers availability is a published Edge release no later
    than the vocabulary's edge_release, or unreleased."""

    def check(self, availability: str, edge_release: str = "v0.9.20") -> list[str]:
        vocabulary = {
            "edge_release": edge_release,
            "headers": [{"name": "X-Test", "availability": availability}],
        }
        report = validate.Report()
        validate.check_vocabulary_consistency({"gateway-headers": vocabulary}, report)
        return report.errors

    def test_published_releases_up_to_edge_release_pass(self) -> None:
        for availability in ("v0.9.4", "v0.9.5", "v0.9.7", "v0.9.17", "v0.9.20", "unreleased"):
            with self.subTest(availability=availability):
                self.assertEqual(self.check(availability), [])

    def test_an_unpublished_tag_fails(self) -> None:
        for availability in ("v0.9.0", "v0.9.3", "v0.9.6", "v0.9.16", "v0.9.18"):
            with self.subTest(availability=availability):
                self.assertEqual(
                    self.check(availability),
                    [
                        "vocabularies/gateway-headers.json: "
                        f"X-Test availability {availability} was never published"
                    ],
                )

    def test_a_release_after_edge_release_fails(self) -> None:
        cases = (("v0.9.21", "v0.9.20"), ("v0.9.10", "v0.9.9"), ("v1.0.0", "v0.9.20"))
        for availability, edge_release in cases:
            with self.subTest(availability=availability):
                self.assertEqual(
                    self.check(availability, edge_release),
                    [
                        "vocabularies/gateway-headers.json: "
                        f"X-Test availability {availability} is after {edge_release}"
                    ],
                )

    def test_the_repository_vocabulary_passes(self) -> None:
        report = validate.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            schemas = validate.load_schemas(ROOT, report)
            registry = validate.build_registry(schemas)
            vocabularies = validate.check_vocabularies(ROOT, schemas, registry, report)
            validate.check_vocabulary_consistency(vocabularies, report)
        self.assertEqual(report.errors, [])
        self.assertIn("gateway-headers", vocabularies)


class EdgeTagTests(unittest.TestCase):
    """No Edge release field names a tag that was never published."""

    def check(self, vocabulary: dict) -> list[str]:
        report = validate.Report()
        validate.check_vocabulary_consistency({"test": vocabulary}, report)
        return report.errors

    def test_published_tags_main_and_commits_pass(self) -> None:
        vocabulary = {
            "edge_release": "v0.9.20",
            "label": {"available_since": "v0.9.5"},
            "provenance": [{"repo": validate.EDGE_REPO, "ref": "v0.9.17", "commit": "a" * 40}],
            "main_branch_delta": {"ref": "main"},
        }
        self.assertEqual(self.check(vocabulary), [])

    def test_an_unpublished_tag_in_any_edge_release_field_fails(self) -> None:
        cases = {
            "edge_release": ({"edge_release": "v0.9.16"}, "/edge_release"),
            "available_since": (
                {"edge_release": "v0.9.20", "label": {"available_since": "v0.9.18"}},
                "/label/available_since",
            ),
            "provenance ref": (
                {
                    "edge_release": "v0.9.20",
                    "provenance": [{"repo": validate.EDGE_REPO, "ref": "v0.9.6"}],
                },
                "/provenance/0/ref",
            ),
            "source ref": (
                {"edge_release": "v0.9.20", "headers": [{"sources": [{"ref": "v0.9.3"}]}]},
                "/headers/0/sources/0/ref",
            ),
        }
        for label, (vocabulary, location) in cases.items():
            with self.subTest(label):
                errors = self.check(vocabulary)
                self.assertEqual(len(errors), 1, errors)
                self.assertTrue(errors[0].startswith(f"vocabularies/test.json: {location} names"))
                self.assertIn("was never published", errors[0])

    def test_another_repositorys_tag_is_not_an_edge_tag(self) -> None:
        vocabulary = {
            "edge_release": "v0.9.20",
            "provenance": [{"repo": "ferrum-edge/ferrum-nexus", "ref": "v0.9.16"}],
        }
        self.assertEqual(self.check(vocabulary), [])

    def test_a_schema_x_contract_naming_an_unpublished_tag_fails(self) -> None:
        report = validate.Report()
        contract = {"provenance": [{"repo": validate.EDGE_REPO, "ref": "v0.9.18"}]}
        validate.check_edge_tags("schema.json", contract, report, "/x-contract")
        self.assertEqual(
            report.errors,
            [
                "schema.json: /x-contract/provenance/0/ref names Edge v0.9.18, "
                "which was never published"
            ],
        )


class VocabularyInstanceTests(unittest.TestCase):
    """Every retained major of a vocabulary schema names its vocabulary file."""

    def run_check(self, v1_instance: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for version, instance in ((1, v1_instance), (2, "vocabularies/x.json")):
                schema = _schema("vocabulary-x", version, {"type": "object"})
                schema["x-contract"]["instance"] = instance
                _write(root / "schemas" / "vocabulary-x" / f"v{version}.schema.json", schema)
            _write(
                root / "vocabularies" / "x.json",
                {
                    "$schema": f"{validate.BASE}/vocabulary-x/v2.schema.json",
                    "vocabulary": "x",
                    "version": 2,
                },
            )
            report = validate.Report()
            with contextlib.redirect_stdout(io.StringIO()):
                schemas = validate.load_schemas(root, report)
                registry = validate.build_registry(schemas)
                validate.check_vocabularies(root, schemas, registry, report)
            return report.errors

    def test_every_major_naming_the_file_passes(self) -> None:
        self.assertEqual(self.run_check("vocabularies/x.json"), [])

    def test_an_earlier_major_naming_another_file_fails(self) -> None:
        self.assertEqual(
            self.run_check("vocabularies/y.json"),
            ["schemas/vocabulary-x/v1.schema.json: x-contract.instance must name its file"],
        )


class CopiedValueTests(unittest.TestCase):
    """diagnostic-ref copies the gateway-errors tokens and phase tokens exactly."""

    def setUp(self) -> None:
        def read(path: str):
            return json.loads((ROOT / path).read_text(encoding="utf-8"))

        self.schema = read("schemas/diagnostic-ref/v1.schema.json")
        self.errors = read("vocabularies/gateway-errors.json")
        self.headers = read("vocabularies/gateway-headers.json")

    def check(self) -> list[str]:
        report = validate.Report()
        validate.check_copied_values(
            {"diagnostic-ref": {1: self.schema}},
            {"gateway-errors": self.errors, "gateway-headers": self.headers},
            report,
        )
        return report.errors

    def phase_enum(self) -> list:
        return self.schema["$defs"]["Detail"]["properties"]["rejection_phase"]["enum"]

    def test_the_repository_values_match(self) -> None:
        self.assertEqual(self.check(), [])
        self.assertIn("loop_detected", self.phase_enum())

    def test_a_phase_token_missing_from_the_detail_enum_fails(self) -> None:
        self.phase_enum().remove("config_stale")
        errors = self.check()
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("detail.rejection_phase enum", errors[0])

    def test_a_new_token_selected_by_a_phase_fails(self) -> None:
        token = next(t for t in self.errors["x_gateway_error_tokens"] if not t["rejection_phases"])
        token["rejection_phases"] = ["new_phase"]
        errors = self.check()
        self.assertEqual(len(errors), 1, errors)
        self.assertIn(token["token"], errors[0])

    def test_a_detail_enum_without_null_fails(self) -> None:
        self.phase_enum().remove(None)
        self.assertEqual(
            self.check(),
            [
                "schemas/diagnostic-ref/v1.schema.json: "
                "detail.rejection_phase enum must allow null"
            ],
        )


def _gated_item(
    name: str,
    ref: str,
    required: bool = False,
    scope: str | None = None,
    required_lines: tuple[str, ...] = ("                  required: [config]",),
) -> str:
    lines = [
        "              - if:",
        "                  required: [plugin_name]",
        "                  properties:",
        "                    plugin_name:",
        f"                      const: {name}",
        "                then:",
    ]
    if required:
        lines += list(required_lines)
    lines.append("                  properties:")
    if scope:
        lines += ["                    scope:", f"                      const: {scope}"]
    lines += [
        "                    config:",
        f'                      $ref: "#/components/schemas/{ref}"',
    ]
    return "\n".join(lines) + "\n"


def _ungated_item(condition: list[str], consequence: list[str]) -> str:
    lines = ["        - if:", "            properties:"]
    lines += ["              " + line for line in condition]
    lines += ["          then:"] + ["            " + line for line in consequence]
    return "\n".join(lines) + "\n"


def _scope_item(name: str, scope: str) -> str:
    """An item outside the enabled gate that only constrains `scope`."""
    return _ungated_item(
        ["plugin_name:", f"  const: {name}"], ["properties:", "  scope:", f"    const: {scope}"]
    )


def _openapi(gated: str, ungated: str = "", gate: str = "const: false") -> str:
    return (
        "components:\n"
        "  schemas:\n"
        "    PluginConfigBase:\n"
        "      type: object\n"
        "      allOf:\n"
        "        - if:\n"
        "            properties:\n"
        "              enabled:\n"
        "                not:\n"
        f"                  {gate}\n"
        "          then:\n"
        "            allOf:\n" + gated + ungated + "\n"
        "    AConfig:\n"
        "      type: object\n"
        "    BConfig:\n"
        "      type: object\n"
    )


class PluginConfigRuleTests(unittest.TestCase):
    """PluginConfigBase is read one if/then item at a time, and the catalog's
    pointer, config_required_when_enabled and scope_constraint must match it."""

    def rules(self, text: str) -> tuple[dict, list[str]]:
        report = validate.Report()
        rules = validate.plugin_config_rules(text, report, "openapi.yaml")
        return rules, report.errors

    def test_each_item_contributes_its_ref_requirement_and_scope(self) -> None:
        text = _openapi(
            _gated_item("a", "AConfig", required=True, scope="global")
            + _gated_item("b", "BConfig"),
            _scope_item("b", "proxy"),
        )
        rules, errors = self.rules(text)
        self.assertEqual(errors, [])
        self.assertEqual(
            rules,
            {
                "a": {"ref": "AConfig", "config_required": True, "scope": "global"},
                "b": {"ref": "BConfig", "config_required": False, "scope": "proxy"},
            },
        )

    def test_a_scope_only_item_leaks_nothing_into_the_next_item(self) -> None:
        # The line scanner this replaced kept `b` current after its scope-only
        # item and charged the next item's $ref to it.
        text = _openapi(
            _gated_item("b", "BConfig"),
            _scope_item("b", "proxy")
            + _ungated_item(
                ["scope:", "  const: proxy"],
                ["properties:", "  config:", '    $ref: "#/components/schemas/AConfig"'],
            ),
        )
        rules, errors = self.rules(text)
        self.assertEqual(errors, [])
        self.assertEqual(
            rules, {"b": {"ref": "BConfig", "config_required": False, "scope": "proxy"}}
        )

    def test_a_config_constraint_outside_the_enabled_gate_fails(self) -> None:
        text = _openapi(
            _gated_item("a", "AConfig"),
            _ungated_item(["plugin_name:", "  const: a"], ["required: [config]"]),
        )
        _, errors = self.rules(text)
        self.assertEqual(errors, ["openapi.yaml: a: a config constraint outside the enabled gate"])

    def test_conflicting_scopes_fail(self) -> None:
        text = _openapi(
            _gated_item("a", "AConfig", scope="global"), _scope_item("a", "proxy")
        )
        _, errors = self.rules(text)
        self.assertEqual(errors, ["openapi.yaml: a constrains scope to both global and proxy"])

    def test_an_enabled_predicate_other_than_not_false_fails(self) -> None:
        # Inverting the gate keeps every name, $ref and requirement in place;
        # the reader must refuse it rather than count them as enabled-only.
        for gate in ("const: true", "const: false\n                  type: boolean"):
            with self.subTest(gate=gate):
                text = _openapi(_gated_item("a", "AConfig", required=True), gate=gate)
                rules, errors = self.rules(text)
                self.assertIn("unsupported enabled predicate", errors[0])
                self.assertNotEqual(
                    rules.get("a"), {"ref": "AConfig", "config_required": True, "scope": None}
                )

    def test_an_else_branch_is_refused(self) -> None:
        # Moving the plugin conditionals into the gate's `else` keeps the
        # predicate, names, $refs and requirements, but applies them only to
        # disabled configs; the reader must refuse it, not count them.
        gate_else = _openapi(_gated_item("a", "AConfig", required=True)).replace(
            "          then:\n            allOf:\n",
            "          then:\n            type: object\n          else:\n            allOf:\n",
        )
        item_else = _openapi(
            _gated_item("a", "AConfig")
            + "                else:\n                  required: [config]\n"
        )
        for label, text in (("gate", gate_else), ("plugin item", item_else)):
            with self.subTest(label):
                rules, errors = self.rules(text)
                self.assertTrue(
                    any("unsupported key 'else:' beside then" in e for e in errors), errors
                )
                self.assertNotEqual(
                    rules.get("a"), {"ref": "AConfig", "config_required": True, "scope": None}
                )

    def test_a_quoted_mapping_key_is_refused(self) -> None:
        for key in ('"required"', "'required'"):
            with self.subTest(key=key):
                text = _openapi(
                    _gated_item(
                        "a",
                        "AConfig",
                        required=True,
                        required_lines=(f"                  {key}: [config]",),
                    )
                )
                _, errors = self.rules(text)
                self.assertEqual(len(errors), 1, errors)
                line = f"{key}: [config]"
                self.assertIn(f"quoted YAML key {line!r} is not supported", errors[0])

    def test_quoted_and_block_required_lists_are_read(self) -> None:
        spellings = {
            "double-quoted flow": ('                  required: ["config"]',),
            "single-quoted flow": ("                  required: [plugin_name, 'config']",),
            "nested block": ("                  required:", "                    - config"),
            "same-indent block": ("                  required:", "                  - \"config\""),
        }
        for label, required_lines in spellings.items():
            with self.subTest(label):
                text = _openapi(
                    _gated_item("a", "AConfig", required=True, required_lines=required_lines)
                )
                rules, errors = self.rules(text)
                self.assertEqual(errors, [])
                self.assertEqual(
                    rules, {"a": {"ref": "AConfig", "config_required": True, "scope": None}}
                )

    def test_an_unknown_required_spelling_fails(self) -> None:
        spellings = {
            "scalar": ("                  required: config",),
            "flow mapping": ("                  required: {config: true}",),
            "block mapping": ("                  required:", "                    config: true"),
        }
        for label, required_lines in spellings.items():
            with self.subTest(label):
                text = _openapi(
                    _gated_item("a", "AConfig", required=True, required_lines=required_lines)
                    + _gated_item("b", "BConfig")
                )
                rules, errors = self.rules(text)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("a: unsupported then required:", errors[0])
                self.assertNotIn("a", rules)

    def check_catalog(self, config_schema: dict) -> list[str]:
        text = _openapi(_gated_item("a", "AConfig", required=True, scope="global"))
        data = text.encode("utf-8")
        catalog = {
            "config_schema_document": {"sha256": hashlib.sha256(data).hexdigest()},
            "plugins": [{"name": "a", "config_schema": config_schema}],
        }
        report = validate.Report()
        validate.check_openapi("openapi.yaml", data, {"plugin-catalog": catalog}, report)
        return report.errors

    def test_a_matching_catalog_entry_passes(self) -> None:
        entry = {
            "document": "openapi.yaml",
            "pointer": "#/components/schemas/AConfig",
            "config_required_when_enabled": True,
            "scope_constraint": "global",
        }
        self.assertEqual(self.check_catalog(entry), [])

    def test_catalog_drift_from_plugin_config_base_fails(self) -> None:
        base = {
            "document": "openapi.yaml",
            "pointer": "#/components/schemas/AConfig",
            "config_required_when_enabled": True,
            "scope_constraint": "global",
        }
        cases = {
            "pointer": ({"pointer": "#/components/schemas/BConfig"}, "references 'AConfig'"),
            "config required": (
                {"config_required_when_enabled": False},
                "config_required_when_enabled is True, catalog has False",
            ),
            "scope": ({"scope_constraint": "proxy"}, "scope_constraint is 'global'"),
            "no scope": ({"scope_constraint": None}, "scope_constraint is 'global'"),
        }
        for label, (change, message) in cases.items():
            with self.subTest(label):
                entry = {**base, **change}
                if entry["scope_constraint"] is None:
                    del entry["scope_constraint"]
                errors = self.check_catalog(entry)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn(message, errors[0])


class CrossCheckTests(unittest.TestCase):
    """A cross-check covers every major's valid fixtures and never passes vacuously."""

    CHECKS = [("finding", "report", "#/$defs/Finding")]

    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        _write(
            self.root / "schemas" / "report" / "v1.schema.json",
            _schema(
                "report",
                1,
                {"type": "object", "$defs": {"Finding": {"type": "object", "required": ["owner"]}}},
            ),
        )
        _write(self.root / "fixtures" / "report" / "valid" / "report.json", {})
        _write(self.root / "fixtures" / "report" / "invalid" / "not-object.json", [])
        self.expectations = {
            "report/invalid/not-object.json": {"instance_path": "", "keyword": "type"}
        }

    def add_finding_major(self, version: int, fixture_dir: Path, valid: dict) -> None:
        _write(
            self.root / "schemas" / "finding" / f"v{version}.schema.json",
            _schema("finding", version, {"type": "object", "required": ["id"]}),
        )
        _write(fixture_dir / "valid" / "finding.json", valid)
        _write(fixture_dir / "invalid" / "no-id.json", {})
        key = (fixture_dir / "invalid" / "no-id.json").relative_to(self.root / "fixtures")
        self.expectations[key.as_posix()] = {"instance_path": "", "keyword": "required"}

    def run_checks(self, checks=None) -> tuple[list[str], int]:
        _write(self.root / "fixtures" / validate.EXPECTATIONS, self.expectations)
        report = validate.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            schemas = validate.load_schemas(self.root, report)
            registry = validate.build_registry(schemas)
            sets = validate.check_fixtures(self.root, schemas, registry, report)
            self.assertEqual(report.errors, [], "the synthetic tree itself must be valid")
            before = report.checked
            with unittest.mock.patch.object(validate, "CROSS_CHECKS", checks or self.CHECKS):
                validate.check_cross(schemas, registry, sets, report)
        return report.errors, report.checked - before

    def test_a_single_major_set_is_cross_checked(self) -> None:
        fixtures = self.root / "fixtures" / "finding"
        self.add_finding_major(1, fixtures, {"id": "a"})
        errors, checked = self.run_checks()
        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("finding/valid/finding.json: valid finding fixture fails report", errors[0])

    def test_every_major_of_a_multi_major_set_is_cross_checked(self) -> None:
        fixtures = self.root / "fixtures" / "finding"
        self.add_finding_major(1, fixtures / "v1", {"id": "a", "owner": "o"})
        self.add_finding_major(2, fixtures / "v2", {"id": "a"})
        errors, checked = self.run_checks()
        self.assertEqual(checked, 1)
        self.assertEqual(len(errors), 1)
        self.assertIn(
            "finding/v2/valid/finding.json: valid finding fixture fails report", errors[0]
        )

    def test_a_cross_check_without_valid_fixtures_fails(self) -> None:
        self.add_finding_major(1, self.root / "fixtures" / "finding", {"id": "a", "owner": "o"})
        errors, checked = self.run_checks([("missing", "report", "#/$defs/Finding")])
        self.assertEqual(checked, 0)
        self.assertEqual(errors, ["cross-check missing->report: no valid missing fixture to check"])

    def test_the_repository_cross_check_covers_every_valid_finding_fixture(self) -> None:
        report = validate.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            schemas = validate.load_schemas(ROOT, report)
            registry = validate.build_registry(schemas)
            sets = validate.check_fixtures(ROOT, schemas, registry, report)
            before = report.checked
            validate.check_cross(schemas, registry, sets, report)
        self.assertEqual(report.errors, [])
        expected = sum(
            len(list((ROOT / "fixtures" / fixture_set).glob("**/valid/*.json")))
            for fixture_set, _, _ in validate.CROSS_CHECKS
        )
        self.assertGreater(expected, 0)
        self.assertEqual(report.checked - before, expected)


class QualificationTests(unittest.TestCase):
    """Qualification cases agree with the schema and with Alloy's derived IDs."""

    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        _write(
            self.root / "schemas" / "manifest" / "v1.schema.json",
            _schema(
                "manifest",
                1,
                {
                    "type": "object",
                    "required": ["service"],
                    "properties": {
                        "gateway": {
                            "type": "object",
                            "properties": {"proxy_id": {"type": "string", "maxLength": 254}},
                        }
                    },
                },
            ),
        )

    def case(self, length: int, exports: bool | None = None, schema_valid: bool = True) -> dict:
        proxy_id = "a" * length
        return {
            "id": f"id-{length}",
            "schema_valid": schema_valid,
            "producer_exports": length <= 241 if exports is None else exports,
            "derived_resource_ids": [f"{proxy_id}-otel-tracing"],
            "instance": {
                "service": {"name": "svc"},
                "gateway": {"proxy_id": proxy_id, "correlation_id": False},
            },
        }

    def run_doc(self, doc) -> tuple[list[str], int]:
        _write(self.root / "qualification" / "manifest" / "v1" / "cases.json", doc)
        report = validate.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            schemas = validate.load_schemas(self.root, report)
            registry = validate.build_registry(schemas)
            before = report.checked
            validate.check_qualifications(self.root, schemas, registry, report)
        return report.errors, report.checked - before

    def run_checks(self, cases, **overrides) -> tuple[list[str], int]:
        doc = {
            "contract": "manifest",
            "contract_version": 1,
            "rule": validate.ALLOY_DERIVED_ID_RULE,
            "edge_resource_id_max_length": 254,
            "producer": {"repo": "o/r", "paths": ["src/x.rs"], "commit": "a" * 40},
            "cases": cases,
            **overrides,
        }
        return self.run_doc(doc)

    def test_a_consistent_boundary_pair_passes(self) -> None:
        errors, checked = self.run_checks([self.case(241), self.case(242)])
        self.assertEqual(errors, [])
        self.assertEqual(checked, 2)

    def test_a_wrong_producer_outcome_fails(self) -> None:
        errors, checked = self.run_checks([self.case(242, exports=True)])
        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("producer_exports must be false", errors[0])

    def test_derived_ids_must_be_alloys(self) -> None:
        missing = self.case(242, exports=True)
        del missing["derived_resource_ids"]
        wrong_suffix = self.case(242, exports=True)
        wrong_suffix["derived_resource_ids"] = ["a" * 242 + "-x"]
        no_correlation = self.case(241)
        del no_correlation["instance"]["gateway"]["correlation_id"]
        no_correlation["id"] = "default-correlation"
        for case in (missing, wrong_suffix, no_correlation):
            with self.subTest(case=case["id"]):
                errors, checked = self.run_checks([case])
                self.assertEqual(checked, 0)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("derived_resource_ids must be Alloy's", errors[0])

    def test_health_and_correlation_add_their_ids(self) -> None:
        case = self.case(239)
        case["instance"]["gateway"]["correlation_id"] = True
        case["instance"]["health"] = {"path": "/readyz"}
        case["producer_exports"] = True
        case["derived_resource_ids"] = [
            "a" * 239 + "-upstream",
            "a" * 239 + "-correlation-id",
            "a" * 239 + "-otel-tracing",
        ]
        errors, checked = self.run_checks([case])
        self.assertEqual(errors, [])
        self.assertEqual(checked, 1)

    def test_a_schema_valid_claim_is_checked_both_ways(self) -> None:
        errors, _ = self.run_checks(
            [self.case(255, exports=False), self.case(241, schema_valid=False)]
        )
        self.assertEqual(len(errors), 2, errors)
        self.assertIn("marked schema_valid but fails manifest v1", errors[0])
        self.assertIn("marked not schema_valid but passes manifest v1", errors[1])

    def test_the_proxy_id_defaults_to_the_service_name(self) -> None:
        case = self.case(241)
        del case["instance"]["gateway"]["proxy_id"]
        case["derived_resource_ids"] = ["svc-otel-tracing"]
        errors, checked = self.run_checks([case])
        self.assertEqual(errors, [])
        self.assertEqual(checked, 1)

    def test_malformed_instances_fail_without_crashing(self) -> None:
        for label, instance in (
            ("array", []),
            ("string service", {"service": "svc"}),
            ("null gateway", {"service": {"name": "svc"}, "gateway": None}),
            ("string gateway", {"service": {"name": "svc"}, "gateway": "g"}),
            ("empty proxy ID", {"service": {"name": "svc"}, "gateway": {"proxy_id": ""}}),
            ("empty service name", {"service": {"name": ""}}),
        ):
            with self.subTest(label):
                case = self.case(241, schema_valid=False)
                case["instance"] = instance
                case["derived_resource_ids"] = ["svc-otel-tracing"]
                if label in ("string service", "empty proxy ID", "empty service name"):
                    case["schema_valid"] = True
                errors, checked = self.run_checks([case])
                self.assertEqual(checked, 0)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("Alloy can derive IDs from", errors[0])

    def test_a_case_without_instance_fails(self) -> None:
        case = self.case(241, schema_valid=False)
        del case["instance"]
        errors, checked = self.run_checks([case])
        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("instance is required", errors[0])

    def test_duplicate_and_missing_ids_are_not_counted(self) -> None:
        nameless = self.case(241)
        del nameless["id"]
        errors, checked = self.run_checks([self.case(241), self.case(241), nameless])
        self.assertEqual(checked, 1)
        self.assertEqual(len(errors), 2, errors)
        self.assertIn("duplicate case id", errors[0])
        self.assertIn("id is required", errors[1])

    def test_envelope_metadata_is_checked(self) -> None:
        for overrides, message in (
            ({"contract_version": True}, "contract_version"),
            ({"contract_version": 2}, "contract_version"),
            ({"producer": {"repo": "o/r", "paths": [], "commit": "a" * 40}}, "producer.paths"),
            ({"producer": {"repo": "o/r", "paths": ["p"], "commit": "abc"}}, "producer.commit"),
            ({"rule": "other"}, "unknown rule"),
            ({"edge_resource_id_max_length": 255}, "must be 254"),
        ):
            with self.subTest(message=message, overrides=overrides):
                errors, _ = self.run_checks([self.case(241)], **overrides)
                self.assertTrue(any(message in e for e in errors), errors)

    def test_a_null_or_non_object_case_set_fails(self) -> None:
        for doc in (None, []):
            with self.subTest(doc=doc):
                errors, checked = self.run_doc(doc)
                self.assertEqual(checked, 0)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("a qualification case set is a JSON object", errors[0])

    def test_layout_is_checked(self) -> None:
        _write(self.root / "qualification" / "manifest" / "v2" / "cases.json", {})
        _write(self.root / "qualification" / "unknown" / "v1" / "cases.json", {})
        (self.root / "qualification" / "empty").mkdir(parents=True)
        _write(self.root / "schemas" / "empty" / "v1.schema.json", _schema("empty", 1, {}))
        errors, _ = self.run_checks([self.case(241)])
        self.assertTrue(any("existing major" in e for e in errors), errors)
        self.assertTrue(any("no schema named 'unknown'" in e for e in errors), errors)
        self.assertTrue(any("empty: an empty qualification directory" in e for e in errors), errors)

    def test_a_missing_qualification_directory_fails(self) -> None:
        report = validate.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            schemas = validate.load_schemas(self.root, report)
            registry = validate.build_registry(schemas)
            validate.check_qualifications(self.root, schemas, registry, report)
        self.assertEqual(len(report.errors), 1, report.errors)
        self.assertIn("missing qualification/ directory", report.errors[0])

    def test_the_repository_cases_pass_and_keep_both_boundary_pairs(self) -> None:
        report = validate.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            schemas = validate.load_schemas(ROOT, report)
            registry = validate.build_registry(schemas)
            before = report.checked
            validate.check_qualifications(ROOT, schemas, registry, report)
        self.assertEqual(report.errors, [])
        path = ROOT / "qualification" / "service-manifest" / "v1" / "derived-id-limit.json"
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        outcomes = {case["id"]: case["producer_exports"] for case in cases}
        self.assertEqual(
            outcomes,
            {
                "no-exporter-241": True,
                "no-exporter-242": False,
                "explicit-exporter-241": True,
                "explicit-exporter-242": False,
            },
        )
        self.assertEqual(report.checked - before, len(cases))


if __name__ == "__main__":
    unittest.main()
