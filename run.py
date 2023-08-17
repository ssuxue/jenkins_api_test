import coverage
import pytest

from .utils.diff_parser import code_diff_map
from .utils.reporter import CustomCoverage


def main():
    m = code_diff_map('./log.diff')
    cov = CustomCoverage()
    # cov = coverage.Coverage()
    cov.start()

    pytest.main(['-v', '-q'])

    cov.stop()
    cov.save()

    report = cov.report(show_missing=True)

    for k, v in enumerate(report):
        print(f'{k} - {v} --> {report[v]}')
    cov.html_report()
    print(m)


if __name__ == '__main__':
    main()
