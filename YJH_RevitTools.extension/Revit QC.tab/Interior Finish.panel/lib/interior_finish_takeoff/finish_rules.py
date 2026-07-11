# -*- coding: utf-8 -*-

"""Room-based finish area calculator for Interior Finish Takeoff."""

from interior_finish_takeoff.constants import (
    SOURCE_TYPE_TYPE_MATERIAL,
    TARGET_CEILING,
    TARGET_FLOOR,
    TARGET_WALL
)
from interior_finish_takeoff.qc_flags import FLAG_ZERO_AREA, add_flag
from interior_finish_takeoff.schemas import TakeoffResultRecord
from interior_finish_takeoff.units import mm_to_m, round_area_m2


DEDUCTION_MODE_NONE = "none"
DEDUCTION_MODE_DOOR_PLACEHOLDER = "door_opening_placeholder"


def build_room_finish_results(room_mapping_records, settings):
    """Build wall, floor, and ceiling finish result records for rooms."""
    results = []
    for room_record in room_mapping_records:
        results.extend(build_room_finish_results_for_room(room_record, settings))
    return results


def build_room_finish_results_for_room(room_record, settings):
    boundary_length_m = _metadata_float(room_record, "boundary_length_m")
    room_area_m2 = _to_float(room_record.get("area_m2"))
    wall_height_m = mm_to_m(
        settings.get("default_wall_finish_height_mm", 2400.0)
    )

    return [
        build_wall_finish_result(
            room_record,
            boundary_length_m,
            wall_height_m,
            settings
        ),
        build_floor_finish_result(room_record, room_area_m2, settings),
        build_ceiling_finish_result(room_record, room_area_m2, settings)
    ]


def build_wall_finish_result(room_record, boundary_length_m, height_m, settings):
    area_m2 = boundary_length_m * height_m
    return _build_takeoff_result(
        room_record,
        TARGET_WALL,
        room_record.get("finish_wall", u""),
        area_m2,
        settings.get("default_waste_rate_wall", 0.0),
        {
            "boundary_length_m": boundary_length_m,
            "finish_height_m": height_m,
            "calculation": "boundary_length_m * finish_height_m"
        }
    )


def build_floor_finish_result(room_record, room_area_m2, settings):
    return _build_takeoff_result(
        room_record,
        TARGET_FLOOR,
        room_record.get("finish_floor", u""),
        room_area_m2,
        settings.get("default_waste_rate_floor", 0.0),
        {
            "calculation": "room_area_m2"
        }
    )


def build_ceiling_finish_result(room_record, room_area_m2, settings):
    metadata = {
        "calculation": "room_area_m2",
        "ceiling_mapping": "room_area_placeholder",
        "default_ceiling_offset_mm": settings.get(
            "default_ceiling_offset_mm",
            0.0
        )
    }
    return _build_takeoff_result(
        room_record,
        TARGET_CEILING,
        room_record.get("finish_ceiling", u""),
        room_area_m2,
        settings.get("default_waste_rate_ceiling", 0.0),
        metadata
    )


def calculate_final_area_m2(area_m2, waste_rate):
    return round_area_m2(_to_float(area_m2) * (1.0 + _to_float(waste_rate)))


def _build_takeoff_result(
    room_record,
    target_type,
    finish_name,
    area_m2,
    waste_rate,
    metadata
):
    flags = list(room_record.get("flags", []))
    area_m2 = round_area_m2(area_m2)
    if area_m2 == 0.0:
        flags = add_flag(flags, FLAG_ZERO_AREA)
    final_area_m2 = calculate_final_area_m2(area_m2, waste_rate)
    result_metadata = {}
    result_metadata.update(metadata)
    result_metadata["deduction_mode"] = DEDUCTION_MODE_NONE
    result_metadata["linked_model_included"] = False

    return TakeoffResultRecord(
        result_id=_build_result_id(room_record, target_type),
        source_type=SOURCE_TYPE_TYPE_MATERIAL,
        target_type=target_type,
        room_id=room_record.get("room_id"),
        room_number=room_record.get("room_number", u""),
        room_name=room_record.get("room_name", u""),
        level_name=room_record.get("level_name", u""),
        finish_name=finish_name,
        area_m2=area_m2,
        waste_factor=waste_rate,
        area_with_waste_m2=final_area_m2,
        final_area_m2=final_area_m2,
        raw_record_count=1,
        deduction_mode=DEDUCTION_MODE_NONE,
        flags=flags,
        metadata=result_metadata
    )


def _build_result_id(room_record, target_type):
    room_id = room_record.get("room_id", u"")
    if not room_id:
        room_id = room_record.get("room_number", u"")
    return u"{0}:{1}".format(room_id, target_type)


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
