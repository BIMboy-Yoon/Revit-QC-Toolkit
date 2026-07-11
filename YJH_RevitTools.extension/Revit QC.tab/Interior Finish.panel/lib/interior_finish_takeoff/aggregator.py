# -*- coding: utf-8 -*-

"""Aggregation helpers for Interior Finish Takeoff material records."""

from interior_finish_takeoff.part_handler import (
    PART_POLICY_EXCLUDE_ORIGINAL_IF_PARTS_EXIST,
    PART_POLICY_INCLUDE_BOTH_AND_FLAG,
    PART_POLICY_PREFER_ORIGINAL,
    PART_POLICY_PREFER_PARTS,
    normalize_part_policy_options,
    split_part_and_original_records
)
from interior_finish_takeoff.constants import (
    SOURCE_TYPE_PAINT,
    SOURCE_TYPE_PART_MATERIAL,
    SOURCE_TYPE_TYPE_MATERIAL,
    TARGET_WALL
)
from interior_finish_takeoff.qc_flags import (
    FLAG_PART_AND_ORIGINAL_BOTH_FOUND,
    FLAG_POSSIBLE_DUPLICATE,
    add_flag
)


def apply_part_handling_policy(records, options=None):
    """Apply Part/original duplicate policy to material records.

    Records are plain dictionaries. The function returns a new list and avoids
    mutating caller-owned record dictionaries.
    """
    policy = normalize_part_policy_options(options)
    grouped = split_part_and_original_records(records)
    output = []

    for source_element_id in sorted(grouped.keys()):
        group = grouped[source_element_id]
        part_records = group["part_records"]
        original_records = group["original_records"]
        has_both = bool(part_records and original_records)

        if not has_both:
            output.extend(_copy_records(part_records))
            output.extend(_copy_records(original_records))
            continue

        if policy[PART_POLICY_INCLUDE_BOTH_AND_FLAG]:
            output.extend(_flag_records(part_records, include_review_flag=True))
            output.extend(_flag_records(original_records, include_review_flag=True))
        elif policy[PART_POLICY_PREFER_ORIGINAL]:
            output.extend(_flag_records(original_records, include_review_flag=False))
        elif (
            policy[PART_POLICY_PREFER_PARTS]
            or policy[PART_POLICY_EXCLUDE_ORIGINAL_IF_PARTS_EXIST]
        ):
            output.extend(_flag_records(part_records, include_review_flag=False))
        else:
            output.extend(_flag_records(part_records, include_review_flag=True))
            output.extend(_flag_records(original_records, include_review_flag=True))

    return output


def find_part_original_duplicate_source_ids(records):
    """Return source ids where Part and original records both exist."""
    duplicate_source_ids = []
    grouped = split_part_and_original_records(records)
    for source_element_id in sorted(grouped.keys()):
        group = grouped[source_element_id]
        if group["part_records"] and group["original_records"]:
            duplicate_source_ids.append(source_element_id)
    return duplicate_source_ids


def build_part_policy_summary(records, options=None):
    """Return a JSON-exportable summary for reporting/review UI."""
    policy = normalize_part_policy_options(options)
    duplicate_source_ids = find_part_original_duplicate_source_ids(records)
    return {
        "active_policy": policy["active_policy"],
        "duplicate_source_ids": duplicate_source_ids,
        "duplicate_source_count": len(duplicate_source_ids)
    }


def filter_material_records_by_settings(records, settings):
    """Filter material records based on user include settings."""
    output = []
    include_paint = bool(settings.get("include_paint", True))
    include_type_material = bool(settings.get("include_type_material", True))
    include_parts = bool(settings.get("include_parts", True))
    for record in records:
        source_type = record.get("source_type", u"")
        if source_type == SOURCE_TYPE_PAINT and not include_paint:
            continue
        if source_type == SOURCE_TYPE_TYPE_MATERIAL and not include_type_material:
            continue
        if source_type == SOURCE_TYPE_PART_MATERIAL:
            if not include_parts or not include_type_material:
                continue
        output.append(_copy_record(record))
    return output


def build_report_data(
    project_name,
    settings,
    material_records,
    room_records,
    takeoff_results,
    baseboard_results,
    part_policy_summary=None
):
    """Build the full JSON-exportable report payload."""
    qc_flag_rows = build_qc_flag_rows(
        material_records,
        room_records,
        takeoff_results,
        baseboard_results
    )
    data = {
        "project_summary": build_project_summary(
            project_name,
            material_records,
            room_records,
            takeoff_results,
            baseboard_results,
            qc_flag_rows
        ),
        "settings_summary": build_settings_summary(settings),
        "material_summary": build_material_summary(material_records),
        "room_summary": build_room_summary(room_records, takeoff_results),
        "baseboard_summary": build_baseboard_summary(baseboard_results),
        "difference_summary": build_difference_summary(
            material_records,
            takeoff_results
        ),
        "qc_flag_table": qc_flag_rows,
        "detail_table": build_detail_table(
            material_records,
            room_records,
            takeoff_results,
            baseboard_results
        ),
        "part_policy_summary": part_policy_summary or {},
        "records": {
            "material_records": material_records,
            "room_records": room_records,
            "takeoff_results": takeoff_results,
            "baseboard_results": baseboard_results
        }
    }
    return data


def build_project_summary(
    project_name,
    material_records,
    room_records,
    takeoff_results,
    baseboard_results,
    qc_flag_rows
):
    return {
        "project_name": _to_text(project_name),
        "material_record_count": len(material_records),
        "room_count": len(room_records),
        "takeoff_result_count": len(takeoff_results),
        "baseboard_result_count": len(baseboard_results),
        "qc_flag_count": len(qc_flag_rows),
        "actual_paint_area_m2": _round(sum_actual_paint_area_m2(material_records)),
        "interior_rule_area_m2": _round(
            sum_interior_rule_wall_area_m2(takeoff_results)
        ),
        "baseboard_area_m2": _round(_sum_field(baseboard_results, "area_m2")),
        "baseboard_length_m": _round(_sum_field(baseboard_results, "length_m"))
    }


def build_settings_summary(settings):
    keys = [
        "include_paint",
        "include_type_material",
        "include_parts",
        "part_policy",
        "default_wall_finish_height_mm",
        "default_ceiling_offset_mm",
        "default_waste_rate_wall",
        "default_waste_rate_floor",
        "default_waste_rate_ceiling",
        "default_skirting_height_mm",
        "default_skirting_waste_rate",
        "output_folder",
        "report_format"
    ]
    rows = []
    for key in keys:
        rows.append({
            "setting": key,
            "value": settings.get(key, u"")
        })
    return rows


def build_material_summary(material_records):
    return {
        "by_level": summarize_records(
            material_records,
            ["level_name"],
            ["area_m2"]
        ),
        "by_material": summarize_records(
            material_records,
            ["material_name"],
            ["area_m2"]
        ),
        "by_category": summarize_records(
            material_records,
            ["category"],
            ["area_m2"]
        ),
        "by_source_type": summarize_records(
            material_records,
            ["source_type"],
            ["area_m2"]
        )
    }


def build_room_summary(room_records, takeoff_results):
    room_rows = summarize_records(
        takeoff_results,
        ["level_name", "room_number", "room_name"],
        ["area_m2", "final_area_m2"]
    )
    boundary_by_room = {}
    for room_record in room_records:
        key = _join_key([
            room_record.get("level_name", u""),
            room_record.get("room_number", u""),
            room_record.get("room_name", u"")
        ])
        metadata = room_record.get("metadata", {})
        boundary_by_room[key] = _to_float(metadata.get("boundary_length_m", 0.0))
    for row in room_rows:
        key = _join_key([
            row.get("level_name", u""),
            row.get("room_number", u""),
            row.get("room_name", u"")
        ])
        row["boundary_length_m"] = _round(boundary_by_room.get(key, 0.0))
    return room_rows


def build_baseboard_summary(baseboard_results):
    return summarize_records(
        baseboard_results,
        ["level_name", "room_number", "room_name", "baseboard_type"],
        ["length_m", "area_m2", "final_area_m2"]
    )


def build_difference_summary(material_records, takeoff_results):
    actual_area = sum_actual_paint_area_m2(material_records)
    rule_area = sum_interior_rule_wall_area_m2(takeoff_results)
    return [
        {
            "scope": "Project Total",
            "actual_paint_area_m2": _round(actual_area),
            "interior_rule_area_m2": _round(rule_area),
            "difference_m2": _round(actual_area - rule_area)
        }
    ]


def build_qc_flag_rows(*record_groups):
    rows = []
    for records in record_groups:
        for record in records:
            for flag in record.get("flags", []):
                rows.append({
                    "flag": flag,
                    "record_type": record.get("record_type", u""),
                    "record_id": _record_identifier(record),
                    "level_name": record.get("level_name", u""),
                    "room_number": record.get("room_number", u""),
                    "room_name": record.get("room_name", u""),
                    "category": record.get("category", record.get("target_type", u"")),
                    "source_type": record.get("source_type", u""),
                    "area_m2": _round(record.get("area_m2", 0.0)),
                    "length_m": _round(record.get("length_m", 0.0))
                })
    return rows


def build_detail_table(
    material_records,
    room_records,
    takeoff_results,
    baseboard_results
):
    rows = []
    for record in material_records:
        rows.append(_detail_row(record, "Material"))
    for record in room_records:
        rows.append(_detail_row(record, "Room"))
    for record in takeoff_results:
        rows.append(_detail_row(record, "Finish Rule"))
    for record in baseboard_results:
        rows.append(_detail_row(record, "Baseboard"))
    return rows


def summarize_records(records, group_fields, sum_fields):
    grouped = {}
    for record in records:
        key_values = []
        for field in group_fields:
            key_values.append(_to_text(record.get(field, u"")))
        key = _join_key(key_values)
        if key not in grouped:
            row = {}
            for index, field in enumerate(group_fields):
                row[field] = key_values[index]
            row["count"] = 0
            for field in sum_fields:
                row[field] = 0.0
            grouped[key] = row
        grouped[key]["count"] += 1
        for field in sum_fields:
            grouped[key][field] += _to_float(record.get(field, 0.0))

    rows = []
    for key in sorted(grouped.keys()):
        row = grouped[key]
        for field in sum_fields:
            row[field] = _round(row[field])
        rows.append(row)
    return rows


def sum_actual_paint_area_m2(material_records):
    total = 0.0
    for record in material_records:
        if record.get("source_type") == SOURCE_TYPE_PAINT:
            total += _to_float(record.get("area_m2", 0.0))
    return total


def sum_interior_rule_wall_area_m2(takeoff_results):
    total = 0.0
    for record in takeoff_results:
        if record.get("target_type") == TARGET_WALL:
            total += _to_float(record.get("area_m2", 0.0))
    return total


def _copy_records(records):
    copied = []
    for record in records:
        copied.append(_copy_record(record))
    return copied


def _flag_records(records, include_review_flag):
    flagged = []
    for record in records:
        copied = _copy_record(record)
        flags = add_flag(copied.get("flags", []), FLAG_POSSIBLE_DUPLICATE)
        if include_review_flag:
            flags = add_flag(flags, FLAG_PART_AND_ORIGINAL_BOTH_FOUND)
            metadata = _copy_metadata(copied)
            metadata["review_required"] = True
            metadata["review_reason"] = FLAG_PART_AND_ORIGINAL_BOTH_FOUND
            copied["metadata"] = metadata
        copied["flags"] = flags
        flagged.append(copied)
    return flagged


def _copy_record(record):
    copied = {}
    if isinstance(record, dict):
        copied.update(record)
    return copied


def _copy_metadata(record):
    metadata = record.get("metadata", {})
    copied = {}
    if isinstance(metadata, dict):
        copied.update(metadata)
    return copied


def _detail_row(record, source_label):
    metadata = record.get("metadata", {})
    boundary_length = 0.0
    if isinstance(metadata, dict):
        boundary_length = metadata.get("boundary_length_m", 0.0)
    return {
        "source": source_label,
        "record_type": record.get("record_type", u""),
        "record_id": _record_identifier(record),
        "level_name": record.get("level_name", u""),
        "room_number": record.get("room_number", u""),
        "room_name": record.get("room_name", u""),
        "category": record.get("category", record.get("target_type", u"")),
        "source_type": record.get("source_type", u""),
        "material_name": record.get("material_name", record.get("finish_name", u"")),
        "finish_name": record.get("finish_name", u""),
        "area_m2": _round(record.get("area_m2", 0.0)),
        "final_area_m2": _round(record.get("final_area_m2", 0.0)),
        "length_m": _round(record.get("length_m", 0.0)),
        "boundary_length_m": _round(boundary_length),
        "flags": u", ".join(record.get("flags", []))
    }


def _record_identifier(record):
    for key in ("result_id", "room_id", "element_id", "record_id"):
        value = record.get(key)
        if value not in (None, u"", ""):
            return _to_text(value)
    return u""


def _sum_field(records, field):
    total = 0.0
    for record in records:
        total += _to_float(record.get(field, 0.0))
    return total


def _join_key(values):
    return u"||".join([_to_text(value) for value in values])


def _round(value):
    return round(_to_float(value), 3)


def _to_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def _to_text(value):
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return u""
