# -*- coding: utf-8 -*-

"""Helpers for tracking Revit Parts back to their source elements."""


PART_POLICY_PREFER_PARTS = "prefer_parts"
PART_POLICY_PREFER_ORIGINAL = "prefer_original"
PART_POLICY_EXCLUDE_ORIGINAL_IF_PARTS_EXIST = "exclude_original_if_parts_exist"
PART_POLICY_INCLUDE_BOTH_AND_FLAG = "include_both_and_flag"

PART_POLICY_KEYS = (
    PART_POLICY_PREFER_PARTS,
    PART_POLICY_PREFER_ORIGINAL,
    PART_POLICY_EXCLUDE_ORIGINAL_IF_PARTS_EXIST,
    PART_POLICY_INCLUDE_BOTH_AND_FLAG
)


def default_part_policy_options():
    """Return the default duplicate-safe Part handling policy."""
    return {
        PART_POLICY_PREFER_PARTS: False,
        PART_POLICY_PREFER_ORIGINAL: False,
        PART_POLICY_EXCLUDE_ORIGINAL_IF_PARTS_EXIST: True,
        PART_POLICY_INCLUDE_BOTH_AND_FLAG: False
    }


def normalize_part_policy_options(options=None):
    """Normalize Part policy options to a single active mode.

    When multiple options are true, the most explicit review mode wins first,
    then exclusion/preference modes. This keeps behavior deterministic.
    """
    normalized = {
        PART_POLICY_PREFER_PARTS: False,
        PART_POLICY_PREFER_ORIGINAL: False,
        PART_POLICY_EXCLUDE_ORIGINAL_IF_PARTS_EXIST: False,
        PART_POLICY_INCLUDE_BOTH_AND_FLAG: False
    }
    if isinstance(options, dict):
        for key in PART_POLICY_KEYS:
            if key in options:
                normalized[key] = bool(options[key])

    active_key = PART_POLICY_EXCLUDE_ORIGINAL_IF_PARTS_EXIST
    for key in (
        PART_POLICY_INCLUDE_BOTH_AND_FLAG,
        PART_POLICY_EXCLUDE_ORIGINAL_IF_PARTS_EXIST,
        PART_POLICY_PREFER_PARTS,
        PART_POLICY_PREFER_ORIGINAL
    ):
        if normalized.get(key, False):
            active_key = key
            break

    for key in PART_POLICY_KEYS:
        normalized[key] = key == active_key
    normalized["active_policy"] = active_key
    return normalized


def get_part_source_element_ids(part):
    """Return source element ids for a Part as JSON-safe strings."""
    if part is None:
        return []
    try:
        source_ids = part.GetSourceElementIds()
    except Exception:
        return []

    results = []
    for source_id in source_ids:
        value = _extract_link_element_id_value(source_id)
        if value is not None and value not in results:
            results.append(value)
    return results


def get_primary_part_source_element_id(part):
    """Return the first source element id for duplicate tracking."""
    source_ids = get_part_source_element_ids(part)
    if source_ids:
        return source_ids[0]
    return None


def get_source_element_id_for_record(element, target_type):
    """Use original element id for Parts and element id otherwise."""
    if target_type == "PART":
        source_element_id = get_primary_part_source_element_id(element)
        if source_element_id is not None:
            return source_element_id
    return get_element_id_value(getattr(element, "Id", None))


def get_element_id_value(element_id):
    """Return an ElementId value compatible with multiple Revit versions."""
    if element_id is None:
        return None


def get_record_source_element_id(record):
    """Return duplicate-tracking source id from a material record."""
    if not isinstance(record, dict):
        return None
    source_element_id = record.get("source_element_id")
    if source_element_id not in (None, u"", ""):
        return _to_text(source_element_id)
    element_id = record.get("element_id")
    if element_id not in (None, u"", ""):
        return _to_text(element_id)
    return None


def is_part_material_record(record):
    """Return True when a material record came from a Revit Part."""
    if not isinstance(record, dict):
        return False
    if record.get("target_type") == "PART":
        return True
    if record.get("source_type") == "PART_MATERIAL":
        return True
    metadata = record.get("metadata", {})
    if isinstance(metadata, dict) and metadata.get("part_source_element_ids"):
        return True
    return False


def split_part_and_original_records(records):
    """Group material records by source element id and Part/original origin."""
    grouped = {}
    for record in records:
        source_element_id = get_record_source_element_id(record)
        if source_element_id is None:
            source_element_id = "__missing_source__:{0}".format(id(record))
        if source_element_id not in grouped:
            grouped[source_element_id] = {
                "part_records": [],
                "original_records": []
            }
        if is_part_material_record(record):
            grouped[source_element_id]["part_records"].append(record)
        else:
            grouped[source_element_id]["original_records"].append(record)
    return grouped
    try:
        return str(element_id.IntegerValue)
    except Exception:
        pass
    try:
        return str(element_id.Value)
    except Exception:
        pass
    try:
        return str(element_id)
    except Exception:
        return None


def _extract_link_element_id_value(link_element_id):
    for attr_name in ("HostElementId", "LinkedElementId"):
        try:
            element_id = getattr(link_element_id, attr_name)
            value = get_element_id_value(element_id)
            if value is not None and value != "-1":
                return value
        except Exception:
            pass
    return get_element_id_value(link_element_id)


def _to_text(value):
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return u""
