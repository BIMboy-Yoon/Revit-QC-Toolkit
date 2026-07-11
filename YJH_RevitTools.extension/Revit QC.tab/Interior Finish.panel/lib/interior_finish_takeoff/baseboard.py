# -*- coding: utf-8 -*-

"""Room-based skirting/baseboard calculator."""

from interior_finish_takeoff.qc_flags import FLAG_ZERO_LENGTH, add_flag
from interior_finish_takeoff.schemas import BaseboardResultRecord
from interior_finish_takeoff.units import mm_to_m, round_area_m2, round_length_m


DEDUCTION_MODE_NONE = "none"
DEDUCTION_MODE_DOOR_PLACEHOLDER = "door_opening_placeholder"


def build_baseboard_results(room_mapping_records, settings):
    """Build baseboard result records for room mappings."""
    results = []
    for room_record in room_mapping_records:
        results.append(build_baseboard_result_for_room(room_record, settings))
    return results


def build_baseboard_result_for_room(room_record, settings):
    skirting_length_m = _metadata_float(room_record, "boundary_length_m")
    skirting_height_m = mm_to_m(
        settings.get("default_skirting_height_mm", 100.0)
    )
    waste_rate = settings.get("default_skirting_waste_rate", 0.0)
    area_m2 = round_area_m2(skirting_length_m * skirting_height_m)
    final_area_m2 = round_area_m2(area_m2 * (1.0 + _to_float(waste_rate)))
    flags = list(room_record.get("flags", []))
    if skirting_length_m == 0.0:
        flags = add_flag(flags, FLAG_ZERO_LENGTH)

    return BaseboardResultRecord(
        result_id=_build_result_id(room_record),
        room_id=room_record.get("room_id"),
        room_number=room_record.get("room_number", u""),
        room_name=room_record.get("room_name", u""),
        level_name=room_record.get("level_name", u""),
        baseboard_type=room_record.get("baseboard_type", u""),
        material_name=room_record.get("baseboard_type", u""),
        length_m=round_length_m(skirting_length_m),
        height_m=skirting_height_m,
        area_m2=area_m2,
        deduction_length_m=0.0,
        deduction_mode=DEDUCTION_MODE_NONE,
        waste_factor=waste_rate,
        final_area_m2=final_area_m2,
        opening_count=0,
        flags=flags,
        metadata={
            "calculation": "boundary_length_m * skirting_height_m",
            "deduction_mode": DEDUCTION_MODE_NONE,
            "door_opening_deduction": "not_implemented",
            "linked_model_included": False
        }
    )


def _build_result_id(room_record):
    room_id = room_record.get("room_id", u"")
    if not room_id:
        room_id = room_record.get("room_number", u"")
    return u"{0}:BASEBOARD".format(room_id)


def _metadata_float(record, key):
    metadata = record.get("metadata", {})
    if isinstance(metadata, dict):
        return _to_float(metadata.get(key))
    return 0.0


def _to_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0
