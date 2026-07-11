# -*- coding: utf-8 -*-

# Interior Finish Takeoff help skeleton entry point.
# TODO: Replace placeholder help with workflow documentation when MVP is defined.

import os
import sys

from pyrevit import script


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PANEL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, os.pardir))
PANEL_LIB_DIR = os.path.join(PANEL_DIR, "lib")

if PANEL_LIB_DIR not in sys.path:
    sys.path.insert(0, PANEL_LIB_DIR)


from interior_finish_takeoff.workflow import (
    build_help_placeholder,
    render_placeholder_result
)


output = script.get_output()
output.set_title("Interior Finish Takeoff - Help")
render_placeholder_result(output, build_help_placeholder())
