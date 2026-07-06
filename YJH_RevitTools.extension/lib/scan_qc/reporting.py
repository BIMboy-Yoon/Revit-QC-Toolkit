# -*- coding: utf-8 -*-


def render_scan_qc_summary(output, selected_wall_count, selected_options):
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
    output.print_md(
        "> Initial UI phase only: no deviation calculation, point recoloring, "
        "view creation, PDF creation, or CSV export was performed."
    )

