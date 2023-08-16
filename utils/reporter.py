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
        self.cov_data = {}
        data = {
            'Name': [], 'Stmts': [],
            'Miss': [], 'Cover': [],
            'Missing': []
        }
        self.cov_data.update(data)
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

    def record(self, line: str) -> str:
        if '------' not in line and 'Missing' not in line and 'Cover' not in line:
            line = line.replace(', ', ',')
            res = line.split()
            self.cov_data['Name'].append(res[0])
            self.cov_data['Stmts'].append(res[1])
            self.cov_data['Miss'].append(res[2])
            self.cov_data['Cover'].append(res[3])
            self.cov_data['Missing'].append(None if len(res) <= 4 else res[4])

    def get_total_percentage_coverage(self):
        """Returns a float, the total percentage covere"""
        return self.total.pc_covered


class CustomCoverage(Coverage):
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
