"""Compose bounded static checks without executing any candidate content."""

from pathlib import PurePosixPath

from .bundles import validate_bundle
from .catalog import discover
from .duplicates import compare_skills
from .models import ScanResult, SourceFile, finding
from .policy import validate_policy
from .security import scan_security
from .structure import validate_structure


MAX_SCAN_BYTES = 100 * 1024 * 1024


def validate(files: tuple[SourceFile, ...], policy: dict,
             candidate_sha: str, policy_sha: str) -> ScanResult:
    """Always return an explicit incomplete result when a check cannot finish."""
    findings = []
    try:
        validate_policy(policy)
        if sum(len(file.data) for file in files) > MAX_SCAN_BYTES:
            raise ValueError('scan budget exceeded')
        skills, inventory_findings = discover(files)
        findings.extend(inventory_findings)
        valid_skills = []
        by_name = {skill.name: skill for skill in skills}
        skill_paths = {file.path for skill in skills for file in skill.files}
        for skill in skills:
            structural = validate_structure(skill)
            findings.extend(structural)
            if not any(item.severity == 'error' for item in structural):
                valid_skills.append(skill)
        for file in files:
            path = PurePosixPath(file.path)
            if len(path.parts) == 1 and path.suffix == '.skill' and path.stem in by_name:
                findings.extend(validate_bundle(file, by_name[path.stem]))
        # Exact bundle parity means the source scan covers accepted archive bytes.
        # Unsupported skill binary contents are rejected by structural validation.
        readable = []
        for file in files:
            if file.path.endswith('.skill'):
                continue
            try:
                file.data.decode('utf-8')
            except UnicodeDecodeError:
                continue
            readable.append(file)
        # Classify by original source path, never by a display-normalized finding
        # path: Unicode normalization must not turn a security finding invisible.
        security_findings = scan_security(tuple(f for f in readable if f.path in skill_paths), policy)
        findings.extend(security_findings)
        infrastructure = tuple(f for f in readable if f.path not in skill_paths)
        findings.extend(item for item in scan_security(infrastructure, policy) if item.rule_id == 'SEC001')
        # Similarity explanations contain shared words. Do not derive any such
        # words from skills with detected secrets; these already block the PR.
        secret_roots = {skill.name for skill in skills for item in security_findings
                        if item.rule_id == 'SEC001' and item.path.startswith(skill.name + '/')}
        findings.extend(compare_skills(tuple(skill for skill in valid_skills if skill.name not in secret_roots)))
    except Exception:
        # Exception messages may contain raw candidate text or credentials.
        findings.append(finding('SCAN001', 'error', 'validation', None,
                                'Static scan could not complete. No passing result is available.', b''))
        return ScanResult(tuple(findings), False, candidate_sha, policy_sha)
    unique = {(item.rule_id, item.path, item.line, item.message): item for item in findings}
    return ScanResult(tuple(sorted(unique.values(), key=lambda f: (f.path, f.rule_id, f.line or 0))),
                      True, candidate_sha, policy_sha)
