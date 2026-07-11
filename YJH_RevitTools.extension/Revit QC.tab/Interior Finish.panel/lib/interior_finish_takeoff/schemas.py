# -*- coding: utf-8 -*-

"""JSON-exportable schema factories for Interior Finish Takeoff.

These factories intentionally return plain dictionaries instead of dataclasses.
They are compatible with IronPython/pyRevit and avoid Revit API dependencies.

Units:
- area_m2 values are square meters.
- length_m values are meters.
- source_area_ft2 and source_length_ft are optional raw Revit internal values.
"""

from interior_finish_takeoff.constants import (
    RECORD_TYPE_BASEBOARD_RESULT,
    RECORD_TYPE_INTERIOR_RULE,
    RECORD_TYPE_QC_FLAG,
    RECORD_TYPE_RAW_MATERIAL,
    RECORD_TYPE_ROOM_MAPPING,
    RECORD_TYPE_TAKEOFF_RESULT,
    SCHEMA_VERSION,
    SEVERITY_INFO,
    SOURCE_TYPE_PAINT,
    VALID_SEVERITIES,
    VALID_SOURCE_TYPES
)
from interior_finish_takeoff.qc_flags import normalize_flags
from interior_finish_takeoff.units import (
    revit_area_to_m2,
    revit_length_to_m,
    round_area_m2,
    round_length_m
)


def RawMaterialRecord(
    source_type,
    element_id=None,
    source_element_id=None,
    element_unique_id=u"",
    category=u"",
    element_category=u"",
    element_name=u"",
    type_name=u"",
    material_id=None,
    material_name=u"",
    paint_material_id=None,
    paint_material_name=u"",
    room_id=None,
    room_number=u"",
    room_name=u"",
    level_id=None,
    level_name=u"",
    target_type=u"",
    area_m2=0.0,
    source_area_ft2=None,
    length_m=0.0,
    source_length_ft=None,
    flags=None,
    metadata=None
):
    """Create a raw material/finish source record."""
    normalized_source_type = normalize_source_type(source_type)
    normalized_area_m2 = area_m2
    normalized_length_m = length_m
    if source_area_ft2 is not None:
        normalized_area_m2 = revit_area_to_m2(source_area_ft2)
    if source_length_ft is not None:
        normalized_length_m = revit_length_to_m(source_length_ft)

    return _record(RECORD_TYPE_RAW_MATERIAL, {
        "source_type": normalized_source_type,
        "element_id": _id_or_none(element_id),
        "source_element_id": _id_or_none(source_element_id),
        "unique_id": _to_text(element_unique_id),
        "element_unique_id": _to_text(element_unique_id),
        "category": _to_text(category or element_category),
        "element_category": _to_text(element_category),
        "element_name": _to_text(element_name),
        "type_name": _to_text(type_name),
        "material_id": _id_or_none(material_id),
        "material_name": _to_text(material_name),
        "paint_material_id": _id_or_none(paint_material_id),
        "paint_material_name": _to_text(paint_material_name),
        "room_id": _id_or_none(room_id),
        "room_number": _to_text(room_number),
        "room_name": _to_text(room_name),
        "level_id": _id_or_none(level_id),
        "level_name": _to_text(level_name),
        "target_type": _to_text(target_type),
        "area_m2": round_area_m2(normalized_area_m2),
        "source_area_ft2": _float_or_none(source_area_ft2),
        "length_m": round_length_m(normalized_length_m),
        "source_length_ft": _float_or_none(source_length_ft),
        "flags": normalize_flags(flags),
        "metadata": _dict_or_empty(metadata)
    })


def RoomMappingRecord(
    room_id=None,
    room_unique_id=u"",
    room_number=u"",
    room_name=u"",
    level_id=None,
    level_name=u"",
    department=u"",
    area_m2=0.0,
    source_area_ft2=None,
    finish_wall=u"",
    finish_floor=u"",
    finish_ceiling=u"",
    baseboard_type=u"",
    mapping_status=u"UNMAPPED",
    flags=None,
    metadata=None
):
    """Create a room-to-finish mapping record."""
    normalized_area_m2 = area_m2
    if source_area_ft2 is not None:
        normalized_area_m2 = revit_area_to_m2(source_area_ft2)

    return _record(RECORD_TYPE_ROOM_MAPPING, {
        "room_id": _id_or_none(room_id),
        "room_unique_id": _to_text(room_unique_id),
        "room_number": _to_text(room_number),
        "room_name": _to_text(room_name),
        "level_id": _id_or_none(level_id),
        "level_name": _to_text(level_name),
        "department": _to_text(department),
        "area_m2": round_area_m2(normalized_area_m2),
        "source_area_ft2": _float_or_none(source_area_ft2),
        "finish_wall": _to_text(finish_wall),
        "finish_floor": _to_text(finish_floor),
        "finish_ceiling": _to_text(finish_ceiling),
        "baseboard_type": _to_text(baseboard_type),
        "mapping_status": _to_text(mapping_status),
        "flags": normalize_flags(flags),
        "metadata": _dict_or_empty(metadata)
    })


def InteriorRuleRecord(
    rule_id,
    source_type=SOURCE_TYPE_PAINT,
    target_type=u"",
    match_parameter=u"",
    match_value=u"",
    material_name=u"",
    finish_code=u"",
    finish_name=u"",
    include_in_takeoff=True,
    include_baseboard=False,
    baseboard_height_m=0.0,
    waste_factor=0.0,
    flags=None,
    metadata=None
):
    """Create a finish takeoff rule record."""
    return _record(RECORD_TYPE_INTERIOR_RULE, {
        "rule_id": _to_text(rule_id),
        "source_type": normalize_source_type(source_type),
        "target_type": _to_text(target_type),
        "match_parameter": _to_text(match_parameter),
        "match_value": _to_text(match_value),
        "material_name": _to_text(material_name),
        "finish_code": _to_text(finish_code),
        "finish_name": _to_text(finish_name),
        "include_in_takeoff": bool(include_in_takeoff),
        "include_baseboard": bool(include_baseboard),
        "baseboard_height_m": round_length_m(baseboard_height_m),
        "waste_factor": _to_float(waste_factor),
        "flags": normalize_flags(flags),
        "metadata": _dict_or_empty(metadata)
    })


def TakeoffResultRecord(
    result_id,
    source_type,
    target_type=u"",
    room_id=None,
    room_number=u"",
    room_name=u"",
    level_name=u"",
    material_id=None,
    material_name=u"",
    finish_code=u"",
    finish_name=u"",
    area_m2=0.0,
    source_area_ft2=None,
    waste_factor=0.0,
    area_with_waste_m2=None,
    final_area_m2=None,
    deduction_mode=u"none",
    raw_record_count=0,
    flags=None,
    metadata=None
):
    """Create an aggregated area takeoff result record."""
    normalized_area_m2 = area_m2
    if source_area_ft2 is not None:
        normalized_area_m2 = revit_area_to_m2(source_area_ft2)
    if area_with_waste_m2 is None:
        area_with_waste_m2 = normalized_area_m2 * (1.0 + _to_float(waste_factor))
    if final_area_m2 is None:
        final_area_m2 = area_with_waste_m2

    return _record(RECORD_TYPE_TAKEOFF_RESULT, {
        "result_id": _to_text(result_id),
        "source_type": normalize_source_type(source_type),
        "target_type": _to_text(target_type),
        "room_id": _id_or_none(room_id),
        "room_number": _to_text(room_number),
        "room_name": _to_text(room_name),
        "level_name": _to_text(level_name),
        "material_id": _id_or_none(material_id),
        "material_name": _to_text(material_name),
        "finish_code": _to_text(finish_code),
        "finish_name": _to_text(finish_name),
        "area_m2": round_area_m2(normalized_area_m2),
        "source_area_ft2": _float_or_none(source_area_ft2),
        "waste_factor": _to_float(waste_factor),
        "area_with_waste_m2": round_area_m2(area_with_waste_m2),
        "final_area_m2": round_area_m2(final_area_m2),
        "deduction_mode": _to_text(deduction_mode),
        "raw_record_count": _to_int(raw_record_count),
        "flags": normalize_flags(flags),
        "metadata": _dict_or_empty(metadata)
    })


def BaseboardResultRecord(
    result_id,
    room_id=None,
    room_number=u"",
    room_name=u"",
    level_name=u"",
    baseboard_type=u"",
    material_name=u"",
    length_m=0.0,
    source_length_ft=None,
    height_m=0.0,
    area_m2=0.0,
    source_area_ft2=None,
    deduction_length_m=0.0,
    deduction_mode=u"none",
    waste_factor=0.0,
    final_area_m2=None,
    opening_count=0,
    flags=None,
    metadata=None
):
    """Create an aggregated room baseboard result record."""
    normalized_length_m = length_m
    normalized_area_m2 = area_m2
    if source_length_ft is not None:
        normalized_length_m = revit_length_to_m(source_length_ft)
    if source_area_ft2 is not None:
        normalized_area_m2 = revit_area_to_m2(source_area_ft2)
    elif not normalized_area_m2 and normalized_length_m and height_m:
        normalized_area_m2 = normalized_length_m * _to_float(height_m)
    if final_area_m2 is None:
        final_area_m2 = normalized_area_m2 * (1.0 + _to_float(waste_factor))

    return _record(RECORD_TYPE_BASEBOARD_RESULT, {
        "result_id": _to_text(result_id),
        "room_id": _id_or_none(room_id),
        "room_number": _to_text(room_number),
        "room_name": _to_text(room_name),
        "level_name": _to_text(level_name),
        "baseboard_type": _to_text(baseboard_type),
        "material_name": _to_text(material_name),
        "length_m": round_length_m(normalized_length_m),
        "source_length_ft": _float_or_none(source_length_ft),
        "height_m": round_length_m(height_m),
        "area_m2": round_area_m2(normalized_area_m2),
        "source_area_ft2": _float_or_none(source_area_ft2),
        "deduction_length_m": round_length_m(deduction_length_m),
        "deduction_mode": _to_text(deduction_mode),
        "waste_factor": _to_float(waste_factor),
        "final_area_m2": round_area_m2(final_area_m2),
        "opening_count": _to_int(opening_count),
        "flags": normalize_flags(flags),
        "metadata": _dict_or_empty(metadata)
    })


def QCFlag(
    code,
    severity=SEVERITY_INFO,
    message=u"",
    record_type=u"",
    record_id=u"",
    element_id=None,
    room_id=None,
    flags=None,
    metadata=None
):
    """Create a JSON-exportable QC flag record."""
    return _record(RECORD_TYPE_QC_FLAG, {
        "code": _to_text(code),
        "severity": normalize_severity(severity),
        "message": _to_text(message),
        "record_type": _to_text(record_type),
        "record_id": _to_text(record_id),
        "element_id": _id_or_none(element_id),
        "room_id": _id_or_none(room_id),
        "flags": normalize_flags(flags),
        "metadata": _dict_or_empty(metadata)
    })


def normalize_source_type(source_type):
    text = _to_text(source_type).upper()
    if text in VALID_SOURCE_TYPES:
        return text
    raise ValueError(
        "source_type must be one of: {0}".format(
            ", ".join(VALID_SOURCE_TYPES)
        )
    )


def normalize_severity(severity):
    text = _to_text(severity).upper()
    if text in VALID_SEVERITIES:
        return text
    return SEVERITY_INFO


def _record(record_type, values):
    record = {
        "schema_version": SCHEMA_VERSION,
        "record_type": record_type
    }
    record.update(values)
    return record


def _dict_or_empty(value):
    if isinstance(value, dict):
        return value
    return {}


def _id_or_none(value):
    if value is None:
        return None
    text = _to_text(value)
    if text == u"":
        return None
    return text


def _float_or_none(value):
    if value is None:
        return None
    return _to_float(value)


def _to_float(value):
    if value is None:
        return 0.0
    try:
        return float(value)
    except Exception:
        return 0.0


def _to_int(value):
    if value is None:
        return 0
    try:
        return int(value)
    except Exception:
        return 0


def _to_text(value):
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return u""
