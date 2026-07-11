# -*- coding: utf-8 -*-

"""Unit conversion helpers for Revit internal units.

Revit stores length in feet and area in square feet. Interior Finish Takeoff
records store all length values in meters and all area values in square meters.
"""


FEET_TO_METER = 0.3048
SQUARE_FEET_TO_SQUARE_METER = 0.09290304
MILLIMETER_TO_METER = 0.001


def feet_to_m(feet_value):
    """Convert Revit internal length in feet to meters."""
    return _to_float(feet_value) * FEET_TO_METER


def m_to_feet(meter_value):
    """Convert meters to Revit internal length in feet."""
    return _to_float(meter_value) / FEET_TO_METER


def ft2_to_m2(square_feet_value):
    """Convert Revit internal area in square feet to square meters."""
    return _to_float(square_feet_value) * SQUARE_FEET_TO_SQUARE_METER


def m2_to_ft2(square_meter_value):
    """Convert square meters to Revit internal area in square feet."""
    return _to_float(square_meter_value) / SQUARE_FEET_TO_SQUARE_METER


def mm_to_m(millimeter_value):
    """Convert millimeters to meters."""
    return _to_float(millimeter_value) * MILLIMETER_TO_METER


def revit_length_to_m(feet_value):
    """Alias for converting Revit internal feet to meters."""
    return feet_to_m(feet_value)


def revit_area_to_m2(square_feet_value):
    """Alias for converting Revit internal square feet to square meters."""
    return ft2_to_m2(square_feet_value)


def get_revit_area_m2(element, material_id, use_paint_material):
    """Read material area from Revit and return square meters.

    This helper keeps the Revit API call in one place so callers can flag
    exceptions while preserving the ft2 -> m2 conversion rule.
    """
    area_ft2 = element.GetMaterialArea(material_id, use_paint_material)
    return revit_area_to_m2(area_ft2)


def round_area_m2(area_m2, digits=3):
    """Round a square-meter area value for stable JSON/CSV output."""
    return round(_to_float(area_m2), digits)


def round_length_m(length_m, digits=3):
    """Round a meter length value for stable JSON/CSV output."""
    return round(_to_float(length_m), digits)


def _to_float(value):
    if value is None:
        return 0.0
    try:
        return float(value)
    except Exception:
        return 0.0
