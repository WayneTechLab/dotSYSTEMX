#!/usr/bin/env python3
"""Read bounded GitHub release and deployment counts; never store provider state."""

import argparse
from datetime import datetime, timezone
import json
import re
import sys
from urllib.request import Request, urlopen


DEFAULT_REPOSITORY = "WayneTechLab/dotSYSTEMX"
REPOSITORY = re.compile(r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+")
NUMBER = r"(?:0|[1-9][0-9]*)"
SOFTWARE_TAG = re.compile(r"v" + NUMBER + r"\." + NUMBER + r"\." + NUMBER +
                          r"(?:-(?:alpha|beta|rc)\.[1-9][0-9]*)?")
MEDIA_TAG = re.compile(r"media-[A-Za-z0-9][A-Za-z0-9.-]*")
API_ROOT = "https://api.github.com/repos/"
PER_PAGE = 100
MAX_PAGES = 10
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
TIMEOUT_SECONDS = 5


class CounterUnavailable(ValueError):
    """A provider result cannot support an exact count."""


def repository_id(value):
    if not isinstance(value, str) or not REPOSITORY.fullmatch(value):
        raise ValueError("Repository must be OWNER/REPO")
    return value


def fetch_page(repository, endpoint, page):
    """Fetch one public GitHub API page without using local credentials."""
    url = (API_ROOT + repository + "/" + endpoint + "?per_page=" + str(PER_PAGE) +
           "&page=" + str(page))
    request = Request(url, headers={"Accept": "application/vnd.github+json",
                                    "User-Agent": "dotSYSTEMX-release-counters"})
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    if len(raw) > MAX_RESPONSE_BYTES:
        raise CounterUnavailable("Provider response exceeded the size limit")
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CounterUnavailable("Provider returned invalid JSON") from error


def collect(repository, endpoint):
    rows = []
    seen = set()
    for page in range(1, MAX_PAGES + 1):
        current = fetch_page(repository, endpoint, page)
        if not isinstance(current, list) or len(current) > PER_PAGE:
            raise CounterUnavailable("Provider returned an invalid page")
        for item in current:
            if (not isinstance(item, dict) or type(item.get("id")) is not int or
                    item["id"] <= 0 or item["id"] in seen):
                raise CounterUnavailable("Provider returned invalid or duplicate records")
            seen.add(item["id"])
            rows.append(item)
        if len(current) < PER_PAGE:
            return rows
    raise CounterUnavailable("Provider result exceeded the pagination limit")


def observed(count):
    return {"state": "observed", "count": count}


def unknown():
    return {"state": "unknown", "count": None}


def snapshot(repository=DEFAULT_REPOSITORY):
    """Return independent observations; a failed endpoint never becomes zero."""
    repository = repository_id(repository)
    result = {"schemaVersion": 1, "repository": repository,
              "source": "GitHub REST API", "observedAt": None,
              "publishedReleases": unknown(), "softwareReleases": unknown(),
              "mediaReleases": unknown(), "otherReleases": unknown(),
              "deploymentRecords": unknown(), "complete": False,
              "meaning": ("Release counts include published GitHub release records only. "
                          "Deployment records count requests, not successful deployments "
                          "or live verification.")}
    try:
        releases = collect(repository, "releases")
        published = []
        for item in releases:
            if type(item.get("draft")) is not bool or not isinstance(item.get("tag_name"), str):
                raise CounterUnavailable("Provider returned invalid release metadata")
            if not item["draft"]:
                published.append(item)
        software = sum(bool(SOFTWARE_TAG.fullmatch(item["tag_name"])) for item in published)
        media = sum(bool(MEDIA_TAG.fullmatch(item["tag_name"])) for item in published)
        result.update(publishedReleases=observed(len(published)),
                      softwareReleases=observed(software), mediaReleases=observed(media),
                      otherReleases=observed(len(published) - software - media))
    except (CounterUnavailable, OSError, TimeoutError, ValueError):
        pass
    try:
        result["deploymentRecords"] = observed(len(collect(repository, "deployments")))
    except (CounterUnavailable, OSError, TimeoutError, ValueError):
        pass
    result["complete"] = (result["publishedReleases"]["state"] == "observed" and
                          result["deploymentRecords"]["state"] == "observed")
    result["observedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read current GitHub release and deployment record counts")
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY, type=repository_id,
                        help="public GitHub OWNER/REPO (default: WayneTechLab/dotSYSTEMX)")
    args = parser.parse_args(argv)
    result = snapshot(args.repository)
    print(json.dumps(result, indent=2))
    return 0 if result["complete"] else 2


if __name__ == "__main__":
    sys.exit(main())
