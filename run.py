import coverage
import pytest

from utils.diff_parser import code_diff_map
from utils.reporter import CustomCoverage


def main():
    m = code_diff_map('./log.diff')
    cov = CustomCoverage()
    # cov = coverage.Coverage()
    cov.start()

    pytest.main(['-v', '-q'])

    cov.stop()
    cov.save()

    rate = cov.delta_coverage_rate(m)
    # report = cov.coverage_data(m)
    delta_cov_rate = '{}%'.format(round(rate * 100, 0))
    print('Incremental code coverage rate is {}'.format(delta_cov_rate))
    cov.html_report()


if __name__ == '__main__':
    main()
