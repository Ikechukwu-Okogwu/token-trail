"""Log utilities for localtest - save test results to result_log."""
from datetime import datetime
from pathlib import Path


def test_log(test_project_name: str, test_result: str) -> str:
    """Save test result to result_log with filename date-test_project-number.txt.

    Number is auto-incremented to avoid overwriting same-day logs for the same project.

    Args:
        test_project_name: Name of the test project (e.g. run_analysis_on_specified_assignment)
        test_result: Content to write to the log file

    Returns:
        Path to the saved log file
    """
    script_dir = Path(__file__).resolve().parent
    result_log_dir = script_dir / "result_log"
    result_log_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    prefix = f"{date_str}-{test_project_name}"
    pattern = f"{prefix}-*.txt"

    existing = list(result_log_dir.glob(pattern))
    numbers = []
    for p in existing:
        try:
            num = int(p.stem.split("-")[-1])
            numbers.append(num)
        except (ValueError, IndexError):
            pass
    next_num = max(numbers, default=0) + 1

    filename = f"{prefix}-{next_num}.txt"
    filepath = result_log_dir / filename
    filepath.write_text(test_result, encoding="utf-8")
    return str(filepath)
