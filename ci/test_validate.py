"""Tests for ci/validate.py: the bounded --fetch-openapi download, the
schema provenance check, the gateway-headers availability check, the
unpublished Edge tag check, the vocabulary x-contract.instance check, the
main_branch_delta presence check, the diagnostic-ref values copied from gateway-errors, the PluginConfigBase
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


class MainBranchDeltaTests(unittest.TestCase):
    """plugin-catalog, gateway-headers and gateway-errors keep a
    main_branch_delta on Edge main; a release resets it, never removes it."""

    RELEASE = "f" * 40
    EMPTY_DELTA = {
        "repo": validate.EDGE_REPO,
        "ref": "main",
        "commit": RELEASE,
        "summary": f"No contract-visible changes beyond v0.9.21 ({RELEASE}) at Edge main {RELEASE}.",
    }

    def check(self, vocabularies: dict[str, dict]) -> list[str]:
        report = validate.Report()
        validate.check_main_branch_delta(vocabularies, report)
        return report.errors

    def vocabularies(self, delta) -> dict[str, dict]:
        docs = {}
        for name in validate.DELTA_VOCABULARIES:
            docs[name] = {"edge_release": "v0.9.21"}
            if delta is not None:
                docs[name]["main_branch_delta"] = dict(delta)
        return docs

    def test_the_empty_delta_at_the_release_commit_passes(self) -> None:
        self.assertEqual(self.check(self.vocabularies(self.EMPTY_DELTA)), [])

    def test_a_removed_delta_fails_in_each_vocabulary(self) -> None:
        errors = self.check(self.vocabularies(None))
        self.assertEqual(len(errors), len(validate.DELTA_VOCABULARIES), errors)
        for name, error in zip(validate.DELTA_VOCABULARIES, errors):
            self.assertTrue(error.startswith(f"vocabularies/{name}.json: main_branch_delta is required"))

    def test_one_vocabulary_without_the_delta_fails_alone(self) -> None:
        vocabularies = self.vocabularies(self.EMPTY_DELTA)
        del vocabularies["gateway-errors"]["main_branch_delta"]
        errors = self.check(vocabularies)
        self.assertEqual(len(errors), 1, errors)
        self.assertTrue(errors[0].startswith("vocabularies/gateway-errors.json: main_branch_delta is required"))

    def test_another_repository_or_branch_fails(self) -> None:
        for field, value in (("repo", "ferrum-edge/ferrum-alloy"), ("ref", "v0.9.21")):
            with self.subTest(field=field):
                delta = dict(self.EMPTY_DELTA, **{field: value})
                errors = self.check(self.vocabularies(delta))
                self.assertEqual(len(errors), len(validate.DELTA_VOCABULARIES), errors)
                self.assertIn("main_branch_delta must name ferrum-edge/ferrum-edge and ref main", errors[0])

    def test_a_missing_vocabulary_fails(self) -> None:
        vocabularies = self.vocabularies(self.EMPTY_DELTA)
        del vocabularies["plugin-catalog"]
        self.assertEqual(
            self.check(vocabularies),
            [
                "vocabularies/plugin-catalog.json: "
                "missing or invalid, so its main_branch_delta cannot be checked"
            ],
        )

    def test_the_repository_vocabularies_pass(self) -> None:
        report = validate.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            schemas = validate.load_schemas(ROOT, report)
            registry = validate.build_registry(schemas)
            vocabularies = validate.check_vocabularies(ROOT, schemas, registry, report)
            validate.check_main_branch_delta(vocabularies, report)
        self.assertEqual(report.errors, [])

    def test_the_empty_delta_validates_against_each_vocabulary_schema(self) -> None:
        report = validate.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            schemas = validate.load_schemas(ROOT, report)
            registry = validate.build_registry(schemas)
        self.assertEqual(report.errors, [])
        for name in validate.DELTA_VOCABULARIES:
            with self.subTest(name=name):
                doc = json.loads((ROOT / "vocabularies" / f"{name}.json").read_text(encoding="utf-8"))
                doc["main_branch_delta"] = dict(self.EMPTY_DELTA)
                schema = schemas[f"vocabulary-{name}"][doc["version"]]
                self.assertIsNone(validate.first_error(validate.validator(schema, registry), doc))


class SensitivityAndReservedHeaderTests(unittest.TestCase):
    """plugin-config-sensitivity matches the catalog's plugins; reserved-header-names
    sets are named for a catalog plugin."""

    def setUp(self) -> None:
        def read(name: str) -> dict:
            return json.loads((ROOT / "vocabularies" / f"{name}.json").read_text(encoding="utf-8"))

        self.catalog = read("plugin-catalog")
        self.sensitivity = read("plugin-config-sensitivity")
        self.reserved = read("reserved-header-names")

    def check(self) -> list[str]:
        report = validate.Report()
        validate.check_plugin_config_sensitivity(
            {"plugin-catalog": self.catalog, "plugin-config-sensitivity": self.sensitivity}, report
        )
        validate.check_reserved_header_names(
            {"plugin-catalog": self.catalog, "reserved-header-names": self.reserved}, report
        )
        return report.errors

    def test_the_repository_vocabularies_pass(self) -> None:
        self.assertEqual(self.check(), [])
        self.assertIn("x-real-ip", self.reserved["sets"][0]["names"])

    def test_a_catalog_plugin_without_an_entry_fails(self) -> None:
        removed = self.sensitivity["plugins"].pop()
        errors = self.check()
        self.assertEqual(errors, [f"vocabularies/plugin-config-sensitivity.json: catalog plugin {removed['name']!r} has no sensitivity entry"])

    def test_an_unknown_plugin_fails(self) -> None:
        self.sensitivity["plugins"].append({"name": "zz_unknown", "rules": []})
        errors = self.check()
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("'zz_unknown' is not a plugin", errors[0])

    def test_a_differently_spelled_repeated_path_fails(self) -> None:
        plugin = next(p for p in self.sensitivity["plugins"] if p["name"] == "otel_tracing")
        plugin["rules"].append({"path": ["end_point"], "sensitivity": "Secret"})
        errors = self.check()
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("otel_tracing repeats rule path 'end_point'", errors[0])

    def test_path_examples_follow_the_grammar(self) -> None:
        reach = validate.sensitivity_rule_reach
        config = {"providers": [{"name": "p", "base_url": "https://a/v1"}]}
        self.assertEqual(
            list(reach(config, ["providers", "*", "base_url"], "EndpointUrl")),
            [("/providers/0/base_url", "EndpointUrl")],
        )
        # Carrying '*' into the element instead would reach name and base_url.
        self.assertEqual(list(reach({"a": [{"b": "x"}]}, ["a", "b"], "Secret")), [("/a/0/b", "Secret")])
        self.assertEqual(list(reach({"a": "scalar"}, ["a", "*"], "EndpointUrl")), [("/a", "Secret")])
        self.assertEqual(list(reach({"a/b": {"~": 1}}, ["a/b", "*"], "Secret")), [("/a~1b/~0", "Secret")])
        example = self.sensitivity["path_examples"][0]
        example["applied"] = []
        errors = self.check()
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("path_examples[0]", errors[0])

    def test_an_unlisted_class_and_a_repeated_path_fail(self) -> None:
        plugin = next(p for p in self.sensitivity["plugins"] if p["rules"])
        self.sensitivity["sensitivities"] = [
            c for c in self.sensitivity["sensitivities"] if c["value"] != plugin["rules"][0]["sensitivity"]
        ]
        plugin["rules"].append(dict(plugin["rules"][0]))
        errors = self.check()
        self.assertTrue(any("uses unlisted sensitivity" in e for e in errors), errors)
        self.assertTrue(any("repeats rule path" in e for e in errors), errors)

    def test_the_mcp_bridge_vocabulary_passes_and_overlaps_fail(self) -> None:
        bridge = json.loads((ROOT / "vocabularies" / "mcp-openapi-bridge.json").read_text(encoding="utf-8"))
        report = validate.Report()
        validate.check_mcp_openapi_bridge({"mcp-openapi-bridge": bridge}, report)
        self.assertEqual(report.errors, [])
        self.assertIn("x-real-ip", bridge["reserved_request_headers"]["names"])
        bridge["reserved_request_headers"]["names"].append("x-ferrum-anything")
        bridge["keys"]["document"].remove("limits")
        report = validate.Report()
        validate.check_mcp_openapi_bridge({"mcp-openapi-bridge": bridge}, report)
        self.assertEqual(len(report.errors), 2, report.errors)
        self.assertTrue(any("covered by prefix 'x-ferrum-'" in e for e in report.errors))
        self.assertTrue(any("lacks 'limits'" in e for e in report.errors))

    def test_a_misnamed_or_unknown_reserved_set_fails(self) -> None:
        self.reserved["sets"][0]["name"] = "correlation_id.header"
        self.reserved["sets"].append(dict(self.reserved["sets"][0], name="nope.header_name", plugin="nope"))
        errors = self.check()
        self.assertTrue(any("must be named correlation_id.header_name" in e for e in errors), errors)
        self.assertTrue(any("names unknown plugin 'nope'" in e for e in errors), errors)


class PluginConfigSchemaFileTests(unittest.TestCase):
    """plugin-config-schemas/ matches the catalog offline: one valid 2020-12
    document per plugin, carrying the catalog's pin."""

    def setUp(self) -> None:
        self.catalog = json.loads((ROOT / "vocabularies" / "plugin-catalog.json").read_text(encoding="utf-8"))

    def check(self, catalog: dict) -> list[str]:
        report = validate.Report()
        validate.check_plugin_config_schema_files(ROOT, {"plugin-catalog": catalog}, report)
        return report.errors

    def test_the_repository_files_pass(self) -> None:
        self.assertEqual(self.check(self.catalog), [])

    def test_a_re_pin_without_regeneration_fails_every_file(self) -> None:
        catalog = json.loads(json.dumps(self.catalog))
        catalog["config_schema_document"]["sha256"] = "0" * 64
        errors = self.check(catalog)
        self.assertEqual(len(errors), len(catalog["plugins"]), errors[:3])
        self.assertTrue(all("x-generated.source differs" in e for e in errors))

    def test_a_missing_or_extra_plugin_fails(self) -> None:
        catalog = json.loads(json.dumps(self.catalog))
        removed = catalog["plugins"].pop(0)
        added = dict(removed, name="zz_new_plugin")
        catalog["plugins"].append(added)
        errors = self.check(catalog)
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(any("zz_new_plugin.schema.json: missing" in e for e in errors))
        self.assertTrue(any(f"{removed['name']}.schema.json: not a catalog plugin" in e for e in errors))


class ResourceSchemaFileTests(unittest.TestCase):
    """resource-schemas/ holds the published Edge resource request schemas."""

    def setUp(self) -> None:
        self.catalog = json.loads((ROOT / "vocabularies" / "plugin-catalog.json").read_text(encoding="utf-8"))

    def check(self, catalog: dict) -> list[str]:
        report = validate.Report()
        validate.check_resource_schema_files(ROOT, {"plugin-catalog": catalog}, report)
        return report.errors

    def test_the_repository_files_pass(self) -> None:
        self.assertEqual(self.check(self.catalog), [])

    def test_a_re_pin_without_regeneration_fails_every_file(self) -> None:
        catalog = json.loads(json.dumps(self.catalog))
        catalog["config_schema_document"]["ref"] = "v9.9.9"
        errors = self.check(catalog)
        self.assertEqual(len(errors), 2 * len(validate.plugin_config_schemas.RESOURCE_ROOTS), errors)


class YamlReaderParityTests(unittest.TestCase):
    """The generator's YAML reader and PyYAML with YAML 1.2 core resolvers agree."""

    DOC = (
        "a: 017\nb: 0o17\nc: 0x1F\nd: 1.0e288\ne: yes\nf: true\ng: ~\nh: 2026-11-27\n"
        "i: [two  spaces, 'q', \"x\\ty\"]\nj: |\n  line\n    more\nk: >-\n  folded\n  text\n"
        "l:\n  - m: 1\n    n: [1, 2]\n"
    )

    def test_the_parsers_agree_on_core_schema_scalars(self) -> None:
        report = validate.Report()
        validate.check_yaml_reader("doc", self.DOC.encode(), report)
        self.assertEqual(report.errors, [])
        yaml, loader = validate.yaml_core_12_loader()
        parsed = yaml.load(self.DOC, Loader=loader)
        self.assertEqual((parsed["a"], parsed["b"], parsed["e"], parsed["h"]), (17, 15, "yes", "2026-11-27"))

    def test_a_disagreement_is_reported(self) -> None:
        report = validate.Report()
        with unittest.mock.patch.object(validate.plugin_config_schemas, "load_yaml", return_value={"a": "17"}):
            validate.check_yaml_reader("doc", b"a: 17\n", report)
        self.assertEqual(len(report.errors), 1, report.errors)
        self.assertIn("disagree at /a: str", report.errors[0])

    def test_types_are_compared_strictly(self) -> None:
        self.assertIsNotNone(validate.yaml_difference({"a": 1}, {"a": 1.0}))
        self.assertIsNotNone(validate.yaml_difference({"a": 1}, {"a": True}))
        self.assertIsNone(validate.yaml_difference({"a": [1, "x"]}, {"a": [1, "x"]}))

    def test_a_generated_file_that_is_not_an_object_fails(self) -> None:
        catalog = json.loads((ROOT / "vocabularies" / "plugin-catalog.json").read_text(encoding="utf-8"))
        real = validate.load_json
        calls = []

        def first_is_null(path, report):
            calls.append(path)
            return None if len(calls) == 1 else real(path, report)

        report = validate.Report()
        with unittest.mock.patch.object(validate, "load_json", side_effect=first_is_null):
            validate.check_plugin_config_schema_files(ROOT, {"plugin-catalog": catalog}, report)
        self.assertEqual(len(report.errors), 1, report.errors)
        self.assertIn("a generated schema is a JSON object", report.errors[0])

    def test_non_json_constants_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "x.json"
            path.write_text('{"maximum": Infinity}\n', encoding="utf-8")
            report = validate.Report()
            self.assertIsNone(validate.load_json(path, report))
            self.assertEqual(len(report.errors), 1, report.errors)


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


class CopiedValueMajorTests(unittest.TestCase):
    """With a second diagnostic-ref major side by side, only the newest
    implemented major mirrors the current vocabulary; the retained major keeps
    the values it was published with."""

    def setUp(self) -> None:
        def read(path: str):
            return json.loads((ROOT / path).read_text(encoding="utf-8"))

        self.v1 = read("schemas/diagnostic-ref/v1.schema.json")
        self.errors = read("vocabularies/gateway-errors.json")
        self.headers = read("vocabularies/gateway-headers.json")
        # The scenario a v2 exists for: Edge retires a token. The current
        # vocabulary drops it, v2 drops it, and v1 keeps accepting it.
        self.retired = "loop_detected"
        self.errors["x_gateway_error_tokens"] = [
            t for t in self.errors["x_gateway_error_tokens"] if t["token"] != self.retired
        ]
        self.v2 = json.loads(json.dumps(self.v1))
        self.v2["$id"] = self.v1["$id"].replace("/v1.schema.json", "/v2.schema.json")
        self.v2["x-contract"]["version"] = 2
        for enum in (self.enum(self.v2), self.phase_enum(self.v2)):
            enum.remove(self.retired)

    @staticmethod
    def enum(schema: dict) -> list:
        return schema["properties"]["gateway_error"]["enum"]

    @staticmethod
    def phase_enum(schema: dict) -> list:
        return schema["$defs"]["Detail"]["properties"]["rejection_phase"]["enum"]

    def check(self, versions: dict[int, dict]) -> list[str]:
        report = validate.Report()
        validate.check_copied_values(
            {"diagnostic-ref": versions},
            {"gateway-errors": self.errors, "gateway-headers": self.headers},
            report,
        )
        return report.errors

    def test_the_retained_major_keeps_a_retired_token(self) -> None:
        self.assertIn(self.retired, self.enum(self.v1))
        self.assertIn(self.retired, self.phase_enum(self.v1))
        self.assertEqual(self.check({1: self.v1, 2: self.v2}), [])

    def test_the_newest_major_must_match_the_vocabulary(self) -> None:
        self.enum(self.v2).append(self.retired)
        errors = self.check({1: self.v1, 2: self.v2})
        self.assertEqual(len(errors), 1, errors)
        self.assertTrue(errors[0].startswith("schemas/diagnostic-ref/v2.schema.json: gateway_error enum"))

    def test_a_single_major_is_still_compared(self) -> None:
        errors = self.check({1: self.v1})
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(all(e.startswith("schemas/diagnostic-ref/v1.schema.json: ") for e in errors))

    def test_a_proposed_newer_major_does_not_mirror_yet(self) -> None:
        self.v2["x-contract"]["status"] = "proposed"
        errors = self.check({1: self.v1, 2: self.v2})
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(all(e.startswith("schemas/diagnostic-ref/v1.schema.json: ") for e in errors))

    def test_no_implemented_major_fails(self) -> None:
        self.v1["x-contract"]["status"] = "proposed"
        self.assertEqual(
            self.check({1: self.v1}),
            [
                "schemas/diagnostic-ref/v1.schema.json: an implemented diagnostic-ref major, "
                "gateway-errors or gateway-headers is missing"
            ],
        )

    def test_the_mirroring_major_is_the_newest_implemented(self) -> None:
        self.assertEqual(validate.mirroring_major({1: self.v1, 2: self.v2}), 2)
        self.v2["x-contract"]["status"] = "proposed"
        self.assertEqual(validate.mirroring_major({1: self.v1, 2: self.v2}), 1)
        self.assertIsNone(validate.mirroring_major({}))


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
    """Qualification cases agree with the schema, their base fixture and Alloy's derived IDs."""

    BASE = {
        "service": {"name": "svc"},
        "gateway": {
            "namespace": "ns",
            "correlation_id": True,
            "otel_endpoint": "http://127.0.0.1:4318/v1/traces",
        },
    }

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
        _write(self.root / "fixtures" / "manifest" / "valid" / "base.json", self.BASE)

    def case(self, length: int, exports: bool | None = None, schema_valid: bool = True) -> dict:
        proxy_id = "a" * length
        return {
            "id": f"id-{length}",
            "schema_valid": schema_valid,
            "producer_exports": length <= 241 if exports is None else exports,
            "derived_resource_ids": [f"{proxy_id}-otel-tracing"],
            "instance": {
                "service": {"name": "svc"},
                "gateway": {"namespace": "ns", "proxy_id": proxy_id, "correlation_id": False},
            },
        }

    def run_doc(self, doc) -> tuple[list[str], int]:
        _write(self.root / "qualification" / "manifest" / "v1" / "cases.json", doc)
        report = validate.Report()
        base_bytes = (self.root / "fixtures" / "manifest" / "valid" / "base.json").read_bytes()
        bases = {
            ("manifest", 1): (
                "fixtures/manifest/valid/base.json",
                hashlib.sha256(base_bytes).hexdigest(),
            )
        }
        with contextlib.redirect_stdout(io.StringIO()), unittest.mock.patch.object(
            validate, "ALLOY_DERIVED_ID_BASES", bases
        ):
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
            "base": "fixtures/manifest/valid/base.json",
            "producer": {"repo": "o/r", "paths": ["src/x.rs"], "commit": "a" * 40},
            "cases": cases,
            **overrides,
        }
        return self.run_doc(doc)

    def assert_one_error(self, cases, message: str, **overrides) -> None:
        errors, checked = self.run_checks(cases, **overrides)
        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn(message, errors[0])

    def test_a_consistent_boundary_pair_passes(self) -> None:
        errors, checked = self.run_checks([self.case(241), self.case(242)])
        self.assertEqual(errors, [])
        self.assertEqual(checked, 2)

    def test_a_wrong_producer_outcome_fails(self) -> None:
        self.assert_one_error([self.case(242, exports=True)], "producer_exports must be false")

    def test_derived_ids_must_be_alloys(self) -> None:
        missing = self.case(242, exports=True)
        del missing["derived_resource_ids"]
        wrong_suffix = self.case(242, exports=True)
        wrong_suffix["derived_resource_ids"] = ["a" * 242 + "-x"]
        default_correlation = self.case(241)
        del default_correlation["instance"]["gateway"]["correlation_id"]
        for case in (missing, wrong_suffix, default_correlation):
            with self.subTest(case=case):
                self.assert_one_error([case], "derived_resource_ids must be Alloy's")

    def test_alloy_derived_ids_follow_health_and_correlation(self) -> None:
        manifest = {
            "service": {"name": "svc"},
            "health": {"path": "/readyz"},
            "gateway": {"proxy_id": "p"},
        }
        self.assertEqual(
            validate.alloy_derived_ids(manifest),
            ["p-upstream", "p-correlation-id", "p-otel-tracing"],
        )
        manifest["gateway"] = {}
        manifest["health"] = None
        self.assertEqual(validate.alloy_derived_ids(manifest), ["svc-correlation-id", "svc-otel-tracing"])
        for bad in ([], {"service": "svc"}, {"service": {"name": "svc"}, "gateway": None},
                    {"service": {"name": ""}}, {"service": {"name": "s"}, "gateway": {"proxy_id": 1}},
                    {"service": {"name": "s"}, "gateway": {"proxy_id": "catalog\n"}},
                    {"service": {"name": "s"}, "gateway": {"proxy_id": "caf\u00e9"}},
                    {"service": {"name": "s"}, "gateway": {"proxy_id": "a" * 255}}):
            with self.subTest(bad=bad):
                self.assertIsNone(validate.alloy_derived_ids(bad))

    def test_a_case_may_vary_only_the_qualified_gateway_fields(self) -> None:
        auth = self.case(241)
        auth["instance"]["auth"] = {"mode": "gateway"}
        self.assert_one_error([auth], "may differ from base only in gateway")
        namespace = self.case(241)
        namespace["instance"]["gateway"]["namespace"] = "other"
        self.assert_one_error([namespace], "gateway.namespace may not differ from base")
        endpoint = self.case(241)
        endpoint["instance"]["gateway"]["otel_endpoint"] = "https://elsewhere"
        self.assert_one_error([endpoint], "gateway.otel_endpoint may not differ from base")
        kept = self.case(241)
        kept["instance"]["gateway"]["otel_endpoint"] = self.BASE["gateway"]["otel_endpoint"]
        errors, checked = self.run_checks([kept])
        self.assertEqual(errors, [])
        self.assertEqual(checked, 1)

    def test_cases_must_be_schema_valid(self) -> None:
        errors, checked = self.run_checks(
            [self.case(255, exports=False), self.case(241, schema_valid=False)]
        )
        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 2, errors)
        self.assertIn("marked schema_valid but fails manifest v1", errors[0])
        self.assertIn("marked not schema_valid but passes manifest v1", errors[1])
        invalid = self.case(241, schema_valid=False)
        invalid["instance"] = []
        self.assert_one_error([invalid], "cases are schema-valid manifests")

    def test_a_proxy_id_alloy_refuses_fails(self) -> None:
        case = self.case(241)
        case["instance"]["gateway"]["proxy_id"] = "catalog\n"
        case["derived_resource_ids"] = ["catalog\n-otel-tracing"]
        self.assert_one_error([case], "valid proxy ID Alloy can derive IDs from")

    def test_the_repository_base_is_the_reviewed_fixture(self) -> None:
        self.assertEqual(
            list(validate.ALLOY_DERIVED_ID_BASES),
            [("service-manifest", 1)],
        )
        path, _ = validate.ALLOY_DERIVED_ID_BASES[("service-manifest", 1)]
        self.assertEqual(path, "fixtures/service-manifest/valid/plain-http.json")

    def test_a_changed_base_fixture_fails(self) -> None:
        base = self.root / "fixtures" / "manifest" / "valid" / "base.json"
        _write(self.root / "qualification" / "manifest" / "v1" / "cases.json", {})
        original = base.read_bytes()
        changed = dict(self.BASE, gateway=dict(self.BASE["gateway"], otel_endpoint="http://otel.internal"))
        doc = {
            "contract": "manifest",
            "contract_version": 1,
            "rule": validate.ALLOY_DERIVED_ID_RULE,
            "edge_resource_id_max_length": 254,
            "base": "fixtures/manifest/valid/base.json",
            "producer": {"repo": "o/r", "paths": ["src/x.rs"], "commit": "a" * 40},
            "cases": [self.case(241)],
        }
        _write(self.root / "qualification" / "manifest" / "v1" / "cases.json", doc)
        bases = {
            ("manifest", 1): ("fixtures/manifest/valid/base.json", hashlib.sha256(original).hexdigest())
        }
        _write(base, changed)
        report = validate.Report()
        with contextlib.redirect_stdout(io.StringIO()), unittest.mock.patch.object(
            validate, "ALLOY_DERIVED_ID_BASES", bases
        ):
            schemas = validate.load_schemas(self.root, report)
            registry = validate.build_registry(schemas)
            before = report.checked
            validate.check_qualifications(self.root, schemas, registry, report)
        self.assertEqual(report.checked - before, 0)
        self.assertEqual(len(report.errors), 1, report.errors)
        self.assertIn("changed since it was reviewed", report.errors[0])

    def test_a_numeric_type_change_is_a_variation(self) -> None:
        self.assertFalse(validate.same_json({"port": 8080}, {"port": 8080.0}))
        self.assertFalse(validate.same_json([1], [True]))
        self.assertTrue(validate.same_json({"a": [1, {"b": "c"}]}, {"a": [1, {"b": "c"}]}))
        case = self.case(241)
        case["instance"]["gateway"]["namespace"] = "ns"
        case["instance"]["service"] = {"name": "svc"}
        case["instance"]["extra"] = 1
        self.assert_one_error([case], "may differ from base only in gateway")

    def test_the_proxy_id_defaults_to_the_service_name(self) -> None:
        case = self.case(241)
        del case["instance"]["gateway"]["proxy_id"]
        case["derived_resource_ids"] = ["svc-otel-tracing"]
        errors, checked = self.run_checks([case])
        self.assertEqual(errors, [])
        self.assertEqual(checked, 1)

    def test_a_case_without_instance_fails(self) -> None:
        case = self.case(241, schema_valid=False)
        del case["instance"]
        self.assert_one_error([case], "instance is required")

    def test_duplicate_and_missing_ids_are_not_counted(self) -> None:
        nameless = self.case(241)
        del nameless["id"]
        errors, checked = self.run_checks([self.case(241), self.case(241), nameless])
        self.assertEqual(checked, 1)
        self.assertEqual(len(errors), 2, errors)
        self.assertIn("duplicate case id", errors[0])
        self.assertIn("id is required", errors[1])

    def test_a_case_id_must_be_printable_ascii(self) -> None:
        for bad in ("\ud800", "a\nb", "caf\u00e9"):
            with self.subTest(bad=bad):
                case = self.case(241)
                case["id"] = bad
                self.assert_one_error([case], "id must be printable ASCII")

    def test_deeply_nested_json_is_reported(self) -> None:
        path = self.root / "qualification" / "manifest" / "v1" / "cases.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[" * 100000 + "]" * 100000, encoding="utf-8")
        report = validate.Report()
        # Whether the C decoder hits the recursion limit depends on the Python
        # build, so force the RecursionError path deterministically.
        with contextlib.redirect_stdout(io.StringIO()):
            schemas = validate.load_schemas(self.root, report)
            registry = validate.build_registry(schemas)
            with unittest.mock.patch.object(validate.json, "loads", side_effect=RecursionError):
                validate.check_qualifications(self.root, schemas, registry, report)
        self.assertEqual(len(report.errors), 1, report.errors)
        self.assertIn("nested too deeply", report.errors[0])

    def test_an_invalid_envelope_counts_no_case(self) -> None:
        for overrides, message in (
            ({"contract_version": True}, "contract_version"),
            ({"contract_version": 2}, "contract_version"),
            ({"producer": {"repo": "o/r", "paths": [], "commit": "a" * 40}}, "producer.paths"),
            ({"producer": {"repo": "o/r", "paths": ["p"], "commit": "abc"}}, "producer.commit"),
            ({"rule": "other"}, "unknown rule"),
            ({"edge_resource_id_max_length": 255}, "must be 254"),
            ({"base": "fixtures/manifest/valid/other.json"}, "base must be"),
            ({"base": "fixtures/manifest/valid/plain-http\u0000.json"}, "base must be"),
            ({"base": None}, "base must be"),
        ):
            with self.subTest(message=message, overrides=overrides):
                errors, checked = self.run_checks([self.case(241)], **overrides)
                self.assertEqual(checked, 0)
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
        _write(self.root / "qualification" / "manifest" / "v1\n" / "cases.json", {})
        (self.root / "qualification" / "empty").mkdir(parents=True)
        _write(self.root / "schemas" / "empty" / "v1.schema.json", _schema("empty", 1, {}))
        errors, _ = self.run_checks([self.case(241)])
        self.assertTrue(any("existing major" in e for e in errors), errors)
        self.assertTrue(any("no schema named 'unknown'" in e for e in errors), errors)
        self.assertTrue(any("empty: an empty qualification directory" in e for e in errors), errors)

    def check_root_only(self) -> list[str]:
        report = validate.Report()
        with contextlib.redirect_stdout(io.StringIO()):
            schemas = validate.load_schemas(self.root, report)
            registry = validate.build_registry(schemas)
            validate.check_qualifications(self.root, schemas, registry, report)
        return report.errors

    def test_a_missing_or_readme_only_qualification_directory_fails(self) -> None:
        errors = self.check_root_only()
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("missing qualification/ directory", errors[0])
        (self.root / "qualification").mkdir()
        (self.root / "qualification" / "README.md").write_text("x\n", encoding="utf-8")
        errors = self.check_root_only()
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("no qualification case sets", errors[0])

    def test_the_repository_cases_pass_and_keep_both_boundary_pairs(self) -> None:
        report = validate.Report()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            schemas = validate.load_schemas(ROOT, report)
            registry = validate.build_registry(schemas)
            validate.check_qualifications(ROOT, schemas, registry, report)
        self.assertEqual(report.errors, [])
        path = ROOT / "qualification" / "service-manifest" / "v1" / "derived-id-limit.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        checked = {
            line.split()[-1]
            for line in output.getvalue().splitlines()
            if line.startswith("  ok (qualification) derived-id-limit.json ")
        }
        self.assertEqual(checked, {case["id"] for case in doc["cases"]})
        base = json.loads((ROOT / doc["base"]).read_text(encoding="utf-8"))
        expected = {
            "no-exporter-241": (241, False, True),
            "no-exporter-242": (242, False, False),
            "explicit-exporter-241": (241, True, True),
            "explicit-exporter-242": (242, True, False),
        }
        cases = {case["id"]: case for case in doc["cases"]}
        self.assertEqual(set(cases), set(expected))
        for case_id, (length, exporter, exports) in expected.items():
            with self.subTest(case_id):
                case = cases[case_id]
                gateway = case["instance"]["gateway"]
                self.assertEqual(len(gateway["proxy_id"]), length)
                self.assertIs(gateway["correlation_id"], False)
                self.assertNotIn("health", case["instance"])
                for key in ("otel_endpoint", "otel_root_sampling_ratio"):
                    if exporter:
                        self.assertEqual(gateway[key], base["gateway"][key])
                    else:
                        self.assertNotIn(key, gateway)
                self.assertIs(case["producer_exports"], exports)


if __name__ == "__main__":
    unittest.main()
