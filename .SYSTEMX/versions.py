"""Strict public release IDs and ordering; no runtime dependencies."""

import re

NUMBER = r"(?:0|[1-9][0-9]*)"
RELEASE = re.compile(r"(" + NUMBER + r")\.(" + NUMBER + r")\.(" + NUMBER +
                     r")(?:-(alpha|beta)\.([1-9][0-9]*))?")


def version_id(value):
    if not isinstance(value, str) or not RELEASE.fullmatch(value):
        raise ValueError("Use an exact release version: X.Y.Z, X.Y.Z-alpha.N, or X.Y.Z-beta.N (N starts at 1)")
    return value


def version_key(value):
    """Numeric prerelease order: alpha, beta, then final for one base version."""
    match = RELEASE.fullmatch(version_id(value))
    major, minor, patch, phase, sequence = match.groups()
    rank = {"alpha": 0, "beta": 1, None: 2}[phase]
    return (int(major), int(minor), int(patch), rank, int(sequence or 0))


def release_channel(value):
    match = RELEASE.fullmatch(version_id(value))
    return match.group(4) or "stable"


def package_version(value):
    """Map supported SemVer prerelease IDs to canonical PEP 440 spelling."""
    return version_id(value).replace("-alpha.", "a").replace("-beta.", "b")
