import os
import sys
import datetime as dt


def main() -> int:
    try:
        import pytest  # type: ignore
    except ImportError:
        print("pytest is not installed. Please install dev dependencies.")
        return 1

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(project_root)

    reports_root = os.path.join(project_root, "reports")
    os.makedirs(reports_root, exist_ok=True)

    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    report_dir = os.path.join(reports_root, timestamp)
    os.makedirs(report_dir, exist_ok=True)

    junit_xml = os.path.join(report_dir, "junit.xml")
    cov_html_dir = os.path.join(report_dir, "coverage-html")

    pytest_args = [
        "-q",
        f"--junitxml={junit_xml}",
        "--cov=app",
        f"--cov-report=html:{cov_html_dir}",
        "--cov-report=term",
        "tests",
    ]

    print("Running pytest with reports...")
    print("Reports directory:", report_dir)
    ret = pytest.main(pytest_args)
    if ret == 0:
        print("Success. Reports generated:")
        print("- JUnit XML:", junit_xml)
        print("- Coverage HTML:", os.path.join(cov_html_dir, "index.html"))
    else:
        print("Tests failed. Reports still generated:")
        print("- JUnit XML:", junit_xml)
        print("- Coverage HTML:", os.path.join(cov_html_dir, "index.html"))
    return ret


if __name__ == "__main__":
    sys.exit(main())


