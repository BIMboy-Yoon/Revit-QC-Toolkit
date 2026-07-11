# -*- coding: utf-8 -*-

# Interior Finish Takeoff read-only run entry point.

import os
import sys

from pyrevit import revit, script


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PANEL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
PANEL_LIB_DIR = os.path.join(PANEL_DIR, "lib")

if PANEL_LIB_DIR not in sys.path:
    sys.path.insert(0, PANEL_LIB_DIR)


from interior_finish_takeoff.aggregator import (
    apply_part_handling_policy,
    build_part_policy_summary,
    build_report_data,
    filter_material_records_by_settings
)
from interior_finish_takeoff.baseboard import build_baseboard_results
from interior_finish_takeoff.config import load_or_create_settings
from interior_finish_takeoff.constants import TARGET_BASEBOARD
from interior_finish_takeoff.exporters import export_report_bundle
from interior_finish_takeoff.finish_rules import build_room_finish_results
from interior_finish_takeoff.material_reader import read_target_material_records
from interior_finish_takeoff.room_mapper import (
    build_room_mapping_records,
    collect_rooms_by_scope
)
from interior_finish_takeoff.ui_forms import show_run_takeoff_options_dialog


def run_step(step_name, func):
    try:
        return func()
    except Exception as error:
        output.print_html(
            u"<h2>Interior Finish Takeoff Failed</h2>"
            u"<p><strong>Failed Step:</strong> {0}</p>"
            u"<pre>{1}</pre>".format(
                _html_escape(step_name),
                _html_escape(error)
            )
        )
        script.exit()


def apply_run_options(settings, run_options):
    runtime_settings = {}
    runtime_settings.update(settings)
    runtime_settings["include_paint"] = bool(run_options["include_paint"])
    runtime_settings["include_type_material"] = bool(
        run_options["include_type_material"]
    )
    runtime_settings["include_parts"] = bool(run_options["include_parts"])
    runtime_settings["part_policy"] = run_options["part_policy"]
    return runtime_settings


def filter_results_by_targets(takeoff_results, baseboard_results, target_types):
    filtered_takeoff = []
    for record in takeoff_results:
        if record.get("target_type") in target_types:
            filtered_takeoff.append(record)

    filtered_baseboard = []
    if "WALL" in target_types or TARGET_BASEBOARD in target_types:
        filtered_baseboard = baseboard_results
    return filtered_takeoff, filtered_baseboard


def open_report(path):
    try:
        os.startfile(path)
        return u"Opened"
    except Exception as error:
        return u"Open failed: {0}".format(_to_text(error))


def print_summary(report_data, export_paths, open_status, run_options):
    project_summary = report_data.get("project_summary", {})
    output.print_html(u"<h2>Interior Finish Takeoff Complete</h2>")
    output.print_html(
        u"<p><strong>Scope:</strong> {0}<br>"
        u"<strong>Categories:</strong> {1}<br>"
        u"<strong>Material Sources:</strong> {2}<br>"
        u"<strong>Part Policy:</strong> {3}</p>".format(
            _html_escape(run_options["scope"]),
            _html_escape(u", ".join(run_options["target_types"])),
            _html_escape(_format_material_sources(run_options)),
            _html_escape(run_options["part_policy"])
        )
    )
    output.print_html(
        u"<p><strong>Rooms:</strong> {0}<br>"
        u"<strong>Material Records:</strong> {1}<br>"
        u"<strong>Takeoff Results:</strong> {2}<br>"
        u"<strong>Baseboard Results:</strong> {3}<br>"
        u"<strong>QC Flags:</strong> {4}</p>".format(
            project_summary.get("room_count", 0),
            project_summary.get("material_record_count", 0),
            project_summary.get("takeoff_result_count", 0),
            project_summary.get("baseboard_result_count", 0),
            project_summary.get("qc_flag_count", 0)
        )
    )
    output.print_html(u"<ul>")
    for label in ("html", "csv", "json"):
        output.print_html(
            u"<li><strong>{0}</strong>: {1}</li>".format(
                label.upper(),
                _html_escape(export_paths[label])
            )
        )
    output.print_html(u"</ul>")
    output.print_html(
        u"<p><strong>Report Open:</strong> {0}</p>".format(
            _html_escape(open_status)
        )
    )


def _format_material_sources(run_options):
    labels = []
    if run_options["include_type_material"]:
        labels.append("Type/Layer")
    if run_options["include_paint"]:
        labels.append("Paint")
    if not labels:
        return "None"
    return ", ".join(labels)


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


output = script.get_output()
output.set_title("Interior Finish Takeoff - Run Takeoff")
doc = revit.doc
uidoc = revit.uidoc

settings_data = run_step(
    "1. Settings Load",
    lambda: load_or_create_settings(PANEL_DIR)
)
settings, config_path, created = settings_data

run_options = run_step(
    "2-5. Scope / Category / Material Source / Part Policy Selection",
    lambda: show_run_takeoff_options_dialog(settings)
)
if run_options is None:
    output.print_html(u"<h2>Interior Finish Takeoff</h2><p>Run cancelled.</p>")
    script.exit()
if not run_options["target_types"]:
    output.print_html(
        u"<h2>Interior Finish Takeoff</h2>"
        u"<p>No category selected. Run cancelled.</p>"
    )
    script.exit()

runtime_settings = apply_run_options(settings, run_options)

material_records = run_step(
    "6. Actual Material Collector",
    lambda: read_target_material_records(
        doc,
        include_parts=runtime_settings.get("include_parts", True),
        target_types=run_options["target_types"]
    )
)
material_records = run_step(
    "6. Material Source Filter",
    lambda: filter_material_records_by_settings(
        material_records,
        runtime_settings
    )
)

room_records = run_step(
    "7. Room Collection / Mapping",
    lambda: build_room_mapping_records(
        doc,
        collect_rooms_by_scope(
            doc,
            uidoc,
            doc.ActiveView,
            run_options["scope"]
        )
    )
)
takeoff_results = run_step(
    "7. Room Rule Calculator",
    lambda: build_room_finish_results(room_records, runtime_settings)
)
baseboard_results = run_step(
    "7. Baseboard Calculator",
    lambda: build_baseboard_results(room_records, runtime_settings)
)
takeoff_results, baseboard_results = run_step(
    "7. Category Result Filter",
    lambda: filter_results_by_targets(
        takeoff_results,
        baseboard_results,
        run_options["target_types"]
    )
)

part_options = {runtime_settings.get("part_policy"): True}
part_policy_summary = run_step(
    "8. Part Policy Duplicate Check",
    lambda: build_part_policy_summary(material_records, part_options)
)
material_records = run_step(
    "8. Aggregator - Part Policy",
    lambda: apply_part_handling_policy(material_records, part_options)
)
report_data = run_step(
    "8. Aggregator - Report Data",
    lambda: build_report_data(
        doc.Title,
        runtime_settings,
        material_records,
        room_records,
        takeoff_results,
        baseboard_results,
        part_policy_summary
    )
)

export_paths = run_step(
    "9. HTML/CSV/JSON Export",
    lambda: export_report_bundle(
        report_data,
        runtime_settings["output_folder"],
        doc.Title
    )
)
open_status = u"Skipped"
if run_options["open_report"]:
    open_status = run_step(
        "10. Open Report",
        lambda: open_report(export_paths["html"])
    )

if created:
    output.print_html(
        u"<p>Default settings file was created automatically: {0}</p>".format(
            _html_escape(config_path)
        )
    )
print_summary(report_data, export_paths, open_status, run_options)
