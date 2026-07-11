# -*- coding: utf-8 -*-

"""Placeholder workflow helpers for the Interior Finish Takeoff Toolkit.

This module intentionally avoids Revit API calls and QC module imports.
Actual takeoff collection, room mapping, baseboard rules, and reporting should
be added here or in sibling modules after the toolkit requirements are fixed.
"""

from interior_finish_takeoff import VERSION


def _build_placeholder_result(title, purpose, todos):
    return {
        "title": title,
        "version": VERSION,
        "purpose": purpose,
        "status": "Skeleton only",
        "todos": todos
    }


def build_run_takeoff_placeholder():
    """Return placeholder data for the future finish takeoff runner."""
    return _build_placeholder_result(
        "Run Takeoff",
        "Interior finish area takeoff execution entry point.",
        [
            "TODO: Collect Rooms, Room Finish parameters, and finish targets read-only.",
            "TODO: Aggregate wall/floor/ceiling finish quantities by room and material.",
            "TODO: Export takeoff rows after the output schema is approved."
        ]
    )


def build_settings_placeholder():
    """Return placeholder data for toolkit-specific settings."""
    return _build_placeholder_result(
        "Settings",
        "Interior Finish Takeoff configuration entry point.",
        [
            "TODO: Define finish parameter names and validation rules.",
            "TODO: Define output folder and file naming rules.",
            "TODO: Keep settings independent from QC Toolkit configuration."
        ]
    )


def build_room_baseboard_placeholder():
    """Return placeholder data for future room baseboard calculations."""
    return _build_placeholder_result(
        "Room Baseboard",
        "Room-based baseboard quantity workflow entry point.",
        [
            "TODO: Define baseboard eligibility rules by room, wall, and opening.",
            "TODO: Calculate baseboard length with read-only model access.",
            "TODO: Flag rooms requiring manual review."
        ]
    )


def build_review_result_placeholder():
    """Return placeholder data for future result review."""
    return _build_placeholder_result(
        "Review Result",
        "Takeoff result review entry point.",
        [
            "TODO: Load the latest Interior Finish Takeoff result.",
            "TODO: Summarize missing data, warnings, and review-needed rooms.",
            "TODO: Provide links to generated CSV/XLSX outputs."
        ]
    )


def build_help_placeholder():
    """Return placeholder data for future toolkit help."""
    return _build_placeholder_result(
        "Help",
        "Interior Finish Takeoff usage guide entry point.",
        [
            "TODO: Document required room/finish parameters.",
            "TODO: Document safe read-only workflow and known limitations.",
            "TODO: Add MVP usage steps after implementation."
        ]
    )


def render_placeholder_result(output, result):
    """Render a simple pyRevit output page from placeholder result data."""
    output.print_html(
        u"<h2>{0}</h2>".format(_html_escape(result["title"]))
    )
    output.print_html(
        u"<p><strong>Toolkit:</strong> Interior Finish Takeoff {0}</p>".format(
            _html_escape(result["version"])
        )
    )
    output.print_html(
        u"<p><strong>Status:</strong> {0}</p>".format(
            _html_escape(result["status"])
        )
    )
    output.print_html(
        u"<p><strong>Purpose:</strong> {0}</p>".format(
            _html_escape(result["purpose"])
        )
    )
    output.print_html(u"<ul>")
    for todo in result["todos"]:
        output.print_html(
            u"<li>{0}</li>".format(_html_escape(todo))
        )
    output.print_html(u"</ul>")


def _html_escape(value):
    text = _to_text(value)
    return (
        text.replace(u"&", u"&amp;")
        .replace(u"<", u"&lt;")
        .replace(u">", u"&gt;")
        .replace(u'"', u"&quot;")
        .replace(u"'", u"&#39;")
    )


def _to_text(value):
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return u""
