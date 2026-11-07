"""Tests for ci/validate.py: the bounded --fetch-openapi download and the
cross-contract fixture check.

Run with: python -I -m unittest discover -s ci -p 'test_*.py'
Every request goes to a loopback server this test starts; nothing leaves the
runner. Cross-check tests build synthetic schema and fixture trees in a
temporary directory, plus one read-only pass over this repository.
"""

from __future__ import annotations

import contextlib
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
        "x-contract": {"name": name, "version": version, "status": "proposed", "owner": "test"},
        **body,
    }


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


if __name__ == "__main__":
    unittest.main()
