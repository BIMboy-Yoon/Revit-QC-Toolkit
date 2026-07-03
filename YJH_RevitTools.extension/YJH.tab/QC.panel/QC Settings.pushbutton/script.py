# -*- coding: utf-8 -*-

import os
import sys

from pyrevit import script


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTENSION_DIR = os.path.abspath(
    os.path.join(SCRIPT_DIR, os.pardir, os.pardir, os.pardir)
)
LIB_DIR = os.path.join(EXTENSION_DIR, "lib")
CONFIG_PATH = os.path.join(EXTENSION_DIR, "config", "qc_config_default.json")
LOCAL_CONFIG_PATH = os.path.join(EXTENSION_DIR, "config", "qc_config_local.json")
REPORTS_DIR = os.path.join(EXTENSION_DIR, "reports")

if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)


from config_loader import load_config
from exporters import get_xlsx_environment_status
from report_history import open_file
from report_ui import html_escape


output = script.get_output()
output.set_title("Revit QC Settings")
local_config_exists = os.path.isfile(LOCAL_CONFIG_PATH)
config = load_config(CONFIG_PATH, LOCAL_CONFIG_PATH)
applied_external_python_path = config.get("export", {}).get(
    "external_python_path",
    u""
)
xlsx_status = get_xlsx_environment_status(
    applied_external_python_path,
    EXTENSION_DIR,
    REPORTS_DIR
)
settings_path = LOCAL_CONFIG_PATH if local_config_exists else CONFIG_PATH
opened, open_error = open_file(settings_path)

if opened:
    status_text = u"기본 연결 프로그램으로 config 파일을 열었습니다: {0}".format(
        html_escape(settings_path)
    )
else:
    status_text = u"자동으로 열지 못했습니다. 아래 경로의 JSON 파일을 직접 수정하세요.<br>{0}".format(
        html_escape(open_error)
    )

local_config_example = (
    u'{\n'
    u'  "external_python_path": "C:\\\\Path\\\\To\\\\Python\\\\python.exe"\n'
    u'}'
)

output.print_html(
    u"""
    <div style="font-family:Segoe UI, Arial, sans-serif;">
        <h2>QC Settings</h2>
        <table style="border-collapse:collapse; width:100%;">
            <tr><td style="padding:6px; font-weight:bold;">Default config path</td><td>{0}</td></tr>
            <tr><td style="padding:6px; font-weight:bold;">Local config path</td><td>{1}</td></tr>
            <tr><td style="padding:6px; font-weight:bold;">Local config exists</td><td>{2}</td></tr>
            <tr><td style="padding:6px; font-weight:bold;">Applied external_python_path</td><td>{3}</td></tr>
        </table>
        <p>{4}</p>
        <h3 style="color:#263645;">Styled XLSX Environment</h3>
        <table style="border-collapse:collapse; width:100%;">
            <tr><td style="padding:6px; font-weight:bold;">External Python detected</td><td>{5}</td></tr>
            <tr><td style="padding:6px; font-weight:bold;">openpyxl available</td><td>{6}</td></tr>
            <tr><td style="padding:6px; font-weight:bold;">Python detail</td><td>{7}</td></tr>
            <tr><td style="padding:6px; font-weight:bold;">Helper script</td><td>{8}</td></tr>
            <tr><td style="padding:6px; font-weight:bold;">Helper exists</td><td>{9}</td></tr>
            <tr><td style="padding:6px; font-weight:bold;">Last debug log</td><td>{10}</td></tr>
            <tr><td style="padding:6px; font-weight:bold;">Probe error</td><td>{11}</td></tr>
        </table>
        <h3 style="color:#263645;">Local Config Example</h3>
        <p>Create <code>config/qc_config_local.json</code> with:</p>
        <pre style="padding:10px; background:#F6F7F8; border:1px solid #D9DEE3;">{12}</pre>
        <div style="padding:10px; background:#fff8e1; border-left:4px solid #E97826;">
            회사별 Sheet, View, Parameter QC 기준은 이 JSON 파일에서 수정할 수 있습니다.<br>
            변경 전 Git 기준점을 남기고 JSON 문법과 Revit Category 이름을 확인하세요.
        </div>
    </div>
    """.format(
        html_escape(CONFIG_PATH),
        html_escape(LOCAL_CONFIG_PATH),
        u"Yes" if local_config_exists else u"No",
        html_escape(applied_external_python_path or u"(empty)"),
        status_text,
        html_escape(xlsx_status["external_python_detected"]),
        html_escape(xlsx_status["openpyxl_available"]),
        html_escape(xlsx_status["python_detail"] or u"(none)"),
        html_escape(xlsx_status["helper_path"]),
        html_escape(xlsx_status["helper_exists"]),
        html_escape(xlsx_status["debug_log_path"]),
        html_escape(xlsx_status["probe_error"] or u"(none)"),
        html_escape(local_config_example)
    )
)
