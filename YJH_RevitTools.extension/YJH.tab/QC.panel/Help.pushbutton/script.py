# -*- coding: utf-8 -*-

from pyrevit import script


output = script.get_output()
output.set_title("Revit QC Toolkit Help")
output.print_html(
    u"""
    <div style="font-family:Segoe UI, Arial, sans-serif;">
        <h2 style="color:#263645;">Revit QC Toolkit</h2>
        <p>Revit 2026 도면과 Parameter를 모델 수정 없이 점검하는 read-only pyRevit 도구입니다.</p>
        <table style="border-collapse:collapse; width:100%;">
            <tr><td style="padding:8px; font-weight:bold;">Run Full QC</td><td>Sheet + View + Parameter QC, Full/Summary CSV, Styled XLSX</td></tr>
            <tr><td style="padding:8px; font-weight:bold;">Quick QC</td><td>Sheet + View QC, 선택형 CSV 및 Styled XLSX</td></tr>
            <tr><td style="padding:8px; font-weight:bold;">QC Settings</td><td>회사별 QC 기준 JSON 확인 및 수정</td></tr>
            <tr><td style="padding:8px; font-weight:bold;">Open Last Report</td><td>마지막 XLSX 또는 CSV 결과 열기</td></tr>
        </table>
        <div style="margin-top:12px; padding:10px; background:#e8f5e9; color:#2e7d32;">
            모든 검사는 Transaction 없이 실행되며 Revit 모델을 수정하지 않습니다.
        </div>
        <p>CSV는 원본 데이터와 호환용으로 유지하며, Styled XLSX는 4개 시트와 디자인이 적용된 보고·공유용 결과물입니다.</p>
        <p>Styled XLSX는 외부 Python helper를 사용하며 외부 Python에 openpyxl이 필요합니다.</p>
        <p>개인 Python 경로는 Git에서 제외되는 <code>config/qc_config_local.json</code>에 설정합니다.</p>
        <p><code>py -3 -m pip install openpyxl</code> / 실패 시 XLSX만 건너뛰고 CSV와 QC는 정상 완료됩니다.</p>
        <p>QC Settings에서 Python 상태를 확인하고 <code>reports/xlsx_helper_debug.log</code>에서 상세 실행 기록을 확인할 수 있습니다.</p>
    </div>
    """
)
