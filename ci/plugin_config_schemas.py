#!/usr/bin/env python3
"""Generate the standalone plugin config schemas from Edge's openapi.yaml.

The plugin catalog (vocabularies/plugin-catalog.json) points every built-in
plugin at a component of Edge's `openapi.yaml` (`config_schema.pointer`) and
pins that file by commit and SHA-256 (`config_schema_document`). This script
reads exactly that file and writes one self-contained JSON Schema 2020-12
document per plugin to plugin-config-schemas/<plugin>.schema.json: the
plugin's component plus every component it reaches through `$ref`, copied
under `$defs` with each `#/components/schemas/<Name>` reference rewritten to
`#/$defs/<Name>`. Consumers can then validate a plugin `config` without
parsing `openapi.yaml`.

The script uses only the Python standard library, so it reads YAML with its
own reader. That reader accepts the block and flow YAML subset Edge's
`openapi.yaml` uses (YAML 1.2 core schema scalars) and refuses anything else
(anchors, aliases, tags, complex keys, duplicate keys, tabs in indentation)
instead of guessing. Output is deterministic: the same catalog and the same
`openapi.yaml` bytes always give the same files.

Usage:
  python -I ci/plugin_config_schemas.py --openapi PATH --write   # regenerate
  python -I ci/plugin_config_schemas.py --openapi PATH --check   # compare
  python -I ci/plugin_config_schemas.py --fetch-openapi --check  # download the pinned file

`ci/validate.py --fetch-openapi` runs the same comparison in CI, and also
checks every generated document against the JSON Schema 2020-12 meta-schema.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

OUTPUT_DIR = "plugin-config-schemas"
CATALOG = "vocabularies/plugin-catalog.json"
SCHEMA_DIALECT = "https://json-schema.org/draft/2020-12/schema"
ID_BASE = "https://github.com/ferrum-edge/ferrum-contracts/" + OUTPUT_DIR
GENERATOR = "ci/plugin_config_schemas.py"
COMPONENT_PREFIX = "#/components/schemas/"
DEFS_PREFIX = "#/$defs/"
MAX_OPENAPI_BYTES = 32 * 1024 * 1024


class YamlError(ValueError):
    """The input uses YAML this reader does not accept, or is malformed."""


# ---------------------------------------------------------------- scalars

_NULL = {"", "~", "null", "Null", "NULL"}
_TRUE = {"true", "True", "TRUE"}
_FALSE = {"false", "False", "FALSE"}
_INT_RE = re.compile(r"[-+]?[0-9]+")
_OCT_RE = re.compile(r"0o[0-7]+")
_HEX_RE = re.compile(r"0x[0-9a-fA-F]+")
_FLOAT_RE = re.compile(r"[-+]?(\.[0-9]+|[0-9]+(\.[0-9]*)?)([eE][-+]?[0-9]+)?")
_INF_RE = re.compile(r"[-+]?\.(inf|Inf|INF)")
_NAN_RE = re.compile(r"\.(nan|NaN|NAN)")


def plain_scalar(text: str):
    """Resolve a plain scalar with the YAML 1.2 core schema."""
    if text in _NULL:
        return None
    if text in _TRUE:
        return True
    if text in _FALSE:
        return False
    if _INT_RE.fullmatch(text):
        return int(text)
    if _OCT_RE.fullmatch(text):
        return int(text[2:], 8)
    if _HEX_RE.fullmatch(text):
        return int(text[2:], 16)
    if _FLOAT_RE.fullmatch(text):
        return float(text)
    if _INF_RE.fullmatch(text) or _NAN_RE.fullmatch(text):
        raise YamlError(f"non-finite number {text!r} has no JSON form")
    if text[0] in "&*!|>%@`":
        raise YamlError(f"unsupported plain scalar {text!r} (anchor, alias, tag or reserved indicator)")
    return text


_ESCAPES = {
    "0": "\0", "a": "\a", "b": "\b", "t": "\t", "\t": "\t", "n": "\n", "v": "\v",
    "f": "\f", "r": "\r", "e": "\x1b", " ": " ", '"': '"', "/": "/", "\\": "\\",
    "N": "\x85", "_": "\xa0", "L": " ", "P": " ",
}


def double_quoted(body: str) -> str:
    out = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        i += 1
        if i >= len(body):
            raise YamlError("dangling escape in double-quoted scalar")
        esc = body[i]
        if esc in _ESCAPES:
            out.append(_ESCAPES[esc])
            i += 1
            continue
        width = {"x": 2, "u": 4, "U": 8}.get(esc)
        digits = body[i + 1 : i + 1 + width] if width else ""
        if not width or len(digits) != width or not re.fullmatch(r"[0-9a-fA-F]+", digits):
            raise YamlError(f"invalid escape \\{esc} in double-quoted scalar")
        out.append(chr(int(digits, 16)))
        i += 1 + width
    return "".join(out)


def _fold_quoted_lines(parts: list[str]) -> str:
    """Join the lines of a multi-line quoted scalar (YAML line folding)."""
    pieces = [parts[0].rstrip(" \t")]
    pending_newlines = 0
    for part in parts[1:]:
        stripped = part.strip(" \t")
        if not stripped:
            pending_newlines += 1
            continue
        pieces.append("\n" * pending_newlines if pending_newlines else " ")
        pieces.append(stripped)
        pending_newlines = 0
    if pending_newlines:
        pieces.append("\n" * pending_newlines)
    return "".join(pieces)


def _scan_quoted(text: str, start: int) -> int:
    """Index just past the closing quote of the quoted scalar at `start`, or -1."""
    quote = text[start]
    i = start + 1
    while i < len(text):
        ch = text[i]
        if quote == '"' and ch == "\\":
            i += 2
            continue
        if ch == quote:
            if quote == "'" and i + 1 < len(text) and text[i + 1] == "'":
                i += 2
                continue
            return i + 1
        i += 1
    return -1


def quoted_scalar(token: str) -> str:
    quote = token[0]
    body = token[1:-1]
    if quote == "'":
        return body.replace("''", "'")
    return double_quoted(body)


def strip_comment(text: str) -> str:
    """Drop a trailing ` # comment` that is outside quotes."""
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "'\"" and (i == 0 or text[i - 1] in " \t[{,:"):
            end = _scan_quoted(text, i)
            if end < 0:
                return text
            i = end
            continue
        if ch == "#" and (i == 0 or text[i - 1] in " \t"):
            return text[:i].rstrip()
        i += 1
    return text.rstrip()


# ------------------------------------------------------------------- flow


class _Flow:
    """A recursive-descent reader for one flow collection ([...] or {...})."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.i = 0

    def skip(self) -> None:
        while self.i < len(self.text) and self.text[self.i] in " \t\n":
            self.i += 1

    def parse(self):
        self.skip()
        value = self.node()
        self.skip()
        if self.i != len(self.text):
            raise YamlError(f"unexpected text after flow collection: {self.text[self.i:]!r}")
        return value

    def node(self):
        self.skip()
        if self.i >= len(self.text):
            raise YamlError("unterminated flow collection")
        ch = self.text[self.i]
        if ch == "[":
            return self.sequence()
        if ch == "{":
            return self.mapping()
        if ch in "'\"":
            end = _scan_quoted(self.text, self.i)
            if end < 0:
                raise YamlError("unterminated quoted scalar in flow collection")
            token = self.text[self.i : end]
            self.i = end
            return quoted_scalar(token.replace("\n", " ") if "\n" in token else token)
        start = self.i
        while self.i < len(self.text):
            ch = self.text[self.i]
            if ch in ",]}":
                break
            if ch == ":" and (self.i + 1 >= len(self.text) or self.text[self.i + 1] in " \t\n,]}"):
                break
            self.i += 1
        raw = " ".join(self.text[start : self.i].split())
        if not raw:
            raise YamlError("empty entry in flow collection")
        return plain_scalar(raw)

    def sequence(self) -> list:
        self.i += 1
        items: list = []
        while True:
            self.skip()
            if self.i < len(self.text) and self.text[self.i] == "]":
                self.i += 1
                return items
            items.append(self.node())
            self.skip()
            if self.i < len(self.text) and self.text[self.i] == ",":
                self.i += 1
                continue
            if self.i < len(self.text) and self.text[self.i] == "]":
                self.i += 1
                return items
            raise YamlError("expected , or ] in flow sequence")

    def mapping(self) -> dict:
        self.i += 1
        result: dict = {}
        while True:
            self.skip()
            if self.i < len(self.text) and self.text[self.i] == "}":
                self.i += 1
                return result
            key = self.node()
            if not isinstance(key, str):
                key = json.dumps(key) if not isinstance(key, bool) else str(key).lower()
            self.skip()
            if self.i >= len(self.text) or self.text[self.i] != ":":
                raise YamlError(f"expected : after flow mapping key {key!r}")
            self.i += 1
            self.skip()
            if self.i < len(self.text) and self.text[self.i] in ",}":
                value = None
            else:
                value = self.node()
            if key in result:
                raise YamlError(f"duplicate key {key!r} in flow mapping")
            result[key] = value
            self.skip()
            if self.i < len(self.text) and self.text[self.i] == ",":
                self.i += 1
                continue
            if self.i < len(self.text) and self.text[self.i] == "}":
                self.i += 1
                return result
            raise YamlError("expected , or } in flow mapping")


def _flow_balance(text: str) -> int:
    depth = 0
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in "'\"":
            end = _scan_quoted(text, i)
            if end < 0:
                return depth if depth else 1
            i = end
            continue
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        i += 1
    return depth


# ------------------------------------------------------------------ block

_KEY_RE = re.compile(r"""^(?:"(?:[^"\\]|\\.)*"|'(?:[^']|'')*'|[^\s#'"\[\]{},&*!|>%@`?-][^#]*?|-[^\s#][^#]*?)\s*:(?:\s|$)""")


class _Block:
    def __init__(self, text: str) -> None:
        if "\t" in "".join(line[: len(line) - len(line.lstrip(" \t"))] for line in text.split("\n")):
            raise YamlError("tab in indentation")
        self.lines = text.split("\n")
        self.n = len(self.lines)

    @staticmethod
    def indent(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def significant(self, i: int) -> int:
        """Index of the next line that is neither blank nor a full-line comment."""
        while i < self.n:
            stripped = self.lines[i].strip()
            if stripped and not stripped.startswith("#"):
                return i
            i += 1
        return i

    def parse_document(self):
        i = self.significant(0)
        if i >= self.n:
            return None
        if self.lines[i].strip() in ("---",):
            i = self.significant(i + 1)
        value, i = self.node(i, self.indent(self.lines[i]))
        i = self.significant(i)
        if i < self.n and self.lines[i].strip() not in ("...",):
            raise YamlError(f"line {i + 1}: unexpected content {self.lines[i]!r}")
        return value

    def node(self, i: int, indent: int):
        content = self.lines[i][indent:]
        if content == "?" or content.startswith("? "):
            raise YamlError(f"line {i + 1}: complex mapping keys are not supported")
        if content == "-" or content.startswith("- "):
            return self.sequence(i, indent)
        if _KEY_RE.match(content):
            return self.mapping(i, indent)
        return self.scalar_lines(i, indent, strip_comment(content), indent - 1)

    def mapping(self, i: int, indent: int):
        result: dict = {}
        while True:
            i = self.significant(i)
            if i >= self.n or self.indent(self.lines[i]) != indent:
                break
            content = self.lines[i][indent:]
            if content == "-" or content.startswith("- "):
                break
            if content.startswith("? "):
                raise YamlError(f"line {i + 1}: complex mapping keys are not supported")
            match = _KEY_RE.match(content)
            if not match:
                raise YamlError(f"line {i + 1}: expected a mapping key, got {content!r}")
            raw_key = content[: match.end()].rstrip()
            raw_key = raw_key[:-1].rstrip()
            key = quoted_scalar(raw_key) if raw_key[:1] != "" and raw_key[0] in "'\"" else raw_key
            if raw_key[:1] != "" and raw_key[0] in "&*!":
                raise YamlError(f"line {i + 1}: anchors, aliases and tags are not supported")
            if key in result:
                raise YamlError(f"line {i + 1}: duplicate key {key!r}")
            rest = content[match.end() :]
            value, i = self.value(i, indent, rest)
            result[key] = value
        return result, i

    def value(self, i: int, indent: int, rest: str):
        """The value of a mapping entry at `indent` whose text after `:` is `rest`."""
        text = strip_comment(rest.strip())
        if text[:1] != "" and text[0] in "|>":
            return self.block_scalar(i, indent, text)
        if text:
            return self.scalar_lines(i, indent, text, indent)
        j = self.significant(i + 1)
        if j >= self.n:
            return None, j
        child = self.indent(self.lines[j])
        content = self.lines[j][child:]
        if child > indent:
            return self.node(j, child)
        if child == indent and (content == "-" or content.startswith("- ")):
            return self.sequence(j, indent)
        return None, i + 1

    def sequence(self, i: int, indent: int):
        items: list = []
        while True:
            i = self.significant(i)
            if i >= self.n or self.indent(self.lines[i]) != indent:
                break
            content = self.lines[i][indent:]
            if not (content == "-" or content.startswith("- ")):
                break
            after = content[1:]
            body = after.lstrip(" ")
            if not body or body.startswith("#"):
                j = self.significant(i + 1)
                if j < self.n and self.indent(self.lines[j]) > indent:
                    value, i = self.node(j, self.indent(self.lines[j]))
                else:
                    value, i = None, i + 1
                items.append(value)
                continue
            column = indent + 1 + (len(after) - len(body))
            if body.startswith("- ") or body == "-" or _KEY_RE.match(body):
                # A compact nested collection: re-read this line as if the
                # item started on its own line at `column`.
                self.lines[i] = " " * column + body
                value, i = self.node(i, column)
                items.append(value)
                continue
            text = strip_comment(body)
            if text[:1] != "" and text[0] in "|>":
                value, i = self.block_scalar(i, indent, text)
            else:
                value, i = self.scalar_lines(i, column, text, indent)
            items.append(value)
        return items, i

    def scalar_lines(self, i: int, column: int, text: str, parent: int):
        """A plain, quoted or flow scalar starting on line i; continuation lines
        are those indented deeper than `parent`."""
        if text[:1] != "" and text[0] in "[{":
            collected = text
            j = i + 1
            while _flow_balance(collected) > 0:
                if j >= self.n:
                    raise YamlError(f"line {i + 1}: unterminated flow collection")
                collected += "\n" + strip_comment(self.lines[j].strip())
                j += 1
            return _Flow(collected).parse(), j
        if text[:1] != "" and text[0] in "'\"":
            end = _scan_quoted(text, 0)
            if end == len(text):
                return quoted_scalar(text), i + 1
            if end > 0:
                raise YamlError(f"line {i + 1}: text after a quoted scalar: {text!r}")
            parts = [text[1:]]
            j = i + 1
            while True:
                if j >= self.n:
                    raise YamlError(f"line {i + 1}: unterminated quoted scalar")
                line = self.lines[j]
                probe = text[0] + line
                close = _scan_quoted(probe, 0)
                if close < 0:
                    parts.append(line)
                    j += 1
                    continue
                tail = probe[close:]
                if strip_comment(tail).strip():
                    raise YamlError(f"line {j + 1}: text after a quoted scalar")
                parts.append(probe[1 : close - 1])
                joined = _fold_quoted_lines(parts)
                body = joined
                if text[0] == "'":
                    return body.replace("''", "'"), j + 1
                return double_quoted(body), j + 1
        parts = [text]
        j = i + 1
        end = i + 1
        while j < self.n:
            line = self.lines[j]
            stripped = line.strip()
            if not stripped:
                parts.append("")
                j += 1
                continue
            if self.indent(line) <= parent or stripped.startswith("#"):
                break
            parts.append(strip_comment(stripped))
            j += 1
            end = j
        while parts and parts[-1] == "":
            parts.pop()
        if len(parts) == 1:
            return plain_scalar(text), end
        return _fold_quoted_lines(parts), end

    def block_scalar(self, i: int, indent: int, header: str):
        match = re.fullmatch(r"([|>])([-+]?)([1-9]?)([-+]?)", header)
        if not match or (match.group(2) and match.group(4)):
            raise YamlError(f"line {i + 1}: unsupported block scalar header {header!r}")
        style = match.group(1)
        chomp = match.group(2) or match.group(4)
        explicit = int(match.group(3)) if match.group(3) else 0
        j = i + 1
        body: list[str] = []
        content_indent = indent + explicit if explicit else None
        while j < self.n:
            line = self.lines[j]
            if line.strip() == "":
                body.append("")
                j += 1
                continue
            line_indent = self.indent(line)
            if line_indent <= indent:
                break
            if content_indent is None:
                content_indent = line_indent
            if line_indent < content_indent:
                break
            body.append(line[content_indent:])
            j += 1
        # Trailing blank lines belong to chomping, not to the next node.
        trailing = 0
        while body and body[-1] == "":
            body.pop()
            trailing += 1
        end = j
        if style == "|":
            text = "\n".join(body)
        else:
            text = _fold_block(body)
        if not body:
            text = ""
            result = "\n" * trailing if chomp == "+" else ""
            return result, end
        if chomp == "-":
            return text, end
        if chomp == "+":
            return text + "\n" + "\n" * trailing, end
        return text + "\n", end


def _fold_block(lines: list[str]) -> str:
    """Folded (`>`) block scalar content: join lines of the same indentation
    with a space, keep newlines around blank and more-indented lines."""
    out = ""
    last_more = None  # whether the last non-empty line was more indented
    after_empty = False
    for line in lines:
        if line == "":
            out += "\n"
            after_empty = True
            continue
        more = line[:1] != "" and line[0] in " \t"
        if last_more is None:
            out += line
        elif after_empty:
            # Between two text lines the first break is folded away and
            # each empty line is one newline; next to a more-indented line
            # the break is kept as well.
            out += line if not (more or last_more) else "\n" + line
        elif not more and not last_more:
            out += " " + line
        else:
            out += "\n" + line
        last_more = more
        after_empty = False
    return out


def load_yaml(text: str):
    """Parse a YAML document in the subset described in the module docstring."""
    return _Block(text).parse_document()


# -------------------------------------------------------------- generation


def openapi_components(text: str) -> dict:
    """`components.schemas` of an OpenAPI document."""
    document = load_yaml(text)
    if not isinstance(document, dict):
        raise YamlError("openapi.yaml is not a mapping")
    schemas = document.get("components", {}).get("schemas")
    if not isinstance(schemas, dict):
        raise YamlError("openapi.yaml has no components.schemas mapping")
    return schemas


_COMPONENT_REF_RE = re.compile(r"#/components/schemas/([A-Za-z0-9_.-]+)((?:/[^/]+)*)")


def _component_ref(pointer: str) -> tuple[str, str]:
    """(component name, JSON Pointer suffix inside it) of a component reference."""
    match = _COMPONENT_REF_RE.fullmatch(pointer) if isinstance(pointer, str) else None
    if not match:
        raise ValueError(f"$ref {pointer!r} is not a reference into {COMPONENT_PREFIX}")
    return match.group(1), match.group(2)


def _component_name(pointer: str) -> str:
    name, suffix = _component_ref(pointer)
    if suffix:
        raise ValueError(f"pointer {pointer!r} names a location inside a component")
    return name


def _rewrite(node, refs: set[str]):
    """Copy `node`, rewriting component references to `$defs` references.

    `#/components/schemas/<Name>` becomes `#/$defs/<Name>`, and a reference to
    a location inside a component keeps its suffix
    (`#/components/schemas/<Name>/$defs/x` becomes `#/$defs/<Name>/$defs/x`).
    Any other `$ref` (another document, another components section) is
    refused, so every generated document is self-contained.
    """
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if key == "$ref":
                name, suffix = _component_ref(value)
                refs.add(name)
                out[key] = DEFS_PREFIX + name + suffix
            else:
                out[key] = _rewrite(value, refs)
        return out
    if isinstance(node, list):
        return [_rewrite(item, refs) for item in node]
    return node


def closure(components: dict, root: str) -> dict[str, dict]:
    """Every component reachable from `root` by `$ref`, rewritten, by name."""
    done: dict[str, dict] = {}
    todo = [root]
    while todo:
        name = todo.pop()
        if name in done:
            continue
        if name not in components:
            raise ValueError(f"components.schemas has no {name!r}")
        refs: set[str] = set()
        done[name] = _rewrite(components[name], refs)
        todo.extend(sorted(refs - set(done)))
    return done


def build(catalog: dict, openapi: bytes) -> dict[str, bytes]:
    """{relative output path: file bytes} for every plugin in the catalog."""
    document = catalog["config_schema_document"]
    digest = hashlib.sha256(openapi).hexdigest()
    if digest != document["sha256"]:
        raise ValueError(f"openapi.yaml sha256 {digest} != pinned {document['sha256']}")
    components = openapi_components(openapi.decode("utf-8"))
    files: dict[str, bytes] = {}
    for plugin in sorted(catalog["plugins"], key=lambda p: p["name"]):
        config = plugin.get("config_schema")
        if not config:
            continue
        if config.get("document") != document["path"]:
            raise ValueError(f"{plugin['name']}: config_schema.document is not {document['path']}")
        root = _component_name(config["pointer"])
        defs = closure(components, root)
        source = {
            "repo": document["repo"],
            "ref": document["ref"],
            "commit": document["commit"],
            "path": document["path"],
            "sha256": document["sha256"],
            "pointer": config["pointer"],
        }
        generated = {
            "plugin": plugin["name"],
            "generator": GENERATOR,
            "source": source,
            "config_required_when_enabled": config.get("config_required_when_enabled", False),
        }
        if "scope_constraint" in config:
            generated["scope_constraint"] = config["scope_constraint"]
        doc = {
            "$schema": SCHEMA_DIALECT,
            "$id": f"{ID_BASE}/{plugin['name']}.schema.json",
            "title": f"{plugin['name']} plugin config",
            "description": (
                f"The `config` object of an enabled `{plugin['name']}` plugin, generated from "
                f"{document['repo']} {document['path']} at {document['ref']} ({document['commit']}), "
                f"component {root} and every component it references. Do not edit: run {GENERATOR}. "
                "This is Edge's own configuration schema, governed by Edge's support policy "
                "(docs/versioning.md); the plugin catalog records when Edge requires it."
            ),
            "x-generated": generated,
            "$ref": DEFS_PREFIX + root,
            "$defs": {name: defs[name] for name in sorted(defs)},
        }
        text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        files[f"{OUTPUT_DIR}/{plugin['name']}.schema.json"] = text.encode("utf-8")
    return files


def compare(root: Path, files: dict[str, bytes]) -> list[str]:
    """Differences between `files` and what is committed under OUTPUT_DIR."""
    problems = []
    directory = root / OUTPUT_DIR
    present = {
        f"{OUTPUT_DIR}/{path.name}": path
        for path in (sorted(directory.iterdir()) if directory.is_dir() else [])
        if path.name != "README.md"
    }
    for rel in sorted(set(files) - set(present)):
        problems.append(f"{rel}: missing; run {GENERATOR} --write")
    for rel in sorted(set(present) - set(files)):
        problems.append(f"{rel}: not generated from the catalog; remove it")
    for rel in sorted(set(files) & set(present)):
        if present[rel].read_bytes() != files[rel]:
            problems.append(f"{rel}: differs from the generator output; run {GENERATOR} --write")
    return problems


def write(root: Path, files: dict[str, bytes]) -> None:
    directory = root / OUTPUT_DIR
    directory.mkdir(exist_ok=True)
    for path in directory.iterdir():
        if path.name != "README.md" and f"{OUTPUT_DIR}/{path.name}" not in files:
            path.unlink()
    for rel, data in files.items():
        (root / rel).write_bytes(data)


def fetch(document: dict) -> bytes:
    for key, pattern in (("repo", r"ferrum-edge/[A-Za-z0-9._-]+"), ("commit", r"[0-9a-f]{40}"), ("path", r"[A-Za-z0-9._/-]+")):
        if not re.fullmatch(pattern, document.get(key, "")):
            raise ValueError(f"config_schema_document.{key} is not fetchable")
    url = f"https://raw.githubusercontent.com/{document['repo']}/{document['commit']}/{document['path']}"
    with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310 (fixed host)
        data = response.read(MAX_OPENAPI_BYTES + 1)
    if len(data) > MAX_OPENAPI_BYTES:
        raise ValueError("openapi.yaml exceeds the size limit")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--openapi", type=Path, help="local copy of the pinned Edge openapi.yaml")
    source.add_argument("--fetch-openapi", action="store_true", help="download the pinned file")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the generated files")
    mode.add_argument("--check", action="store_true", help="fail if the committed files differ")
    args = parser.parse_args()
    root = args.root.resolve()
    catalog = json.loads((root / CATALOG).read_text(encoding="utf-8"))
    data = fetch(catalog["config_schema_document"]) if args.fetch_openapi else args.openapi.read_bytes()
    files = build(catalog, data)
    if args.write:
        write(root, files)
        print(f"wrote {len(files)} files to {OUTPUT_DIR}/")
        return 0
    problems = compare(root, files)
    for problem in problems:
        print(problem, file=sys.stderr)
    if not problems:
        print(f"{len(files)} generated files match")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
