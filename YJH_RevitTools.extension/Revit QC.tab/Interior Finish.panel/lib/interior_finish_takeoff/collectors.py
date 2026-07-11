# -*- coding: utf-8 -*-

"""Revit element collectors for Interior Finish Takeoff.

This module is read-only and intentionally independent from the existing QC
Toolkit modules.
"""

from interior_finish_takeoff.constants import (
    TARGET_CEILING,
    TARGET_FLOOR,
    TARGET_PART,
    TARGET_WALL
)

try:
    from Autodesk.Revit.DB import BuiltInCategory, FilteredElementCollector
except Exception:
    BuiltInCategory = None
    FilteredElementCollector = None


def collect_target_elements(doc, include_parts=True, target_types=None):
    """Collect Walls, Floors, Ceilings, and optionally Parts.

    Returns a list of dictionaries with target_type and element keys.
    """
    results = []
    selected_target_types = _normalize_target_types(target_types)
    for spec in _target_category_specs(include_parts):
        if selected_target_types and spec["target_type"] not in selected_target_types:
            continue
        elements = collect_elements_by_category(doc, spec["built_in_category"])
        for element in elements:
            results.append({
                "target_type": spec["target_type"],
                "element": element
            })
    return results


def collect_walls(doc):
    return collect_elements_by_category(doc, _get_built_in_category("OST_Walls"))


def collect_floors(doc):
    return collect_elements_by_category(doc, _get_built_in_category("OST_Floors"))


def collect_ceilings(doc):
    return collect_elements_by_category(doc, _get_built_in_category("OST_Ceilings"))


def collect_parts(doc):
    return collect_elements_by_category(doc, _get_built_in_category("OST_Parts"))


def collect_elements_by_category(doc, built_in_category):
    """Return non-type elements for a Revit BuiltInCategory."""
    if doc is None or built_in_category is None:
        return []
    if FilteredElementCollector is None:
        raise RuntimeError("Revit API is not available.")
    return list(
        FilteredElementCollector(doc)
        .OfCategory(built_in_category)
        .WhereElementIsNotElementType()
        .ToElements()
    )


def _target_category_specs(include_parts):
    specs = [
        {
            "target_type": TARGET_WALL,
            "built_in_category": _get_built_in_category("OST_Walls")
        },
        {
            "target_type": TARGET_FLOOR,
            "built_in_category": _get_built_in_category("OST_Floors")
        },
        {
            "target_type": TARGET_CEILING,
            "built_in_category": _get_built_in_category("OST_Ceilings")
        }
    ]
    if include_parts:
        specs.append({
            "target_type": TARGET_PART,
            "built_in_category": _get_built_in_category("OST_Parts")
        })
    return specs


def _normalize_target_types(target_types):
    if target_types is None:
        return None
    normalized = []
    for target_type in target_types:
        if target_type not in normalized:
            normalized.append(target_type)
    return normalized


def _get_built_in_category(name):
    if BuiltInCategory is None:
        return None
    try:
        return getattr(BuiltInCategory, name)
    except Exception:
        return None
