import coverage
import pytest
import argparse

from utils.diff_parser import code_diff_map
from utils.reporter import CustomCoverage


def get_parser():

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default='log.diff', help='diff with git log path')
    args = parser.parse_args()
    return args
    

def main():
    path = get_parser().path
    m = code_diff_map(path)
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
