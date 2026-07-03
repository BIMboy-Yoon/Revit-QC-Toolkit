# -*- coding: utf-8 -*-

import io
import os

import clr

clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

from System import Guid
from System.Drawing import Color, Font, FontFamily, FontStyle, Size
from System.Windows.Forms import (
    AutoScaleMode,
    Button,
    CheckBox,
    ColumnStyle,
    DialogResult,
    DockStyle,
    FlowDirection,
    FlowLayoutPanel,
    FolderBrowserDialog,
    Form,
    FormBorderStyle,
    FormStartPosition,
    Label,
    MessageBox,
    MessageBoxButtons,
    MessageBoxIcon,
    Padding,
    RowStyle,
    SizeType,
    TableLayoutPanel,
    TextBox,
    ToolTip
)


LATEST_EXPORT_FOLDER_FILE = "latest_export_folder.txt"
NAVY_COLOR = Color.FromArgb(38, 54, 69)
MUTED_COLOR = Color.FromArgb(102, 112, 122)
LIGHT_BACKGROUND_COLOR = Color.FromArgb(248, 249, 251)


def get_preferred_font(size, style=FontStyle.Regular):
    preferred_names = [u"SUIT", u"Pretendard", u"Malgun Gothic", u"Segoe UI"]

    try:
        available_names = [family.Name.lower() for family in FontFamily.Families]
        for font_name in preferred_names:
            if font_name.lower() in available_names:
                return Font(font_name, size, style)
    except Exception:
        pass

    return Font(u"Segoe UI", size, style)


def get_latest_export_folder_pointer(reports_dir):
    return os.path.join(reports_dir, LATEST_EXPORT_FOLDER_FILE)


def read_latest_export_folder(reports_dir):
    pointer_path = get_latest_export_folder_pointer(reports_dir)

    if not os.path.isfile(pointer_path):
        return u""

    try:
        with io.open(pointer_path, "r", encoding="utf-8-sig") as pointer_file:
            folder_path = pointer_file.read().strip()

        if os.path.isdir(folder_path):
            return folder_path
    except Exception:
        pass

    return u""


def write_latest_export_folder(reports_dir, folder_path):
    if not os.path.isdir(reports_dir):
        os.makedirs(reports_dir)

    pointer_path = get_latest_export_folder_pointer(reports_dir)

    with io.open(pointer_path, "w", encoding="utf-8") as pointer_file:
        pointer_file.write(folder_path)

    return pointer_path


def validate_export_folder(folder_path):
    if not folder_path or not folder_path.strip():
        return False, u"저장 폴더를 선택하세요."

    folder_path = folder_path.strip()

    if not os.path.isdir(folder_path):
        return False, u"선택한 폴더를 찾을 수 없습니다: {0}".format(folder_path)

    test_path = os.path.join(
        folder_path,
        u".revit_qc_write_test_{0}.tmp".format(Guid.NewGuid().ToString("N"))
    )

    try:
        with io.open(test_path, "w", encoding="utf-8") as test_file:
            test_file.write(u"write test")
    except Exception as ex:
        return False, u"선택한 폴더에 파일을 저장할 수 없습니다: {0}".format(ex)
    finally:
        try:
            if os.path.isfile(test_path):
                os.remove(test_path)
        except Exception:
            pass

    return True, u""


class ExportOptionsForm(Form):
    def __init__(self, last_folder, quick_mode):
        Form.__init__(self)
        self.result = None
        self.Text = "Revit QC - Export Options"
        self.ClientSize = Size(820, 470)
        self.MinimumSize = Size(780, 450)
        self.FormBorderStyle = FormBorderStyle.FixedDialog
        self.StartPosition = FormStartPosition.CenterScreen
        self.MaximizeBox = False
        self.MinimizeBox = False
        self.ShowInTaskbar = False
        self.BackColor = Color.White
        self.ForeColor = NAVY_COLOR
        self.Font = get_preferred_font(9.5)
        self.AutoScaleMode = AutoScaleMode.Font

        main_layout = TableLayoutPanel()
        main_layout.Dock = DockStyle.Fill
        main_layout.BackColor = Color.White
        main_layout.Padding = Padding(28, 24, 28, 20)
        main_layout.ColumnCount = 1
        main_layout.RowCount = 6
        main_layout.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 100.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 38.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 32.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 88.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 32.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Percent, 100.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 52.0))
        self.Controls.Add(main_layout)

        intro_label = Label()
        intro_label.Text = "Select an export folder and output formats for the QC report."
        intro_label.Dock = DockStyle.Fill
        intro_label.AutoSize = False
        intro_label.ForeColor = NAVY_COLOR
        intro_label.Font = get_preferred_font(11.0, FontStyle.Bold)
        intro_label.Padding = Padding(0, 3, 0, 0)
        main_layout.Controls.Add(intro_label, 0, 0)

        last_label = Label()
        if last_folder:
            last_label.Text = u"Last export folder: {0}".format(last_folder)
        else:
            last_label.Text = "Last export folder: Not available"
        last_label.Dock = DockStyle.Fill
        last_label.AutoSize = False
        last_label.AutoEllipsis = True
        last_label.ForeColor = MUTED_COLOR
        last_label.Padding = Padding(0, 2, 0, 0)
        main_layout.Controls.Add(last_label, 0, 1)

        self.last_folder_tooltip = ToolTip()
        self.last_folder_tooltip.SetToolTip(last_label, last_label.Text)

        folder_layout = TableLayoutPanel()
        folder_layout.Dock = DockStyle.Fill
        folder_layout.Margin = Padding(0, 4, 0, 8)
        folder_layout.ColumnCount = 1
        folder_layout.RowCount = 2
        folder_layout.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 100.0))
        folder_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 28.0))
        folder_layout.RowStyles.Add(RowStyle(SizeType.Percent, 100.0))
        main_layout.Controls.Add(folder_layout, 0, 2)

        folder_label = Label()
        folder_label.Text = "Export folder"
        folder_label.Dock = DockStyle.Fill
        folder_label.AutoSize = False
        folder_label.ForeColor = NAVY_COLOR
        folder_label.Font = get_preferred_font(9.5, FontStyle.Bold)
        folder_layout.Controls.Add(folder_label, 0, 0)

        folder_input_layout = TableLayoutPanel()
        folder_input_layout.Dock = DockStyle.Fill
        folder_input_layout.Margin = Padding(0)
        folder_input_layout.ColumnCount = 2
        folder_input_layout.RowCount = 1
        folder_input_layout.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 100.0))
        folder_input_layout.ColumnStyles.Add(ColumnStyle(SizeType.Absolute, 104.0))
        folder_input_layout.RowStyles.Add(RowStyle(SizeType.Percent, 100.0))
        folder_layout.Controls.Add(folder_input_layout, 0, 1)

        self.folder_text = TextBox()
        self.folder_text.Text = last_folder or u""
        self.folder_text.Dock = DockStyle.Fill
        self.folder_text.Margin = Padding(0, 2, 12, 2)
        self.folder_text.WordWrap = False
        self.folder_text.TextChanged += self._update_folder_tooltip
        folder_input_layout.Controls.Add(self.folder_text, 0, 0)

        self.folder_tooltip = ToolTip()
        self.folder_tooltip.SetToolTip(self.folder_text, self.folder_text.Text)

        browse_button = Button()
        browse_button.Text = "Browse..."
        browse_button.Dock = DockStyle.Fill
        browse_button.Margin = Padding(0)
        browse_button.Click += self._browse_folder
        folder_input_layout.Controls.Add(browse_button, 1, 0)

        formats_label = Label()
        formats_label.Text = "Export formats"
        formats_label.Dock = DockStyle.Fill
        formats_label.AutoSize = False
        formats_label.ForeColor = NAVY_COLOR
        formats_label.Font = get_preferred_font(9.5, FontStyle.Bold)
        formats_label.Padding = Padding(0, 4, 0, 0)
        main_layout.Controls.Add(formats_label, 0, 3)

        formats_layout = TableLayoutPanel()
        formats_layout.Dock = DockStyle.Fill
        formats_layout.BackColor = LIGHT_BACKGROUND_COLOR
        formats_layout.Margin = Padding(0, 0, 0, 8)
        formats_layout.Padding = Padding(14, 10, 14, 10)
        formats_layout.ColumnCount = 1
        formats_layout.RowCount = 4
        formats_layout.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 100.0))
        formats_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 36.0))
        formats_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 36.0))
        formats_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 36.0))
        formats_layout.RowStyles.Add(RowStyle(SizeType.Percent, 100.0))
        main_layout.Controls.Add(formats_layout, 0, 4)

        self.full_csv_check = self._create_check_box(
            "Full CSV",
            not quick_mode
        )
        formats_layout.Controls.Add(self.full_csv_check, 0, 0)
        self.summary_csv_check = self._create_check_box(
            "Summary CSV",
            True
        )
        formats_layout.Controls.Add(self.summary_csv_check, 0, 1)
        self.styled_xlsx_check = self._create_check_box(
            "Styled XLSX Report",
            True
        )
        formats_layout.Controls.Add(self.styled_xlsx_check, 0, 2)

        note_label = Label()
        note_label.Text = "Styled XLSX creates a formatted Excel report for review and sharing."
        note_label.Dock = DockStyle.Fill
        note_label.AutoSize = False
        note_label.ForeColor = MUTED_COLOR
        note_label.Font = get_preferred_font(8.5)
        note_label.Padding = Padding(26, 2, 0, 0)
        formats_layout.Controls.Add(note_label, 0, 3)

        button_layout = FlowLayoutPanel()
        button_layout.Dock = DockStyle.Fill
        button_layout.FlowDirection = FlowDirection.RightToLeft
        button_layout.WrapContents = False
        button_layout.Margin = Padding(0)
        button_layout.Padding = Padding(0, 10, 0, 0)
        main_layout.Controls.Add(button_layout, 0, 5)

        ok_button = Button()
        ok_button.Text = "Run QC"
        ok_button.Size = Size(104, 34)
        ok_button.Margin = Padding(10, 0, 0, 0)
        ok_button.Click += self._confirm
        self.AcceptButton = ok_button

        cancel_button = Button()
        cancel_button.Text = "Cancel"
        cancel_button.Size = Size(104, 34)
        cancel_button.Margin = Padding(10, 0, 0, 0)
        cancel_button.DialogResult = DialogResult.Cancel
        button_layout.Controls.Add(cancel_button)
        button_layout.Controls.Add(ok_button)
        self.CancelButton = cancel_button

    def _create_check_box(self, text, checked):
        check_box = CheckBox()
        check_box.Text = text
        check_box.Dock = DockStyle.Fill
        check_box.AutoSize = True
        check_box.Margin = Padding(4, 4, 4, 4)
        check_box.ForeColor = NAVY_COLOR
        check_box.Checked = checked
        return check_box

    def _update_folder_tooltip(self, sender, event_args):
        if hasattr(self, "folder_tooltip"):
            self.folder_tooltip.SetToolTip(self.folder_text, self.folder_text.Text)

    def _browse_folder(self, sender, event_args):
        dialog = FolderBrowserDialog()
        dialog.Description = "Select the Revit QC export folder"
        dialog.ShowNewFolderButton = True

        current_folder = self.folder_text.Text.strip()
        if os.path.isdir(current_folder):
            dialog.SelectedPath = current_folder

        if dialog.ShowDialog(self) == DialogResult.OK:
            self.folder_text.Text = dialog.SelectedPath

        dialog.Dispose()

    def _confirm(self, sender, event_args):
        if not (
            self.full_csv_check.Checked
            or self.summary_csv_check.Checked
            or self.styled_xlsx_check.Checked
        ):
            MessageBox.Show(
                self,
                "Select at least one export format.",
                "Export Options",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning
            )
            return

        folder_path = self.folder_text.Text.strip()
        is_valid, validation_error = validate_export_folder(folder_path)

        if not is_valid:
            MessageBox.Show(
                self,
                validation_error,
                "Export Options",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning
            )
            return

        selected_formats = []
        if self.full_csv_check.Checked:
            selected_formats.append(u"Full CSV")
        if self.summary_csv_check.Checked:
            selected_formats.append(u"Summary CSV")
        if self.styled_xlsx_check.Checked:
            selected_formats.append(u"Styled XLSX Report")

        self.result = {
            "folder": folder_path,
            "full_csv": self.full_csv_check.Checked,
            "summary_csv": self.summary_csv_check.Checked,
            "styled_xlsx": self.styled_xlsx_check.Checked,
            "selected_formats": selected_formats,
            "folder_history_error": u""
        }
        self.DialogResult = DialogResult.OK
        self.Close()


def request_export_options(reports_dir, quick_mode=False):
    last_folder = read_latest_export_folder(reports_dir)
    options_form = ExportOptionsForm(last_folder, quick_mode)
    dialog_result = options_form.ShowDialog()
    selected_options = options_form.result
    options_form.Dispose()

    if dialog_result != DialogResult.OK or selected_options is None:
        return None

    try:
        write_latest_export_folder(reports_dir, selected_options["folder"])
    except Exception as ex:
        selected_options["folder_history_error"] = u"{0}".format(ex)

    return selected_options
