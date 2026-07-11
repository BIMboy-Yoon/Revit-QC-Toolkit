# -*- coding: utf-8 -*-

"""File exporters for Interior Finish Takeoff reports."""

import codecs
import json
import os
from datetime import datetime

from interior_finish_takeoff.report_html import render_html_report


def export_report_bundle(report_data, output_folder, project_name):
    """Export HTML, CSV, and JSON debug files."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    base_path = os.path.join(
        output_folder,
        build_report_file_stem(project_name)
    )
    html_path = base_path + ".html"
    csv_path = base_path + ".csv"
    json_path = base_path + ".json"

    write_text_file(html_path, render_html_report(report_data))
    write_text_file(csv_path, render_csv_report(report_data))
    write_text_file(json_path, json.dumps(
        report_data,
        ensure_ascii=False,
        indent=2,
        sort_keys=True
    ))
    return {
        "html": html_path,
        "csv": csv_path,
        "json": json_path
    }


def build_report_file_stem(project_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_project_name = sanitize_filename(project_name)
    if not safe_project_name:
        safe_project_name = "Untitled_Project"
    return "Interior_Finish_Takeoff_{0}_{1}".format(
        safe_project_name,
        timestamp
    )


def render_csv_report(report_data):
    lines = []
    _append_section(lines, "Project Summary", [report_data.get("project_summary", {})])
    _append_section(lines, "Settings Summary", report_data.get("settings_summary", []))
    material = report_data.get("material_summary", {})
    _append_section(lines, "Material Summary - By Level", material.get("by_level", []))
    _append_section(lines, "Material Summary - By Material", material.get("by_material", []))
    _append_section(lines, "Material Summary - By Category", material.get("by_category", []))
    _append_section(lines, "Material Summary - By Source Type", material.get("by_source_type", []))
    _append_section(lines, "Room Summary", report_data.get("room_summary", []))
    _append_section(lines, "Baseboard Summary", report_data.get("baseboard_summary", []))
    _append_section(lines, "Difference Summary", report_data.get("difference_summary", []))
    _append_section(lines, "QC Flag Table", report_data.get("qc_flag_table", []))
    _append_section(lines, "Detail Table", report_data.get("detail_table", []))
    return u"\n".join(lines)


def write_text_file(path, content):
    with codecs.open(path, "w", "utf-8") as output_file:
        output_file.write(_to_text(content))


def sanitize_filename(value):
    text = _to_text(value).strip()
    invalid_chars = u'<>:"/\\|?*'
    cleaned = []
    for char in text:
        if char in invalid_chars:
            cleaned.append(u"_")
        elif ord(char) < 32:
            cleaned.append(u"_")
        else:
            cleaned.append(char)
    return u"".join(cleaned).strip(u" .")


def _append_section(lines, title, rows):
    lines.append(_csv_row([title]))
    if not rows:
        lines.append(_csv_row(["No data"]))
        lines.append(u"")
        return
    columns = _collect_columns(rows)
    lines.append(_csv_row(columns))
    for row in rows:
        values = []
        for column in columns:
            values.append(row.get(column, u""))
        lines.append(_csv_row(values))
    lines.append(u"")


def _collect_columns(rows):
    columns = []
    for row in rows:
        for key in sorted(row.keys()):
            if key not in columns:
                columns.append(key)
    return columns


def _csv_row(values):
    escaped = []
    for value in values:
        text = _to_text(value)
        text = text.replace(u'"', u'""')
        escaped.append(u'"{0}"'.format(text))
    return u",".join(escaped)


def _to_text(value):
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return u""
