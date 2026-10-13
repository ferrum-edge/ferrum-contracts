"""Tests for the bounded --fetch-openapi download in ci/validate.py.

Run with: python -I -m unittest discover -s ci -p 'test_*.py'
Every request goes to a loopback server this test starts; nothing leaves the
runner.
"""

from __future__ import annotations

import http.server
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
