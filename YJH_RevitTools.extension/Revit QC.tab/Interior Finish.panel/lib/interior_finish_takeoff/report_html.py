# -*- coding: utf-8 -*-

"""Single-file HTML report renderer for Interior Finish Takeoff."""


def render_html_report(report_data):
    project = report_data.get("project_summary", {})
    return u"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Interior Finish Takeoff Report</title>
<style>
body {{ font-family: Segoe UI, Arial, sans-serif; margin: 28px; color: #263645; background: #ffffff; }}
h1 {{ font-size: 24px; margin: 0 0 6px 0; }}
h2 {{ font-size: 17px; margin: 28px 0 10px 0; border-bottom: 1px solid #d9dee3; padding-bottom: 6px; }}
.meta {{ color: #5f6f7d; margin-bottom: 20px; }}
.grid {{ display: grid; grid-template-columns: repeat(4, minmax(140px, 1fr)); gap: 10px; margin: 14px 0 20px 0; }}
.metric {{ border: 1px solid #d9dee3; padding: 10px; background: #f7f8fa; }}
.metric .label {{ color: #5f6f7d; font-size: 12px; }}
.metric .value {{ font-size: 18px; font-weight: 600; margin-top: 4px; }}
table {{ border-collapse: collapse; width: 100%; margin: 8px 0 20px 0; font-size: 12px; }}
th, td {{ border: 1px solid #d9dee3; padding: 6px 8px; text-align: left; vertical-align: top; }}
th {{ background: #edf1f4; color: #263645; }}
tr:nth-child(even) td {{ background: #fafbfc; }}
.flag {{ color: #b71c1c; font-weight: 600; }}
</style>
</head>
<body>
<h1>Interior Finish Takeoff Report</h1>
<div class="meta">Project: {project_name}</div>
{project_summary}
{settings_summary}
{material_summary}
{room_summary}
{baseboard_summary}
{difference_summary}
{qc_flag_table}
{detail_table}
</body>
</html>
""".format(
        project_name=_html_escape(project.get("project_name", u"")),
        project_summary=_render_project_summary(project),
        settings_summary=_render_section_table(
            "Settings Summary",
            report_data.get("settings_summary", []),
            ["setting", "value"]
        ),
        material_summary=_render_material_summary(
            report_data.get("material_summary", {})
        ),
        room_summary=_render_section_table(
            "Room Summary",
            report_data.get("room_summary", []),
            [
                "level_name",
                "room_number",
                "room_name",
                "boundary_length_m",
                "area_m2",
                "final_area_m2",
                "count"
            ]
        ),
        baseboard_summary=_render_section_table(
            "Baseboard Summary",
            report_data.get("baseboard_summary", []),
            [
                "level_name",
                "room_number",
                "room_name",
                "baseboard_type",
                "length_m",
                "area_m2",
                "final_area_m2",
                "count"
            ]
        ),
        difference_summary=_render_section_table(
            "Difference Summary: Actual Paint Area vs Interior Rule Area",
            report_data.get("difference_summary", []),
            [
                "scope",
                "actual_paint_area_m2",
                "interior_rule_area_m2",
                "difference_m2"
            ]
        ),
        qc_flag_table=_render_section_table(
            "QC Flag Table",
            report_data.get("qc_flag_table", []),
            [
                "flag",
                "record_type",
                "record_id",
                "level_name",
                "room_number",
                "room_name",
                "category",
                "source_type",
                "area_m2",
                "length_m"
            ],
            flag_column="flag"
        ),
        detail_table=_render_section_table(
            "Detail Table",
            report_data.get("detail_table", []),
            [
                "source",
                "record_type",
                "record_id",
                "level_name",
                "room_number",
                "room_name",
                "category",
                "source_type",
                "material_name",
                "finish_name",
                "area_m2",
                "final_area_m2",
                "length_m",
                "boundary_length_m",
                "flags"
            ],
            flag_column="flags"
        )
    )


def _render_project_summary(project):
    metrics = [
        ("Material Records", project.get("material_record_count", 0)),
        ("Rooms", project.get("room_count", 0)),
        ("Takeoff Results", project.get("takeoff_result_count", 0)),
        ("QC Flags", project.get("qc_flag_count", 0)),
        ("Actual Paint Area m2", project.get("actual_paint_area_m2", 0.0)),
        ("Interior Rule Area m2", project.get("interior_rule_area_m2", 0.0)),
        ("Baseboard Length m", project.get("baseboard_length_m", 0.0)),
        ("Baseboard Area m2", project.get("baseboard_area_m2", 0.0))
    ]
    html = [u"<h2>Project Summary</h2>", u"<div class='grid'>"]
    for label, value in metrics:
        html.append(
            u"<div class='metric'><div class='label'>{0}</div><div class='value'>{1}</div></div>".format(
                _html_escape(label),
                _html_escape(value)
            )
        )
    html.append(u"</div>")
    return u"\n".join(html)


def _render_material_summary(summary):
    html = [u"<h2>Material Summary</h2>"]
    sections = [
        ("By Level", "by_level", ["level_name", "area_m2", "count"]),
        ("By Material", "by_material", ["material_name", "area_m2", "count"]),
        ("By Category", "by_category", ["category", "area_m2", "count"]),
        ("By Source Type", "by_source_type", ["source_type", "area_m2", "count"])
    ]
    for title, key, columns in sections:
        html.append(u"<h3>{0}</h3>".format(_html_escape(title)))
        html.append(_render_table(summary.get(key, []), columns))
    return u"\n".join(html)


def _render_section_table(title, rows, columns, flag_column=None):
    return u"<h2>{0}</h2>\n{1}".format(
        _html_escape(title),
        _render_table(rows, columns, flag_column=flag_column)
    )


def _render_table(rows, columns, flag_column=None):
    if not rows:
        return u"<p>No data.</p>"
    html = [u"<table>", u"<thead><tr>"]
    for column in columns:
        html.append(u"<th>{0}</th>".format(_html_escape(column)))
    html.append(u"</tr></thead><tbody>")
    for row in rows:
        html.append(u"<tr>")
        for column in columns:
            value = row.get(column, u"")
            class_attr = u" class='flag'" if flag_column == column and value else u""
            html.append(
                u"<td{0}>{1}</td>".format(class_attr, _html_escape(value))
            )
        html.append(u"</tr>")
    html.append(u"</tbody></table>")
    return u"\n".join(html)


def _html_escape(value):
    text = _to_text(value)
    return (
        text.replace(u"&", u"&amp;")
        .replace(u"<", u"&lt;")
        .replace(u">", u"&gt;")
        .replace(u'"', u"&quot;")
        .replace(u"'", u"&#39;")
    )


def _to_text(value):
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return u""
