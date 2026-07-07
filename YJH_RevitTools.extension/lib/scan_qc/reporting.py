# -*- coding: utf-8 -*-


def _yes_no(value):
    return u"Yes" if value else u"No"


def _found_missing(value):
    return u"Found" if value else u"Missing"


def _missing_standard_names(standards_result):
    missing_items = []
    if not standards_result["plan_template_found"]:
        missing_items.append(standards_result["plan_template_name"])
    if not standards_result["view3d_template_found"]:
        missing_items.append(standards_result["view3d_template_name"])
    if not standards_result["base_3d_view_found"]:
        missing_items.append(standards_result["base_3d_view_name"])
    return missing_items


def _standards_rows(standards_result, location_text):
    return [
        [
            u"{0} in {1}".format(
                standards_result["plan_template_name"],
                location_text
            ),
            _found_missing(standards_result["plan_template_found"])
        ],
        [
            u"{0} in {1}".format(
                standards_result["view3d_template_name"],
                location_text
            ),
            _found_missing(standards_result["view3d_template_found"])
        ],
        [
            u"{0} in {1}".format(
                standards_result["base_3d_view_name"],
                location_text
            ),
            _found_missing(standards_result["base_3d_view_found"])
        ]
    ]


def _render_project_standards(output, title, current_project, warning_prefix):
    output.print_md(title)
    output.print_table(
        table_data=_standards_rows(current_project, u"current project"),
        columns=[u"Standards Item", u"Status"]
    )

    missing_items = _missing_standard_names(current_project)
    if missing_items:
        output.print_md(
            u"> **Warning:** {0} Missing: {1}.".format(
                warning_prefix,
                u", ".join(missing_items)
            )
        )
    else:
        output.print_md("> All required Scan QC standards were found in the project.")


def _render_standards_source(output, standards_source):
    output.print_md("### B. Standards Source File")
    source_rows = [
        [u"Standards RVT Path", standards_source["standards_rvt_path"]],
        [
            u"Standards RVT Exists",
            _yes_no(standards_source["standards_rvt_exists"])
        ]
    ]
    source_rows.extend(_standards_rows(standards_source, u"standards file"))
    output.print_table(
        table_data=source_rows,
        columns=[u"Standards Item", u"Status"]
    )

    if not standards_source["standards_rvt_exists"]:
        output.print_md(
            "> **Warning:** The configured standards RVT file was not found. "
            "The source standards could not be inspected."
        )
        return

    if standards_source["standards_open_error"]:
        output.print_md(
            u"> **Warning:** The standards RVT could not be opened: {0}"
            .format(standards_source["standards_open_error"])
        )
        return

    if standards_source["standards_close_error"]:
        output.print_md(
            u"> **Warning:** The standards RVT was inspected but could not be closed: {0}"
            .format(standards_source["standards_close_error"])
        )

    missing_items = _missing_standard_names(standards_source)
    if missing_items:
        output.print_md(
            u"> **Warning:** Standards source file is incomplete. Missing: {0}. "
            u"No standards were copied or created.".format(u", ".join(missing_items))
        )
    else:
        output.print_md(
            "> All required Scan QC standards were found in the source file."
        )


def _format_names(names):
    return u", ".join(names) if names else u"None"


def _format_copy_failures(copy_failures):
    if not copy_failures:
        return u"None"
    return u" | ".join(
        u"{0}: {1}".format(item[0], item[1])
        for item in copy_failures
    )


def _render_installation_result(output, installation):
    output.print_md("### C. Standards Installation")
    output.print_table(
        table_data=[
            [u"Installation Required", _yes_no(installation["required"])],
            [u"Installation Attempted", _yes_no(installation["attempted"])],
            [u"Already Present", _format_names(installation["already_present"])],
            [u"Installed", _format_names(installation["installed"])],
            [
                u"Missing in Standards Source",
                _format_names(installation["missing_in_source"])
            ],
            [u"Copy Failures", _format_copy_failures(installation["copy_failures"])],
            [
                u"Blocked Reason",
                installation["blocked_reason"] or u"None"
            ],
            [
                u"Transaction Status",
                (
                    u"Not required"
                    if not installation["required"]
                    else (
                        u"Not started"
                        if not installation["attempted"]
                        else (
                            u"Committed"
                            if installation["transaction_committed"]
                            else u"Failed"
                        )
                    )
                )
            ]
        ],
        columns=[u"Installation Item", u"Result"]
    )

    if installation["transaction_error"]:
        output.print_md(
            u"> **Warning:** Standards installation transaction failed: {0}"
            .format(installation["transaction_error"])
        )
    if installation["blocked_reason"]:
        output.print_md(
            u"> **Warning:** Standards installation was blocked: {0}"
            .format(installation["blocked_reason"])
        )
    if installation["missing_in_source"]:
        output.print_md(
            u"> **Warning:** Required standards were missing in the source file: {0}."
            .format(u", ".join(installation["missing_in_source"]))
        )
    if installation["copy_failures"]:
        output.print_md(
            u"> **Warning:** One or more standards could not be copied: {0}"
            .format(_format_copy_failures(installation["copy_failures"]))
        )
    if (
        not installation["required"]
        and not installation["attempted"]
    ):
        output.print_md("> No standards installation was required.")


def _render_standards_check(output, standards_result):
    _render_project_standards(
        output,
        "### A. Current Project Standards - Before Installation",
        standards_result["before"],
        u"Current project standards were incomplete before installation."
    )
    _render_standards_source(
        output,
        standards_result["standards_source"]
    )
    _render_installation_result(
        output,
        standards_result["installation"]
    )
    _render_project_standards(
        output,
        "### D. Current Project Standards - After Installation",
        standards_result["after"],
        u"Current project standards remain incomplete after installation."
    )


def render_scan_qc_summary(
    output,
    selected_wall_count,
    selected_options,
    standards_check
):
    """Render the initial Scan QC selection summary in pyRevit output."""
    selected_output_options = selected_options["selected_output_options"]
    output_options_text = (
        u", ".join(selected_output_options)
        if selected_output_options
        else u"None"
    )

    output.set_title("Revit Scan QC")
    output.print_md("## Scan QC Summary")
    output.print_table(
        table_data=[
            [u"Selected Wall Count", selected_wall_count],
            [u"Selected Point Cloud", selected_options["point_cloud_name"]],
            [u"Point Cloud ElementId", selected_options["point_cloud_id"]],
            [u"Selected Output Options", output_options_text]
        ],
        columns=[u"Item", u"Value"]
    )
    _render_standards_check(output, standards_check)
    output.print_md(
        "> Standards installation phase only: no deviation calculation, point recoloring, "
        "QC working view creation, markers, PDF creation, or CSV export was performed."
    )
