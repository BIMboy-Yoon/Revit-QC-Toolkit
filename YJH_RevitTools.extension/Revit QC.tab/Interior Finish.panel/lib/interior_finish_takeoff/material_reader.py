# -*- coding: utf-8 -*-

"""Material reader for Interior Finish Takeoff.

Reads material ids and material areas from Revit elements without modifying the
model. Existing QC Toolkit modules are intentionally not imported here.
"""

from interior_finish_takeoff.collectors import collect_target_elements
from interior_finish_takeoff.constants import (
    SOURCE_TYPE_PAINT,
    SOURCE_TYPE_PART_MATERIAL,
    SOURCE_TYPE_TYPE_MATERIAL,
    TARGET_PART
)
from interior_finish_takeoff.part_handler import (
    get_element_id_value,
    get_part_source_element_ids,
    get_source_element_id_for_record
)
from interior_finish_takeoff.qc_flags import (
    FLAG_API_EXCEPTION,
    FLAG_NO_MATERIAL,
    FLAG_ZERO_AREA,
    add_flag,
    normalize_flags
)
from interior_finish_takeoff.schemas import RawMaterialRecord
from interior_finish_takeoff.units import get_revit_area_m2, round_area_m2


def read_target_material_records(doc, include_parts=True, target_types=None):
    """Collect target elements and read material records for each element."""
    records = []
    for item in collect_target_elements(
        doc,
        include_parts=include_parts,
        target_types=target_types
    ):
        records.extend(
            read_element_material_records(
                doc,
                item["element"],
                item["target_type"]
            )
        )
    return records


def read_elements_material_records(doc, elements, target_type):
    """Read material records for an explicit element list."""
    records = []
    for element in elements:
        records.extend(read_element_material_records(doc, element, target_type))
    return records


def read_element_material_records(doc, element, target_type):
    """Read layer/type and paint material area records from one element."""
    records = []
    source_type = _source_type_for_target(target_type)
    source_context = _build_source_context(doc, element, target_type)

    type_material_ids, type_flags = _safe_get_material_ids(element, False)
    paint_material_ids, paint_flags = _safe_get_material_ids(element, True)

    for material_id in type_material_ids:
        records.append(
            _build_material_record(
                doc,
                element,
                material_id,
                False,
                source_type,
                target_type,
                source_context,
                type_flags
            )
        )

    for material_id in paint_material_ids:
        records.append(
            _build_material_record(
                doc,
                element,
                material_id,
                True,
                SOURCE_TYPE_PAINT,
                target_type,
                source_context,
                paint_flags
            )
        )

    if not type_material_ids and not paint_material_ids:
        flags = normalize_flags(type_flags + paint_flags)
        flags = add_flag(flags, FLAG_NO_MATERIAL)
        records.append(
            _empty_material_record(source_type, target_type, source_context, flags)
        )
    else:
        if type_flags and not type_material_ids:
            records.append(
                _empty_material_record(
                    source_type,
                    target_type,
                    source_context,
                    type_flags
                )
            )
        if paint_flags and not paint_material_ids:
            records.append(
                _empty_material_record(
                    SOURCE_TYPE_PAINT,
                    target_type,
                    source_context,
                    paint_flags
                )
            )

    return records


def _safe_get_material_ids(element, use_paint_material):
    flags = []
    try:
        material_ids = list(element.GetMaterialIds(use_paint_material))
        return material_ids, flags
    except Exception:
        flags.append(FLAG_API_EXCEPTION)
        return [], flags


def _build_material_record(
    doc,
    element,
    material_id,
    use_paint_material,
    source_type,
    target_type,
    source_context,
    inherited_flags
):
    flags = normalize_flags(inherited_flags)
    try:
        area_m2 = get_revit_area_m2(element, material_id, use_paint_material)
    except Exception:
        area_m2 = 0.0
        flags = add_flag(flags, FLAG_API_EXCEPTION)

    area_m2 = round_area_m2(area_m2)
    if area_m2 == 0.0:
        flags = add_flag(flags, FLAG_ZERO_AREA)

    material_name = _get_material_name(doc, material_id)
    material_id_value = get_element_id_value(material_id)
    paint_material_id = None
    paint_material_name = u""
    if use_paint_material:
        paint_material_id = material_id_value
        paint_material_name = material_name

    return RawMaterialRecord(
        source_type=source_type,
        element_id=source_context["element_id"],
        source_element_id=source_context["source_element_id"],
        element_unique_id=source_context["unique_id"],
        category=source_context["category"],
        element_category=source_context["category"],
        element_name=source_context["element_name"],
        type_name=source_context["type_name"],
        material_id=material_id_value,
        material_name=material_name,
        paint_material_id=paint_material_id,
        paint_material_name=paint_material_name,
        level_id=source_context["level_id"],
        level_name=source_context["level_name"],
        target_type=target_type,
        area_m2=area_m2,
        flags=flags,
        metadata={
            "use_paint_material": bool(use_paint_material),
            "part_source_element_ids": source_context["part_source_element_ids"]
        }
    )


def _empty_material_record(source_type, target_type, source_context, flags):
    return RawMaterialRecord(
        source_type=source_type,
        element_id=source_context["element_id"],
        source_element_id=source_context["source_element_id"],
        element_unique_id=source_context["unique_id"],
        category=source_context["category"],
        element_category=source_context["category"],
        element_name=source_context["element_name"],
        type_name=source_context["type_name"],
        level_id=source_context["level_id"],
        level_name=source_context["level_name"],
        target_type=target_type,
        area_m2=0.0,
        flags=flags,
        metadata={
            "part_source_element_ids": source_context["part_source_element_ids"]
        }
    )


def _build_source_context(doc, element, target_type):
    element_id = get_element_id_value(getattr(element, "Id", None))
    source_element_id = get_source_element_id_for_record(element, target_type)
    level_id, level_name = _get_level_info(doc, element)
    part_source_element_ids = []
    if target_type == TARGET_PART:
        part_source_element_ids = get_part_source_element_ids(element)

    return {
        "element_id": element_id,
        "source_element_id": source_element_id,
        "unique_id": _to_text(getattr(element, "UniqueId", u"")),
        "category": _get_category_name(element),
        "element_name": _get_element_name(element),
        "type_name": _get_type_name(doc, element),
        "level_id": level_id,
        "level_name": level_name,
        "part_source_element_ids": part_source_element_ids
    }


def _source_type_for_target(target_type):
    if target_type == TARGET_PART:
        return SOURCE_TYPE_PART_MATERIAL
    return SOURCE_TYPE_TYPE_MATERIAL


def _get_material_name(doc, material_id):
    try:
        material = doc.GetElement(material_id)
        return _to_text(getattr(material, "Name", u""))
    except Exception:
        return u""


def _get_type_name(doc, element):
    try:
        type_id = element.GetTypeId()
        element_type = doc.GetElement(type_id)
        return _to_text(getattr(element_type, "Name", u""))
    except Exception:
        return u""


def _get_level_info(doc, element):
    level_id = _get_level_id(element)
    level_name = u""
    if level_id is not None:
        try:
            level = doc.GetElement(level_id)
            level_name = _to_text(getattr(level, "Name", u""))
        except Exception:
            level_name = u""
    return get_element_id_value(level_id), level_name


def _get_level_id(element):
    try:
        return element.LevelId
    except Exception:
        pass
    try:
        return element.GenLevel.Id
    except Exception:
        pass
    return None


def _get_category_name(element):
    try:
        return _to_text(element.Category.Name)
    except Exception:
        return u""


def _get_element_name(element):
    try:
        return _to_text(element.Name)
    except Exception:
        return u""


def _to_text(value):
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return u""
