import csv
import io
import json
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen


OWNER = "taicortezz"
REPO = "ci-cd-pipeline-analysis"
WORKFLOW_NAME = "CI"
API_BASE_URL = "https://api.github.com"
OUTPUT_DIR = Path("metrics")
CSV_PATH = OUTPUT_DIR / "pipeline-runs.csv"
JSON_PATH = OUTPUT_DIR / "pipeline-runs.json"
MAX_RUNS = 12
DEBUG_GITHUB_API = os.getenv("DEBUG_GITHUB_API") == "1"

FIELDS = [
    "run_id",
    "run_number",
    "workflow_name",
    "commit_sha",
    "commit_message",
    "status",
    "conclusion",
    "workflow_duration_seconds",
    "job_name",
    "job_status",
    "job_conclusion",
    "job_duration_seconds",
    "test_count",
    "test_failures",
    "test_average_duration",
    "created_at",
    "updated_at",
    "run_started_at",
    "html_url",
]


def debug_log(message):
    if DEBUG_GITHUB_API:
        print(f"[github-api-debug] {message}", file=sys.stderr)


def parse_datetime(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def duration_seconds(start, end):
    start_dt = parse_datetime(start)
    end_dt = parse_datetime(end)
    if not start_dt or not end_dt:
        return None
    return int((end_dt - start_dt).total_seconds())


def api_get(path, params=None):
    query = f"?{urlencode(params)}" if params else ""
    url = f"{API_BASE_URL}{path}{query}"
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    debug_log(f"GET {url} token_present={bool(token)}")
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=30) as response:
            debug_log(f"GET {url} status={response.status}")
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        permissions = error.headers.get("X-Accepted-GitHub-Permissions")
        debug_log(
            f"GET {url} status={error.code} "
            f"accepted_permissions={permissions} body={body}"
        )
        raise RuntimeError(
            f"GitHub API error {error.code} for {url}: {body}"
        ) from error
    except URLError as error:
        raise RuntimeError(
            f"Could not connect to GitHub API for {url}: {error}"
        ) from error


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def read_response_body(response):
    return response.read()


def api_download(path):
    url = f"{API_BASE_URL}{path}"
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    debug_log(f"DOWNLOAD {url} token_present={bool(token)}")
    request = Request(url, headers=headers)
    opener = build_opener(NoRedirectHandler)
    try:
        with opener.open(request, timeout=30) as response:
            debug_log(f"DOWNLOAD {url} initial_status={response.status}")
            if response.status == 200:
                return read_response_body(response)
    except HTTPError as error:
        if error.code == 302:
            redirect_url = error.headers.get("Location")
            debug_log(
                f"DOWNLOAD {url} initial_status=302 "
                f"redirect={bool(redirect_url)}"
            )
            if not redirect_url:
                return None

            redirect_request = Request(redirect_url)
            try:
                with urlopen(redirect_request, timeout=30) as response:
                    debug_log(
                        "DOWNLOAD redirected artifact "
                        f"status={response.status}"
                    )
                    return read_response_body(response)
            except HTTPError as redirect_error:
                body = redirect_error.read().decode(
                    "utf-8",
                    errors="replace",
                )
                debug_log(
                    "DOWNLOAD redirected artifact "
                    f"status={redirect_error.code} body={body}"
                )
                return None
            except URLError as redirect_error:
                debug_log(
                    "DOWNLOAD redirected artifact connection_error="
                    f"{redirect_error}"
                )
                return None

        body = error.read().decode("utf-8", errors="replace")
        permissions = error.headers.get("X-Accepted-GitHub-Permissions")
        debug_log(
            f"DOWNLOAD {url} status={error.code} "
            f"accepted_permissions={permissions} body={body}"
        )
        if error.code in {401, 403, 404, 410}:
            return None
        raise RuntimeError(
            f"GitHub API error {error.code} for {url}: {body}"
        ) from error
    except URLError as error:
        raise RuntimeError(
            f"Could not connect to GitHub API for {url}: {error}"
        ) from error


def fetch_workflow_runs():
    data = api_get(
        f"/repos/{OWNER}/{REPO}/actions/runs",
        {"per_page": 100},
    )
    runs = data.get("workflow_runs", [])
    ci_runs = [run for run in runs if run.get("name") == WORKFLOW_NAME]
    sorted_runs = sorted(ci_runs, key=lambda run: run.get("run_number") or 0)
    return sorted_runs[:MAX_RUNS]


def fetch_jobs(run_id):
    jobs = []
    page = 1
    while True:
        data = api_get(
            f"/repos/{OWNER}/{REPO}/actions/runs/{run_id}/jobs",
            {"per_page": 100, "page": page},
        )
        page_jobs = data.get("jobs", [])
        jobs.extend(page_jobs)
        if len(page_jobs) < 100:
            break
        page += 1
    return jobs


def fetch_artifacts(run_id):
    data = api_get(
        f"/repos/{OWNER}/{REPO}/actions/runs/{run_id}/artifacts",
        {"per_page": 100},
    )
    return data.get("artifacts", [])


def parse_optional_number(value, number_type=float):
    if value is None or value == "":
        return None
    try:
        return number_type(value)
    except (TypeError, ValueError):
        return None


def metrics_from_summary(content):
    summary = json.loads(content.decode("utf-8"))
    test_count = parse_optional_number(summary.get("test_count"), int)
    test_failures = parse_optional_number(summary.get("test_failures"), int)
    average_duration = parse_optional_number(
        summary.get("test_average_duration"),
        float,
    )
    return {
        "test_count": test_count,
        "test_failures": test_failures,
        "test_average_duration": average_duration,
    }


def metrics_from_junit(content):
    root = ElementTree.fromstring(content)
    suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
    test_count = sum(int(suite.attrib.get("tests", 0)) for suite in suites)
    failures = sum(int(suite.attrib.get("failures", 0)) for suite in suites)
    errors = sum(int(suite.attrib.get("errors", 0)) for suite in suites)
    total_time = sum(float(suite.attrib.get("time", 0)) for suite in suites)
    average_duration = None
    if test_count:
        average_duration = round(total_time / test_count, 4)

    return {
        "test_count": test_count,
        "test_failures": failures + errors,
        "test_average_duration": average_duration,
    }


def merge_test_metrics(summary_metrics, junit_metrics):
    return {
        "test_count": (
            summary_metrics.get("test_count")
            if summary_metrics.get("test_count") is not None
            else junit_metrics.get("test_count")
        ),
        "test_failures": (
            summary_metrics.get("test_failures")
            if summary_metrics.get("test_failures") is not None
            else junit_metrics.get("test_failures")
        ),
        "test_average_duration": (
            summary_metrics.get("test_average_duration")
            if summary_metrics.get("test_average_duration") is not None
            else junit_metrics.get("test_average_duration")
        ),
    }


def empty_test_metrics():
    return {
        "test_count": None,
        "test_failures": None,
        "test_average_duration": None,
    }


def fetch_test_metrics(run_id, warnings):
    try:
        artifacts = fetch_artifacts(run_id)
    except RuntimeError as error:
        warnings.append(f"Run {run_id}: could not list artifacts: {error}")
        return empty_test_metrics()

    artifact = next(
        (item for item in artifacts if item.get("name") == "test-results"),
        None,
    )
    if not artifact:
        warnings.append(f"Run {run_id}: artifact test-results not found")
        return empty_test_metrics()

    artifact_id = artifact.get("id")
    zip_bytes = api_download(
        f"/repos/{OWNER}/{REPO}/actions/artifacts/{artifact_id}/zip"
    )
    if not zip_bytes:
        warnings.append(
            f"Run {run_id}: artifact test-results could not be downloaded"
        )
        return empty_test_metrics()

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            names = archive.namelist()
            summary_metrics = {}
            junit_metrics = {}

            if "test-summary.json" in names:
                summary_metrics = metrics_from_summary(
                    archive.read("test-summary.json")
                )
            if "test-results.xml" in names:
                junit_metrics = metrics_from_junit(
                    archive.read("test-results.xml")
                )

            if not summary_metrics and not junit_metrics:
                warnings.append(
                    f"Run {run_id}: artifact has no test-summary.json "
                    "or test-results.xml"
                )

            return merge_test_metrics(summary_metrics, junit_metrics)
    except (
        zipfile.BadZipFile,
        KeyError,
        json.JSONDecodeError,
        ElementTree.ParseError,
    ) as error:
        warnings.append(f"Run {run_id}: could not parse artifact: {error}")
        return empty_test_metrics()


def build_rows(runs):
    rows = []
    warnings = []
    for run in runs:
        run_id = run.get("id")
        jobs = fetch_jobs(run_id)
        test_metrics = fetch_test_metrics(run_id, warnings)
        workflow_duration = duration_seconds(
            run.get("run_started_at"),
            run.get("updated_at"),
        )

        head_commit = run.get("head_commit") or {}
        commit_message = head_commit.get("message")
        if commit_message:
            commit_message = commit_message.splitlines()[0]

        for job in jobs:
            rows.append(
                {
                    "run_id": run_id,
                    "run_number": run.get("run_number"),
                    "workflow_name": run.get("name"),
                    "commit_sha": run.get("head_sha"),
                    "commit_message": commit_message,
                    "status": run.get("status"),
                    "conclusion": run.get("conclusion"),
                    "workflow_duration_seconds": workflow_duration,
                    "job_name": job.get("name"),
                    "job_status": job.get("status"),
                    "job_conclusion": job.get("conclusion"),
                    "job_duration_seconds": duration_seconds(
                        job.get("started_at"),
                        job.get("completed_at"),
                    ),
                    "test_count": test_metrics.get("test_count"),
                    "test_failures": test_metrics.get("test_failures"),
                    "test_average_duration": test_metrics.get(
                        "test_average_duration"
                    ),
                    "created_at": run.get("created_at"),
                    "updated_at": run.get("updated_at"),
                    "run_started_at": run.get("run_started_at"),
                    "html_url": run.get("html_url"),
                }
            )

    return rows, warnings


def write_csv(rows):
    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_json(rows):
    JSON_PATH.write_text(
        json.dumps(rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main():
    if not os.getenv("GITHUB_TOKEN"):
        print(
            "GITHUB_TOKEN is not set. Running without authentication; "
            "GitHub API rate limits may be lower.",
            file=sys.stderr,
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    runs = fetch_workflow_runs()
    rows, warnings = build_rows(runs)
    write_csv(rows)
    write_json(rows)

    print(f"Runs processed: {len(runs)}")
    print(f"Jobs processed: {len(rows)}")
    print(f"CSV generated: {CSV_PATH}")
    print(f"JSON generated: {JSON_PATH}")
    if warnings:
        print("Artifact warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("Artifact warnings: none")


if __name__ == "__main__":
    main()
