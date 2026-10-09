"""Static metadata, manifest, content and local-link checks for one skill."""

from __future__ import annotations

import posixpath
import re
from bisect import bisect_right
from itertools import islice
from urllib.parse import unquote, urlsplit

import yaml

from .models import Finding, Skill, finding


MAX_FRONTMATTER = 8 * 1024
MAX_TEXT_FILE = 1024 * 1024
MAX_BINARY_FILE = 5 * 1024 * 1024
MAX_DESCRIPTION = 1024
_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_TEXT_SUFFIXES = {
    ".md", ".markdown", ".txt", ".yaml", ".yml", ".json", ".toml", ".ini",
    ".cfg", ".conf", ".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs",
    ".ts", ".tsx", ".jsx", ".html", ".css", ".scss", ".sql", ".xml", ".csv",
    ".tsv", ".svg", ".env.example", ".gitignore", ".rst", ".log",
}
_IMAGE_SIGNATURES = {
    ".png": (b"\x89PNG\r\n\x1a\n",),
    ".jpg": (b"\xff\xd8\xff",),
    ".jpeg": (b"\xff\xd8\xff",),
    ".webp": (None,),
}
_ALLOWED_SCHEMES = {"https", "http", "mailto"}


class _UniqueSafeLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader, node, deep=False):
    if not isinstance(node, yaml.MappingNode):
        raise yaml.constructor.ConstructorError(None, None, "expected a mapping", node.start_mark)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(None, None, "unhashable mapping key", key_node.start_mark) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(None, None, f"duplicate key {key!r}", key_node.start_mark)
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def strict_yaml(data: bytes) -> object:
    """Parse UTF-8 YAML safely, rejecting anchors/aliases and duplicate keys."""
    if not isinstance(data, bytes):
        raise ValueError("YAML input must be bytes")
    try:
        source = data.decode("utf-8")
        for token in yaml.scan(source, Loader=_UniqueSafeLoader):
            if isinstance(token, (yaml.tokens.AnchorToken, yaml.tokens.AliasToken)):
                raise ValueError("YAML anchors and aliases are not permitted")
        return yaml.load(source, Loader=_UniqueSafeLoader)
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ValueError("invalid UTF-8 YAML") from exc


def parse_frontmatter(data: bytes) -> tuple[dict, str]:
    """Return strict YAML metadata and UTF-8 body from a Markdown document."""
    try:
        text = data.decode("utf-8")
    except (AttributeError, UnicodeDecodeError) as exc:
        raise ValueError("Markdown is not valid UTF-8") from exc
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        raise ValueError("missing frontmatter opener")
    first_end = text.find("\n") + 1
    close = re.search(r"(?m)^---[ \t]*\r?\n", text[first_end:])
    if not close:
        raise ValueError("missing frontmatter closer")
    yaml_text = text[first_end:first_end + close.start()]
    if len(yaml_text.encode("utf-8")) > MAX_FRONTMATTER:
        raise ValueError("frontmatter exceeds 8 KiB")
    metadata = strict_yaml(yaml_text.encode("utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError("frontmatter must be a mapping")
    body = text[first_end + close.end():]
    if not body.strip():
        raise ValueError("Markdown body is empty")
    return metadata, body


def _error(rule: str, path: str, message: str, line: int | None = None, data: bytes = b"") -> Finding:
    return finding(rule, "error", path, line, message, data)


def _frontmatter_limit(data: bytes) -> bool:
    if not data.startswith(b"---\n") and not data.startswith(b"---\r\n"):
        return False
    first_end = data.find(b"\n") + 1
    close = re.search(rb"(?m)^---[ \t]*\r?\n", data[first_end:])
    return bool(close and close.start() > MAX_FRONTMATTER)


def _webp(data: bytes) -> bool:
    return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"


def _validate_files(skill: Skill, result: list[Finding]) -> tuple[dict[str, bytes], dict[str, str]]:
    file_map: dict[str, bytes] = {}
    texts: dict[str, str] = {}
    root = skill.name
    seen_paths: set[str] = set()
    for source in skill.files:
        path = source.path
        data = source.data
        if source.mode not in {"100644", "100755"}:
            result.append(_error("STR006", str(path), "skill entries must be regular files"))
            continue
        if (not isinstance(path, str) or path.startswith("/") or "\\" in path
                or any(part in ("", ".", "..") for part in path.split("/"))
                or not path.startswith(root + "/")):
            result.append(_error("STR006", str(path), "file path must be a normalized path inside this skill"))
            continue
        if path in seen_paths:
            result.append(_error("STR006", path, "duplicate virtual file path"))
            continue
        seen_paths.add(path)
        if not isinstance(data, bytes):
            result.append(_error("STR007", path, "file content must be bytes"))
            continue
        file_map[path] = data
        suffix = posixpath.splitext(path.lower())[1]
        if suffix in _IMAGE_SIGNATURES:
            if len(data) > MAX_BINARY_FILE:
                result.append(_error("STR008", path, "image exceeds 5 MiB"))
                continue
            try:
                executable = bool(int(str(source.mode), 8) & 0o111)
            except ValueError:
                executable = False
            if executable:
                result.append(_error("STR009", path, "raster image may not have executable permissions"))
                continue
            valid = _webp(data) if suffix == ".webp" else any(data.startswith(sig) for sig in _IMAGE_SIGNATURES[suffix])
            if not valid:
                result.append(_error("STR009", path, "image extension does not match a supported raster signature"))
            continue
        if suffix in _TEXT_SUFFIXES or not suffix or path.lower().endswith('.env.example'):
            if len(data) > MAX_TEXT_FILE:
                result.append(_error("STR008", path, "text file exceeds 1 MiB"))
                continue
            try:
                texts[path] = data.decode("utf-8")
            except UnicodeDecodeError:
                result.append(_error("STR007", path, "text file is not valid UTF-8"))
        else:
            result.append(_error("STR009", path, "unsupported file type"))
    return file_map, texts


def _manifest(skill: Skill, texts: dict[str, str], result: list[Finding]) -> None:
    path = f"{skill.name}/skill-review.yaml"
    text = texts.get(path)
    if text is None:
        result.append(_error("STR010", path, "required review manifest is missing or unreadable"))
        return
    data = text.encode("utf-8")
    try:
        value = strict_yaml(data)
    except ValueError:
        result.append(_error("STR011", path, "review manifest is invalid YAML"))
        return
    if not isinstance(value, dict):
        result.append(_error("STR011", path, "review manifest must be a mapping"))
        return
    def exact_keys(obj, required, where):
        if not isinstance(obj, dict) or set(obj) != set(required):
            result.append(_error("STR012", path, f"{where} has missing or unknown keys"))
            return False
        return True
    if not exact_keys(value, {"schema_version", "purpose", "differentiation", "access", "cases"}, "manifest"):
        return
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        result.append(_error("STR012", path, "schema_version must be 1"))
    for key in ("purpose", "differentiation"):
        if not isinstance(value[key], str) or not value[key].strip():
            result.append(_error("STR012", path, f"{key} must be a nonempty string"))
    access_keys = {"files_read", "files_written", "network_hosts", "tools", "dependencies"}
    if exact_keys(value["access"], access_keys, "access"):
        for key, members in value["access"].items():
            if not isinstance(members, list) or any(not isinstance(member, str) or not member.strip() for member in members):
                result.append(_error("STR012", path, f"access.{key} must be a list of nonempty strings"))
    cases = value["cases"]
    if not isinstance(cases, list) or len(cases) < 2:
        result.append(_error("STR012", path, "cases must contain at least happy-path and boundary"))
        return
    identifiers = []
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not exact_keys(case, {"id", "prompt", "expected", "forbidden"}, label):
            continue
        for key in ("id", "prompt"):
            if not isinstance(case[key], str) or not case[key].strip():
                result.append(_error("STR012", path, f"{label}.{key} must be a nonempty string"))
        identifiers.append(case["id"])
        for key in ("expected", "forbidden"):
            members = case[key]
            if not isinstance(members, list) or any(not isinstance(member, str) or not member.strip() for member in members):
                result.append(_error("STR012", path, f"{label}.{key} must be a list of nonempty strings"))
    if len(identifiers) != len(set(item for item in identifiers if isinstance(item, str))):
        result.append(_error("STR012", path, "case IDs must be distinct"))
    for mandatory in ("happy-path", "boundary"):
        if mandatory not in identifiers:
            result.append(_error("STR012", path, f"required case ID {mandatory} is missing"))


def _destinations(markdown: str):
    """Yield (destination, character offset) for Markdown links and images."""
    def mask(match: re.Match) -> str:
        return "".join("\n" if char == "\n" else " " for char in match.group(0))

    # Mask code while retaining every offset and newline for accurate findings.
    text = re.sub(r"(?ms)^\s{0,3}(?:`{3,}|~{3,})[^\n]*\n.*?^\s{0,3}(?:`{3,}|~{3,})[^\n]*(?:\n|$)", mask, markdown)
    text = re.sub(r"`+[^`\n]*`+", mask, text)
    definitions: dict[str, tuple[str, int]] = {}
    for match in re.finditer(r"(?m)^[ \t]{0,3}\[([^\]\n]+)\]:[ \t]*(?:<([^>\n]+)>|(\S+))", text):
        definitions[match.group(1).strip().casefold()] = (match.group(2) or match.group(3), match.start())
    for destination, offset in definitions.values():
        yield destination, offset
    i = 0
    while i < len(text):
        image = text.startswith("![", i)
        if image:
            open_bracket = i + 1
        elif text[i] == "[" and (i == 0 or text[i - 1] != "!"):
            open_bracket = i
        else:
            i += 1
            continue
        if i > 0 and text[i - 1] == "\\":
            i += 1
            continue
        close = text.find("]", open_bracket + 1)
        if close < 0:
            break
        after = close + 1
        if after < len(text) and text[after] == "(":
            j, depth, quote = after + 1, 0, None
            while j < min(len(text), after + 4097):
                char = text[j]
                if quote:
                    if char == quote and (j == 0 or text[j - 1] != "\\"):
                        quote = None
                elif char in "\"'":
                    quote = char
                elif char == "(":
                    depth += 1
                elif char == ")":
                    if depth == 0:
                        break
                    depth -= 1
                j += 1
            if j < len(text) and text[j] == ')' and not quote and depth == 0:
                inner = text[after + 1:j].strip()
                if inner.startswith("<") and ">" in inner:
                    dest = inner[1:inner.find(">")]
                else:
                    dest = re.split(r"\s+", inner, maxsplit=1)[0] if inner else ""
                if dest:
                    yield dest, after + 1
                i = j + 1
                continue
            raise ValueError('Unclosed or overlong Markdown link destination')
        elif after < len(text) and text[after] == "[":
            end = text.find("]", after + 1)
            if end >= 0:
                label = text[after + 1:end].strip() or text[open_bracket + 1:close].strip()
                entry = definitions.get(label.casefold())
                if entry:
                    yield entry
                i = end + 1
                continue
        else:
            # CommonMark shortcut reference: [label], where a definition exists.
            entry = definitions.get(text[open_bracket + 1:close].strip().casefold())
            if entry:
                yield entry
        i = close + 1


def _check_links(skill: Skill, file_map: dict[str, bytes], texts: dict[str, str], result: list[Finding]) -> None:
    files = set(file_map)
    for source_path, text in texts.items():
        if not source_path.lower().endswith((".md", ".markdown")):
            continue
        try:
            destinations = list(islice(_destinations(text), 2001))
            if len(destinations) > 2000:
                raise ValueError('Too many Markdown links')
        except ValueError:
            result.append(_error('STR015', source_path, 'Malformed link or Markdown link complexity limit exceeded'))
            continue
        newlines = [index for index, char in enumerate(text) if char == '\n']
        for raw, offset in destinations:
            line = bisect_right(newlines, offset) + 1
            decoded = unquote(raw.strip())
            if not decoded:
                continue
            if decoded.startswith("#"):
                continue
            parsed = urlsplit(decoded)
            if parsed.scheme:
                if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
                    result.append(_error("STR013", source_path, "Markdown destination uses a disallowed URL scheme", line))
                continue
            if decoded.startswith("//"):
                result.append(_error("STR013", source_path, "protocol-relative Markdown destinations are disallowed", line))
                continue
            target = parsed.path
            if not target:
                continue
            if "\\" in target or target.startswith("/") or "\x00" in target:
                result.append(_error("STR013", source_path, "local Markdown destination escapes the skill", line))
                continue
            base = posixpath.dirname(source_path)
            normalized = posixpath.normpath(posixpath.join(base, target))
            root = skill.name
            if normalized != root and not normalized.startswith(root + "/"):
                result.append(_error("STR013", source_path, "local Markdown destination escapes the skill", line))
                continue
            if normalized not in files and not any(path.startswith(normalized.rstrip("/") + "/") for path in files):
                result.append(_error("STR014", source_path, "local Markdown destination does not exist", line))


def validate_structure(skill: Skill) -> tuple[Finding, ...]:
    findings: list[Finding] = []
    file_map, texts = _validate_files(skill, findings)
    skill_path = f"{skill.name}/SKILL.md"
    raw = file_map.get(skill_path)
    if raw is None:
        findings.append(_error("STR001", skill_path, "SKILL.md is required"))
    elif len(raw) > MAX_TEXT_FILE:
        findings.append(_error("STR008", skill_path, "text file exceeds 1 MiB"))
    elif _frontmatter_limit(raw):
        findings.append(_error("STR002", skill_path, "frontmatter exceeds 8 KiB"))
    else:
        try:
            metadata, body = parse_frontmatter(raw)
        except ValueError as exc:
            message = str(exc)
            findings.append(_error("STR002", skill_path, message))
        else:
            name, description = metadata.get("name"), metadata.get("description")
            if not isinstance(name, str) or not _NAME.fullmatch(name) or len(name) > 64:
                findings.append(_error("STR003", skill_path, "name must be 1-64 lowercase letters, digits, or single hyphens, and match the skill directory"))
            elif name != skill.name:
                findings.append(_error("STR003", skill_path, "name must match the skill directory"))
            if not isinstance(description, str) or not description.strip() or len(description) > MAX_DESCRIPTION:
                findings.append(_error("STR004", skill_path, "description must be a nonempty string of at most 1024 characters"))
            for key in metadata:
                if key not in {"name", "description", "license", "compatibility", "metadata", "allowed-tools", "argument-hint", "disable-model-invocation"}:
                    findings.append(_error("STR005", skill_path, "unsupported metadata field"))
            for key in ("license", "compatibility", "argument-hint"):
                if key in metadata and (not isinstance(metadata[key], str) or not metadata[key].strip()):
                    findings.append(_error("STR005", skill_path, f"{key} must be a nonempty string"))
            if "disable-model-invocation" in metadata and type(metadata["disable-model-invocation"]) is not bool:
                findings.append(_error("STR005", skill_path, "disable-model-invocation must be a boolean"))
            if ("compatibility" in metadata and isinstance(metadata["compatibility"], str)
                    and len(metadata["compatibility"]) > 500):
                findings.append(_error("STR005", skill_path, "compatibility exceeds 500 characters"))
            if "metadata" in metadata and (not isinstance(metadata["metadata"], dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in metadata["metadata"].items())):
                findings.append(_error("STR005", skill_path, "metadata must map strings to strings"))
            if "allowed-tools" in metadata and (not isinstance(metadata["allowed-tools"], str) or not metadata["allowed-tools"].strip()):
                findings.append(_error("STR005", skill_path, "allowed-tools must be a nonempty space-delimited string"))
    _manifest(skill, texts, findings)
    _check_links(skill, file_map, texts, findings)
    return tuple(findings)
