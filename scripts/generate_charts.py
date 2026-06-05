import csv
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402


CSV_PATH = Path("metrics/pipeline-runs.csv")
OUTPUT_DIR = Path("graphs")


def parse_int(value):
    if value in (None, ""):
        return None
    return int(float(value))


def parse_float(value):
    if value in (None, ""):
        return None
    return float(value)


def load_rows():
    with CSV_PATH.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def unique_runs(rows):
    runs = {}
    for row in rows:
        run_number = parse_int(row["run_number"])
        if run_number not in runs:
            runs[run_number] = row
    return [runs[key] for key in sorted(runs)]


def save_chart(path):
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()


def plot_workflow_duration(runs):
    run_numbers = [parse_int(row["run_number"]) for row in runs]
    durations = [parse_float(row["workflow_duration_seconds"]) for row in runs]

    plt.figure(figsize=(10, 5))
    plt.plot(run_numbers, durations, marker="o", color="#2563eb")
    plt.title("Workflow duration by execution")
    plt.xlabel("Execution / run number")
    plt.ylabel("Duration (seconds)")
    plt.xticks(run_numbers)
    plt.grid(axis="y", alpha=0.3)
    save_chart(OUTPUT_DIR / "workflow-duration.png")


def plot_job_duration(rows):
    labels = []
    durations = []
    colors = []
    palette = {
        "ci": "#2563eb",
        "lint": "#16a34a",
        "tests": "#dc2626",
        "quality": "#9333ea",
    }

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            parse_int(row["run_number"]) or 0,
            row["job_name"] or "",
        ),
    )
    for row in sorted_rows:
        duration = parse_float(row["job_duration_seconds"])
        if duration is None:
            continue
        job_name = row["job_name"]
        labels.append(f"#{row['run_number']} {job_name}")
        durations.append(duration)
        colors.append(palette.get(job_name, "#64748b"))

    plt.figure(figsize=(12, 6))
    plt.bar(labels, durations, color=colors)
    plt.title("Job duration by execution")
    plt.xlabel("Execution and job")
    plt.ylabel("Duration (seconds)")
    plt.xticks(rotation=60, ha="right")
    plt.grid(axis="y", alpha=0.3)
    save_chart(OUTPUT_DIR / "job-duration.png")


def plot_success_failure(runs):
    conclusions = [
        row["conclusion"] or "unknown"
        for row in runs
    ]
    counts = Counter(conclusions)
    labels = list(counts.keys())
    values = [counts[label] for label in labels]
    colors = [
        "#16a34a" if label == "success" else "#dc2626"
        for label in labels
    ]

    plt.figure(figsize=(7, 5))
    plt.bar(labels, values, color=colors)
    plt.title("Success and failure rate")
    plt.xlabel("Conclusion")
    plt.ylabel("Runs")
    plt.grid(axis="y", alpha=0.3)
    for index, value in enumerate(values):
        plt.text(index, value + 0.05, str(value), ha="center")
    save_chart(OUTPUT_DIR / "success-failure.png")


def plot_tests_vs_duration(runs):
    points = [
        (
            parse_int(row["run_number"]),
            parse_int(row["test_count"]),
            parse_float(row["workflow_duration_seconds"]),
        )
        for row in runs
        if row["test_count"] and row["workflow_duration_seconds"]
    ]

    plt.figure(figsize=(9, 5))
    if points:
        run_numbers, test_counts, durations = zip(*points)
        plt.scatter(test_counts, durations, color="#ea580c", s=70)
        for run_number, test_count, duration in points:
            plt.annotate(
                f"#{run_number}",
                (test_count, duration),
                textcoords="offset points",
                xytext=(6, 6),
            )
    else:
        plt.text(
            0.5,
            0.5,
            "No test_count data available",
            ha="center",
            va="center",
        )

    plt.title("Test count vs workflow duration")
    plt.xlabel("Test count")
    plt.ylabel("Workflow duration (seconds)")
    plt.grid(alpha=0.3)
    save_chart(OUTPUT_DIR / "tests-vs-duration.png")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    runs = unique_runs(rows)

    plot_workflow_duration(runs)
    plot_job_duration(rows)
    plot_success_failure(runs)
    plot_tests_vs_duration(runs)

    print("Generated charts:")
    print(OUTPUT_DIR / "workflow-duration.png")
    print(OUTPUT_DIR / "job-duration.png")
    print(OUTPUT_DIR / "success-failure.png")
    print(OUTPUT_DIR / "tests-vs-duration.png")


if __name__ == "__main__":
    main()
