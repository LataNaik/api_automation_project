import pytest
import json
import os
from datetime import datetime
from utils.data_loader import clear_ids_file
from utils.dashboard_generator import generate_dashboard

# Store test results
test_results = {
    "start_time": None,
    "end_time": None,
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "tests": []
}

@pytest.fixture(scope="session", autouse=True)
def setup_test_session():
    """
    Pytest fixture that runs once before all tests.
    Clears the ids.txt file to ensure fresh test execution.
    """
    clear_ids_file()
    test_results["start_time"] = datetime.now().isoformat()
    yield
    test_results["end_time"] = datetime.now().isoformat()

    # Save test results to JSON
    try:
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        results_file = os.path.join(output_dir, "test_results.json")

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save test results: {e}")

    # Generate dashboard after all tests complete
    print("\n" + "="*60)
    print("Generating interactive dashboard...")
    print("="*60)
    try:
        dashboard_path = generate_dashboard()
        print(f"\n📊 Dashboard URL: file://{dashboard_path}")
    except Exception as e:
        print(f"Warning: Could not generate dashboard: {e}")

def pytest_runtest_logreport(report):
    """Hook to capture test results"""
    if report.when == "call":
        test_results["total"] += 1

        test_info = {
            "name": report.nodeid,
            "outcome": report.outcome,
            "duration": round(report.duration, 2)
        }

        # Capture stdout (print statements from tests)
        if hasattr(report, 'capstdout') and report.capstdout:
            test_info["stdout"] = report.capstdout

        # Capture stderr
        if hasattr(report, 'capstderr') and report.capstderr:
            test_info["stderr"] = report.capstderr

        if report.outcome == "passed":
            test_results["passed"] += 1
        elif report.outcome == "failed":
            test_results["failed"] += 1
            test_info["error"] = str(report.longrepr) if hasattr(report, 'longrepr') else "Unknown error"
        elif report.outcome == "skipped":
            test_results["skipped"] += 1

        test_results["tests"].append(test_info)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture stdout/stderr for each test"""
    outcome = yield
    report = outcome.get_result()

    if call.when == "call":
        # Capture stdout
        if hasattr(item, '_captured_stdout'):
            report.capstdout = item._captured_stdout
        # Capture stderr
        if hasattr(item, '_captured_stderr'):
            report.capstderr = item._captured_stderr


@pytest.fixture(autouse=True)
def capture_test_output(request, capfd):
    """Fixture to capture test output"""
    yield
    captured = capfd.readouterr()
    request.node._captured_stdout = captured.out
    request.node._captured_stderr = captured.err
