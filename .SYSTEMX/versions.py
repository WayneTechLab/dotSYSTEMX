"""Strict public release IDs and ordering; no runtime dependencies."""

import re

NUMBER = r"(?:0|[1-9][0-9]*)"
RELEASE = re.compile(r"(" + NUMBER + r")\.(" + NUMBER + r")\.(" + NUMBER +
                     r")(?:-alpha\.([1-9][0-9]*))?")


def version_id(value):
    if not isinstance(value, str) or not RELEASE.fullmatch(value):
        raise ValueError("Use an exact release version: X.Y.Z or X.Y.Z-alpha.N (N starts at 1)")
    return value


def version_key(value):
    """Numeric alpha order, then the final release for the same base version."""
    match = RELEASE.fullmatch(version_id(value))
    major, minor, patch, alpha = match.groups()
    return (int(major), int(minor), int(patch), alpha is None, int(alpha or 0))


def release_channel(value):
    return "stable" if version_key(value)[3] else "alpha"


def package_version(value):
    """Map the public SemVer alpha ID to Python's canonical PEP 440 spelling."""
    return version_id(value).replace("-alpha.", "a")
