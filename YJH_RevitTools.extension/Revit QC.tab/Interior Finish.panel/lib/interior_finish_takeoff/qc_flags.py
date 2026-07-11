# -*- coding: utf-8 -*-

"""QC flag constants and helpers for Interior Finish Takeoff records."""

from interior_finish_takeoff.constants import (
    SEVERITY_ERROR,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    VALID_SEVERITIES
)


FLAG_MISSING_ROOM = "MISSING_ROOM"
FLAG_MISSING_ROOM_FINISH = "MISSING_ROOM_FINISH"
FLAG_MISSING_MATERIAL = "MISSING_MATERIAL"
FLAG_NO_MATERIAL = "NO_MATERIAL"
FLAG_API_EXCEPTION = "API_EXCEPTION"
FLAG_POSSIBLE_DUPLICATE = "POSSIBLE_DUPLICATE"
FLAG_PART_AND_ORIGINAL_BOTH_FOUND = "PART_AND_ORIGINAL_BOTH_FOUND"
FLAG_UNSUPPORTED_SOURCE_TYPE = "UNSUPPORTED_SOURCE_TYPE"
FLAG_ZERO_AREA = "ZERO_AREA"
FLAG_ZERO_LENGTH = "ZERO_LENGTH"
FLAG_ROOM_BOUNDARY_ERROR = "ROOM_BOUNDARY_ERROR"
FLAG_RULE_NOT_FOUND = "RULE_NOT_FOUND"
FLAG_ROOM_MAPPING_REVIEW = "ROOM_MAPPING_REVIEW"
FLAG_BASEBOARD_REVIEW = "BASEBOARD_REVIEW"

VALID_FLAG_CODES = (
    FLAG_MISSING_ROOM,
    FLAG_MISSING_ROOM_FINISH,
    FLAG_MISSING_MATERIAL,
    FLAG_NO_MATERIAL,
    FLAG_API_EXCEPTION,
    FLAG_POSSIBLE_DUPLICATE,
    FLAG_PART_AND_ORIGINAL_BOTH_FOUND,
    FLAG_UNSUPPORTED_SOURCE_TYPE,
    FLAG_ZERO_AREA,
    FLAG_ZERO_LENGTH,
    FLAG_ROOM_BOUNDARY_ERROR,
    FLAG_RULE_NOT_FOUND,
    FLAG_ROOM_MAPPING_REVIEW,
    FLAG_BASEBOARD_REVIEW
)


def normalize_flags(flags):
    """Return a JSON-safe list of unique flag strings in input order."""
    normalized = []
    for flag in _as_list(flags):
        text = _to_text(flag)
        if text and text not in normalized:
            normalized.append(text)
    return normalized


def add_flag(flags, flag):
    """Return a new flag list with flag appended once."""
    normalized = normalize_flags(flags)
    text = _to_text(flag)
    if text and text not in normalized:
        normalized.append(text)
    return normalized


def merge_flags(*flag_lists):
    """Merge several flag lists into a single unique list."""
    merged = []
    for flag_list in flag_lists:
        for flag in normalize_flags(flag_list):
            if flag not in merged:
                merged.append(flag)
    return merged


def is_valid_flag_code(flag_code):
    return _to_text(flag_code) in VALID_FLAG_CODES


def normalize_severity(severity):
    text = _to_text(severity).upper()
    if text in VALID_SEVERITIES:
        return text
    return SEVERITY_INFO


def is_blocking_severity(severity):
    return normalize_severity(severity) == SEVERITY_ERROR


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _to_text(value):
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return u""
