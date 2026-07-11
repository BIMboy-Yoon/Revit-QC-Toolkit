# -*- coding: utf-8 -*-

# Interior Finish Takeoff settings entry point.

import os
import sys

from pyrevit import script


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PANEL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
PANEL_LIB_DIR = os.path.join(PANEL_DIR, "lib")

if PANEL_LIB_DIR not in sys.path:
    sys.path.insert(0, PANEL_LIB_DIR)


from interior_finish_takeoff.config import (
    format_settings_summary,
    load_or_create_settings,
    save_settings
)
from interior_finish_takeoff.ui_forms import show_settings_dialog


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


output = script.get_output()
output.set_title("Interior Finish Takeoff - Settings")
settings, config_path, created = load_or_create_settings(PANEL_DIR)
updated_settings = show_settings_dialog(settings)

if updated_settings is None:
    output.print_html(u"<h2>Interior Finish Takeoff Settings</h2>")
    output.print_html(u"<p>Settings update cancelled.</p>")
    script.exit()

save_settings(updated_settings, config_path)

output.print_html(u"<h2>Interior Finish Takeoff Settings Saved</h2>")
if created:
    output.print_html(u"<p>Default settings file was created automatically.</p>")
output.print_html(u"<table>")
for label, value in format_settings_summary(updated_settings, config_path):
    output.print_html(
        u"<tr><td><strong>{0}</strong></td><td>{1}</td></tr>".format(
            _html_escape(label),
            _html_escape(value)
        )
    )
output.print_html(u"</table>")
