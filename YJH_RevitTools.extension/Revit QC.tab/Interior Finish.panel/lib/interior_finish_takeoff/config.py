# -*- coding: utf-8 -*-

"""JSON settings for Interior Finish Takeoff.

Settings are stored as user-local runtime state under APPDATA instead of inside
the extension repository. This avoids committing machine-specific paths.
"""

import json
import os

from interior_finish_takeoff.part_handler import (
    PART_POLICY_EXCLUDE_ORIGINAL_IF_PARTS_EXIST,
    PART_POLICY_INCLUDE_BOTH_AND_FLAG,
    PART_POLICY_PREFER_ORIGINAL,
    PART_POLICY_PREFER_PARTS
)


CONFIG_VERSION = "0.1.0"

REPORT_FORMAT_HTML = "HTML"
REPORT_FORMAT_CSV = "CSV"
REPORT_FORMAT_JSON = "JSON"

REPORT_FORMATS = (
    REPORT_FORMAT_HTML,
    REPORT_FORMAT_CSV,
    REPORT_FORMAT_JSON
)

PART_POLICIES = (
    PART_POLICY_EXCLUDE_ORIGINAL_IF_PARTS_EXIST,
    PART_POLICY_INCLUDE_BOTH_AND_FLAG,
    PART_POLICY_PREFER_PARTS,
    PART_POLICY_PREFER_ORIGINAL
)

DEFAULT_SETTINGS = {
    "config_version": CONFIG_VERSION,
    "include_paint": True,
    "include_type_material": True,
    "include_parts": True,
    "part_policy": PART_POLICY_EXCLUDE_ORIGINAL_IF_PARTS_EXIST,
    "default_wall_finish_height_mm": 2400.0,
    "default_ceiling_offset_mm": 0.0,
    "default_waste_rate_wall": 0.05,
    "default_waste_rate_floor": 0.03,
    "default_waste_rate_ceiling": 0.03,
    "default_skirting_height_mm": 100.0,
    "default_skirting_waste_rate": 0.05,
    "output_folder": "",
    "report_format": REPORT_FORMAT_HTML
}

BOOL_KEYS = (
    "include_paint",
    "include_type_material",
    "include_parts"
)

NUMBER_KEYS = (
    "default_wall_finish_height_mm",
    "default_ceiling_offset_mm",
    "default_waste_rate_wall",
    "default_waste_rate_floor",
    "default_waste_rate_ceiling",
    "default_skirting_height_mm",
    "default_skirting_waste_rate"
)


def load_or_create_settings(panel_dir):
    """Load settings, creating a default JSON file when it does not exist."""
    config_path = get_config_path()
    default_settings = build_default_settings(panel_dir)
    if not os.path.exists(config_path):
        save_settings(default_settings, config_path)
        return default_settings, config_path, True

    loaded = {}
    try:
        with open(config_path, "r") as config_file:
            loaded = json.load(config_file)
    except Exception:
        loaded = {}

    settings = normalize_settings(loaded, default_settings)
    if settings != loaded:
        save_settings(settings, config_path)
    return settings, config_path, False


def save_settings(settings, config_path=None):
    """Save normalized settings to the user-local JSON config path."""
    if config_path is None:
        config_path = get_config_path()
    folder = os.path.dirname(config_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(config_path, "w") as config_file:
        json.dump(
            settings,
            config_file,
            indent=2,
            sort_keys=True
        )
    return config_path


def build_default_settings(panel_dir):
    settings = {}
    settings.update(DEFAULT_SETTINGS)
    settings["output_folder"] = get_default_output_folder(panel_dir)
    return settings


def normalize_settings(settings, default_settings=None):
    if default_settings is None:
        default_settings = DEFAULT_SETTINGS
    normalized = {}
    normalized.update(default_settings)
    if isinstance(settings, dict):
        normalized.update(settings)

    normalized["config_version"] = CONFIG_VERSION
    for key in BOOL_KEYS:
        normalized[key] = bool(normalized.get(key, default_settings[key]))
    for key in NUMBER_KEYS:
        normalized[key] = _to_float(normalized.get(key, default_settings[key]))

    part_policy = _to_text(normalized.get("part_policy", ""))
    if part_policy not in PART_POLICIES:
        part_policy = default_settings["part_policy"]
    normalized["part_policy"] = part_policy

    report_format = _to_text(normalized.get("report_format", "")).upper()
    if report_format not in REPORT_FORMATS:
        report_format = default_settings["report_format"]
    normalized["report_format"] = report_format

    output_folder = _to_text(normalized.get("output_folder", ""))
    if not output_folder:
        output_folder = default_settings["output_folder"]
    normalized["output_folder"] = output_folder
    return normalized


def get_config_path():
    base_folder = os.environ.get("APPDATA", "")
    if not base_folder:
        base_folder = os.path.expanduser("~")
    return os.path.join(
        base_folder,
        "YJH_RevitTools",
        "InteriorFinishTakeoff",
        "settings.json"
    )


def get_default_output_folder(panel_dir):
    extension_dir = os.path.abspath(
        os.path.join(panel_dir, os.pardir, os.pardir)
    )
    return os.path.join(
        extension_dir,
        "reports",
        "interior_finish_takeoff"
    )


def format_settings_summary(settings, config_path):
    lines = [
        ("Config Path", config_path),
        ("Include Paint", settings["include_paint"]),
        ("Include Type Material", settings["include_type_material"]),
        ("Include Parts", settings["include_parts"]),
        ("Part Policy", settings["part_policy"]),
        ("Wall Finish Height", "{0} mm".format(
            settings["default_wall_finish_height_mm"]
        )),
        ("Ceiling Offset", "{0} mm".format(
            settings["default_ceiling_offset_mm"]
        )),
        ("Wall Waste Rate", settings["default_waste_rate_wall"]),
        ("Floor Waste Rate", settings["default_waste_rate_floor"]),
        ("Ceiling Waste Rate", settings["default_waste_rate_ceiling"]),
        ("Skirting Height", "{0} mm".format(
            settings["default_skirting_height_mm"]
        )),
        ("Skirting Waste Rate", settings["default_skirting_waste_rate"]),
        ("Output Folder", settings["output_folder"]),
        ("Report Format", settings["report_format"])
    ]
    return lines


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
            return ""
