# -*- coding: utf-8 -*-

from System.IO import Directory, Path, StreamWriter
from System.Text import UTF8Encoding

from collectors import to_text
from grouping import get_issue_group_fields


def csv_escape(value):
    text = to_text(value)

    if u"," in text or u'"' in text or u"\n" in text or u"\r" in text:
        text = text.replace(u'"', u'""')
        return u'"{0}"'.format(text)

    return text


def get_export_path(export_folder, file_prefix, report_name, timestamp, extension):
    if not export_folder or not Directory.Exists(export_folder):
        raise Exception(
            u"선택한 Export 폴더를 사용할 수 없습니다: {0}".format(
                export_folder
            )
        )

    return Path.Combine(
        export_folder,
        u"{0}_{1}_{2}.{3}".format(
            file_prefix,
            report_name,
            timestamp,
            extension
        )
    )


def write_csv_row(writer, values):
    writer.WriteLine(u",".join([csv_escape(value) for value in values]))


def write_csv_metadata(writer, version, summary_data, qc_status):
    write_csv_row(writer, [u"Report Version", version])
    write_csv_row(writer, [u"QC Status", qc_status])
    write_csv_row(writer, [u"Checked Sheets", summary_data["checked_sheets"]])
    write_csv_row(writer, [u"Checked Views", summary_data["checked_views"]])
    write_csv_row(writer, [u"Sheet Issues", summary_data["sheet_issues"]])
    write_csv_row(writer, [u"View Issues", summary_data["view_issues"]])
    write_csv_row(writer, [u"Parameter Issues", summary_data["parameter_issues"]])
    write_csv_row(writer, [u"Total Issues", summary_data["total_issues"]])
    write_csv_row(writer, [u"High", summary_data["high_count"]])
    write_csv_row(writer, [u"Medium", summary_data["medium_count"]])
    write_csv_row(writer, [u"Low", summary_data["low_count"]])
    writer.WriteLine(u"")


def save_full_csv(
    issue_rows,
    summary_data,
    qc_status,
    timestamp,
    version,
    file_prefix,
    export_folder
):
    csv_path = get_export_path(
        export_folder,
        file_prefix,
        u"Full",
        timestamp,
        u"csv"
    )
    writer = None

    try:
        writer = StreamWriter(csv_path, False, UTF8Encoding(True))
        write_csv_metadata(writer, version, summary_data, qc_status)
        write_csv_row(
            writer,
            [
                u"Category",
                u"Item Type / Number",
                u"Item Name",
                u"Severity",
                u"QC Item",
                u"Issue Message",
                u"Original Issue Detail"
            ]
        )

        for row in issue_rows:
            qc_item, issue_message = get_issue_group_fields(row)
            write_csv_row(
                writer,
                [row[0], row[1], row[2], row[3], qc_item, issue_message, row[4]]
            )
    finally:
        if writer is not None:
            writer.Close()

    return csv_path


def save_summary_csv(
    group_rows,
    summary_data,
    qc_status,
    timestamp,
    version,
    file_prefix,
    export_folder
):
    csv_path = get_export_path(
        export_folder,
        file_prefix,
        u"Summary",
        timestamp,
        u"csv"
    )
    writer = None

    try:
        writer = StreamWriter(csv_path, False, UTF8Encoding(True))
        write_csv_metadata(writer, version, summary_data, qc_status)
        write_csv_row(
            writer,
            [u"Category", u"Item Type", u"QC Item", u"Severity", u"Count", u"Sample Items"]
        )

        for row in group_rows:
            write_csv_row(writer, row)
    finally:
        if writer is not None:
            writer.Close()

    return csv_path


def export_styled_xlsx(
    issue_rows,
    group_rows,
    summary_data,
    qc_status,
    timestamp,
    version,
    file_prefix,
    export_folder
):
    """v2.4 호출 구조용 placeholder. QC 실행을 중단시키지 않는다."""
    intended_path = get_export_path(
        export_folder,
        file_prefix,
        u"Report",
        timestamp,
        u"xlsx"
    )
    return (
        u"",
        u"Styled XLSX export is not implemented yet. Target: {0}".format(
            intended_path
        )
    )
