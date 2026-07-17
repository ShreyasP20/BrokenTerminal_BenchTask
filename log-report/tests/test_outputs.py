import json
import re
from collections import Counter
from pathlib import Path


LOG_PATH = Path("/app/access.log")
REPORT_PATH = Path("/app/report.json")

EXPECTED_KEYS = {
    "total_requests",
    "unique_ips",
    "top_path",
}

REQUEST_PATTERN = re.compile(
    r'"(?:GET|POST|PUT|DELETE|HEAD|PATCH) (?P<path>\S+) HTTP/\d(?:\.\d)?"'
)


def calculate_expected_report():
    paths = Counter()
    ips = set()
    total_requests = 0

    with LOG_PATH.open(encoding="utf-8") as log_file:
        for line_number, raw_line in enumerate(log_file, start=1):
            line = raw_line.strip()

            if not line:
                continue

            fields = line.split()
            assert fields, f"access.log line {line_number} is malformed"

            total_requests += 1
            ips.add(fields[0])

            match = REQUEST_PATTERN.search(line)
            assert match is not None, (
                f"access.log line {line_number} has no valid request path"
            )
            paths[match.group("path")] += 1

    assert paths, "access.log contains no requests"

    highest_count = max(paths.values())
    top_paths = sorted(
        path for path, count in paths.items()
        if count == highest_count
    )

    return {
        "total_requests": total_requests,
        "unique_ips": len(ips),
        "top_path": top_paths[0],
    }


def load_report():
    assert REPORT_PATH.is_file(), (
        "Expected the report at /app/report.json"
    )

    try:
        with REPORT_PATH.open(encoding="utf-8") as report_file:
            report = json.load(report_file)
    except json.JSONDecodeError as error:
        raise AssertionError(
            f"/app/report.json is not valid JSON: {error}"
        ) from error

    assert isinstance(report, dict), (
        "The JSON report must be an object"
    )

    return report


def test_report_has_exact_schema():
    report = load_report()

    assert set(report) == EXPECTED_KEYS, (
        f"Expected exactly these keys: {sorted(EXPECTED_KEYS)}; "
        f"received: {sorted(report)}"
    )

    assert (
        isinstance(report["total_requests"], int)
        and not isinstance(report["total_requests"], bool)
    ), "total_requests must be an integer"

    assert (
        isinstance(report["unique_ips"], int)
        and not isinstance(report["unique_ips"], bool)
    ), "unique_ips must be an integer"

    assert isinstance(report["top_path"], str), (
        "top_path must be a string"
    )


def test_report_values_match_access_log():
    report = load_report()
    expected = calculate_expected_report()

    assert report == expected, (
        f"Incorrect report.\nExpected: {expected}\nReceived: {report}"
    )
