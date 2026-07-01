import pytest
import json
import os
from datetime import datetime
from utils.data_loader import clear_ids_file
from utils.dashboard_generator import generate_dashboard
from utils.auth import clear_token_cache


def _is_master(config):
    return not hasattr(config, "workerinput")


def pytest_sessionstart(session):
    """Runs on master (and non-xdist) before workers are spawned — guaranteed clear."""
    if _is_master(session.config):
        clear_ids_file()
        clear_token_cache()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Runs on the master after all tests complete. Builds test_results and dashboard."""
    if not _is_master(config):
        return

    stats = terminalreporter.stats
    passed  = [r for r in stats.get("passed",  []) if r.when == "call"]
    failed  = [r for r in stats.get("failed",  []) if r.when == "call"]
    skipped = [r for r in stats.get("skipped", []) if r.when == "call"]
    errors  = [r for r in stats.get("error",   []) if r.when in ("call", "setup")]

    tests = []
    for report in passed + failed + skipped + errors:
        info = {
            "name": report.nodeid,
            "outcome": report.outcome,
            "duration": round(report.duration, 2),
        }
        if report.outcome == "failed" and hasattr(report, "longrepr"):
            info["error"] = str(report.longrepr)
        if hasattr(report, "capstdout") and report.capstdout:
            info["stdout"] = report.capstdout
        tests.append(info)

    end_dt = datetime.now()
    if hasattr(terminalreporter, "_sessionstarttime"):
        start_dt = datetime.fromtimestamp(terminalreporter._sessionstarttime)
    else:
        start_dt = end_dt

    test_results = {
        "start_time": start_dt.isoformat(),
        "end_time": end_dt.isoformat(),
        "duration": round((end_dt - start_dt).total_seconds(), 2),
        "total":   len(passed) + len(failed) + len(skipped) + len(errors),
        "passed":  len(passed),
        "failed":  len(failed) + len(errors),
        "skipped": len(skipped),
        "tests":   tests,
    }

    try:
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "test_results.json"), "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save test results: {e}")

    print("\n" + "=" * 60)
    print("Generating interactive dashboard...")
    print("=" * 60)
    try:
        dashboard_path = generate_dashboard()
        print(f"\n Dashboard URL: file://{dashboard_path}")
    except Exception as e:
        print(f"Warning: Could not generate dashboard: {e}")
