import copy
import logging
import sys
from typing import Optional, Iterable, IO, Union, List, Dict, Any

from coverage import Coverage
from coverage.control import override_config
from coverage.exceptions import NoDataError
from coverage.report import SummaryReporter
from coverage.report_core import get_analysis_to_report
from coverage.types import TMorf


class CustomSummaryReporter(SummaryReporter):
    def __init__(self, coverage: Coverage) -> None:
        super().__init__(coverage)
        self.cov_data = {'reporters': []}
        self.percentage = None

    def report(self, morfs: Optional[Iterable[TMorf]], outfile: Optional[IO[str]] = None) -> dict[Any, Any]:
        """Writes a report summarizing coverage statistics per module.

        `outfile` is a text-mode file object to write the summary to.

        """
        self.outfile = outfile or sys.stdout

        self.coverage.get_data().set_query_contexts(self.config.report_contexts)
        for fr, analysis in get_analysis_to_report(self.coverage, morfs):
            self.report_one_file(fr, analysis)

        if not self.total.n_files and not self.skipped_count:
            raise NoDataError("No data to report.")

        if self.output_format == "total":
            self.write(self.total.pc_covered_str)
        else:
            self.tabular_report()

        self.cov_data.update({'pc_covered': self.total.pc_covered})
        return self.cov_data

    def write(self, line: str) -> None:
        """Write a line to the output, adding a newline."""
        assert self.outfile is not None
        self.outfile.write(line.rstrip())
        self.outfile.write("\n")
        self.record(line.rstrip())

    def record(self, line: str):
        if '------' not in line and 'Missing' not in line and 'Cover' not in line:
            line = line.replace(', ', ',')
            res = line.split()

            cov_info = {
                'name': res[0],
                'stmts': res[1],
                'miss': res[2],
                'cover': res[3],
                'missing': None if len(res) <= 4 else self.string2arr(res[4])
            }

            if res[0] == 'TOTAL':
                self.cov_data.update({res[0]: cov_info})
            else:
                self.cov_data.get('reporters').append(cov_info)

    def get_total_percentage_coverage(self):
        """Returns a float, the total percentage covere"""
        return self.total.pc_covered

    def string2arr(self, content: str) -> [Any]:
        contents = content.split(',')
        # nums = copy.deepcopy(contents)
        nums = []

        for idx, val in enumerate(contents):
            if '-' in val:
                vals = val.split('-')
                start = int(vals[0])
                end = int(vals[1]) + 1
                arr = [num for num in range(start, end)]

                # del contents[idx]
                # contents.extend(arr)
                nums.extend(arr)
            else:
                nums.append(int(val))
        return nums


class CustomCoverage(Coverage):

    def __init__(self):
        super().__init__()
        logger = logging.getLogger("logger")
        handler1 = logging.StreamHandler()
        handler1.setLevel(logging.ERROR)
        logger.addHandler(handler1)
        self.logger = logger

    def report(
            self,
            morfs: Optional[Iterable[TMorf]] = None,
            show_missing: Optional[bool] = None,
            ignore_errors: Optional[bool] = None,
            file: Optional[IO[str]] = None,
            omit: Optional[Union[str, List[str]]] = None,
            include: Optional[Union[str, List[str]]] = None,
            skip_covered: Optional[bool] = None,
            contexts: Optional[List[str]] = None,
            skip_empty: Optional[bool] = None,
            precision: Optional[int] = None,
            sort: Optional[str] = None,
            output_format: Optional[str] = None,
    ) -> dict[Any, Any]:
        """Write a textual summary report to `file`.

        Each module in `morfs` is listed, with counts of statements, executed
        statements, missing statements, and a list of lines missed.

        If `show_missing` is true, then details of which lines or branches are
        missing will be included in the report.  If `ignore_errors` is true,
        then a failure while reporting a single file will not stop the entire
        report.

        `file` is a file-like object, suitable for writing.

        `output_format` determines the format, either "text" (the default),
        "markdown", or "total".

        `include` is a list of file name patterns.  Files that match will be
        included in the report. Files matching `omit` will not be included in
        the report.

        If `skip_covered` is true, don't report on files with 100% coverage.

        If `skip_empty` is true, don't report on empty files (those that have
        no statements).

        `contexts` is a list of regular expression strings.  Only data from
        :ref:`dynamic contexts <dynamic_contexts>` that match one of those
        expressions (using :func:`re.search <python:re.search>`) will be
        included in the report.

        `precision` is the number of digits to display after the decimal
        point for percentages.

        All of the arguments default to the settings read from the
        :ref:`configuration file <config>`.

        Returns a float, the total percentage covered.

        .. versionadded:: 4.0
            The `skip_covered` parameter.

        .. versionadded:: 5.0
            The `contexts` and `skip_empty` parameters.

        .. versionadded:: 5.2
            The `precision` parameter.

        .. versionadded:: 7.0
            The `format` parameter.

        """
        self._prepare_data_for_reporting()
        with override_config(
                self,
                ignore_errors=ignore_errors,
                report_omit=omit,
                report_include=include,
                show_missing=show_missing,
                skip_covered=skip_covered,
                report_contexts=contexts,
                skip_empty=skip_empty,
                precision=precision,
                sort=sort,
                format=output_format,
        ):
            reporter = CustomSummaryReporter(self)
            return reporter.report(morfs, outfile=file)

    def get_reports(self, ret: dict[Any, Any]):
        return ret.get('reporters')

    def coverage_data(self, delta_data: dict[Any, Any], show_missing=True) -> dict[Any, Any]:
        ret = self.report(show_missing=show_missing)
        reports = self.get_reports(ret)
        try:
            for idx, rep in enumerate(reports):
                if rep.get('name') in delta_data:
                    rep.update({'delta': delta_data[rep.get('name')]})
                    reports[idx] = rep
                    ret.update({'reporters': reports})
        except AttributeError as e:
            self.logger.error(e)
        return ret

    def delta_coverage_rate(self, delta_data: dict[Any, Any], show_missing=True) -> float:
        ret = self.coverage_data(delta_data, show_missing=show_missing)
        self.logger.info(ret)
        reports = self.get_reports(ret)

        # covered_delta_line_count = 0
        uncovered_delta_line_count = 0
        delta_line_count = 0
        delta_cov = 0

        try:
            for rep in reports:
                delta_line_count += len(rep.get('delta', []))
                uncovered_delta_line_count += len(set(rep.get('delta', [])) & set(rep.get('missing', [])))

            delta_cov = 1 - uncovered_delta_line_count / delta_line_count
        except ZeroDivisionError as e:
            self.logger.error(e)
        except AttributeError as e:
            self.logger.error(e)
        finally:
            return delta_cov
