# -*- coding: utf-8 -*-

# Interior Finish Takeoff review/report entry point.

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
from interior_finish_takeoff.exporters import export_report_bundle
from interior_finish_takeoff.finish_rules import build_room_finish_results
from interior_finish_takeoff.material_reader import read_target_material_records
from interior_finish_takeoff.room_mapper import (
    build_room_mapping_records,
    collect_context_rooms
)


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
output.set_title("Interior Finish Takeoff - Review Result")
doc = revit.doc
uidoc = revit.uidoc
settings, config_path, created = load_or_create_settings(PANEL_DIR)

rooms = collect_context_rooms(doc, uidoc, doc.ActiveView)
room_records = build_room_mapping_records(doc, rooms)
takeoff_results = build_room_finish_results(room_records, settings)
baseboard_results = build_baseboard_results(room_records, settings)

material_records = read_target_material_records(
    doc,
    include_parts=settings.get("include_parts", True)
)
material_records = filter_material_records_by_settings(
    material_records,
    settings
)
part_options = {
    settings.get("part_policy"): True
}
part_policy_summary = build_part_policy_summary(material_records, part_options)
material_records = apply_part_handling_policy(material_records, part_options)

report_data = build_report_data(
    doc.Title,
    settings,
    material_records,
    room_records,
    takeoff_results,
    baseboard_results,
    part_policy_summary
)
export_paths = export_report_bundle(
    report_data,
    settings["output_folder"],
    doc.Title
)

output.print_html(u"<h2>Interior Finish Takeoff Report Created</h2>")
if created:
    output.print_html(u"<p>Default settings file was created automatically.</p>")
output.print_html(
    u"<p><strong>Rooms:</strong> {0}<br>"
    u"<strong>Material Records:</strong> {1}<br>"
    u"<strong>QC Flags:</strong> {2}</p>".format(
        len(room_records),
        len(material_records),
        len(report_data.get("qc_flag_table", []))
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
