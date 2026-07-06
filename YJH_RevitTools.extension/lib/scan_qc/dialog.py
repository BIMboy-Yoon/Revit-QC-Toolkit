# -*- coding: utf-8 -*-

import clr

clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

from System.Drawing import Color, ContentAlignment, Font, FontFamily, FontStyle, Size
from System.Windows.Forms import (
    AutoScaleMode,
    Button,
    CheckBox,
    ColumnStyle,
    ComboBox,
    ComboBoxStyle,
    DialogResult,
    DockStyle,
    FlowDirection,
    FlowLayoutPanel,
    FlatStyle,
    Form,
    FormBorderStyle,
    FormStartPosition,
    GroupBox,
    Label,
    Padding,
    RowStyle,
    SizeType,
    TableLayoutPanel
)

from scan_qc.collectors import get_element_id_value, get_point_cloud_name
from scan_qc.settings import get_output_options, get_tolerance_mm


NAVY_COLOR = Color.FromArgb(38, 54, 69)
BUTTON_NAVY_COLOR = Color.FromArgb(83, 103, 119)
BUTTON_HOVER_COLOR = Color.FromArgb(70, 88, 103)
MUTED_COLOR = Color.FromArgb(95, 111, 125)
BORDER_COLOR = Color.FromArgb(214, 221, 227)
LIGHT_BACKGROUND_COLOR = Color.FromArgb(244, 246, 248)
WARNING_BACKGROUND_COLOR = Color.FromArgb(255, 241, 230)


def get_preferred_font(size, style=FontStyle.Regular):
    preferred_names = [u"Segoe UI", u"Malgun Gothic", u"Pretendard", u"SUIT"]

    try:
        available_names = [family.Name.lower() for family in FontFamily.Families]
        for font_name in preferred_names:
            if font_name.lower() in available_names:
                return Font(font_name, size, style)
    except Exception:
        pass

    return Font(u"Segoe UI", size, style)


def format_mm_value(value):
    try:
        numeric_value = float(value)
        if numeric_value.is_integer():
            return u"{0}".format(int(numeric_value))
    except (TypeError, ValueError):
        pass

    return u"{0}".format(value)


class ScanQcForm(Form):
    def __init__(self, selected_wall_count, point_clouds, settings):
        Form.__init__(self)
        self.result = None
        self.point_clouds = point_clouds
        tolerance_mm = get_tolerance_mm(settings)
        output_defaults = get_output_options(settings)

        self.Text = "Revit QC - Scan QC"
        self.ClientSize = Size(760, 620)
        self.MinimumSize = Size(740, 600)
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
        main_layout.Padding = Padding(28, 22, 28, 18)
        main_layout.ColumnCount = 1
        main_layout.RowCount = 7
        main_layout.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 100.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 50.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 58.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 112.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 112.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 142.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Percent, 100.0))
        main_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 48.0))
        self.Controls.Add(main_layout)

        intro_label = Label()
        intro_label.Text = "Scan QC Setup"
        intro_label.Dock = DockStyle.Fill
        intro_label.AutoSize = False
        intro_label.ForeColor = NAVY_COLOR
        intro_label.Font = get_preferred_font(15.0, FontStyle.Bold)
        intro_label.Padding = Padding(0, 5, 0, 0)
        main_layout.Controls.Add(intro_label, 0, 0)

        wall_card = Label()
        wall_card.Text = u"Selected Walls: {0}".format(selected_wall_count)
        wall_card.Dock = DockStyle.Fill
        wall_card.AutoSize = False
        wall_card.BackColor = LIGHT_BACKGROUND_COLOR
        wall_card.ForeColor = NAVY_COLOR
        wall_card.Font = get_preferred_font(11.0, FontStyle.Bold)
        wall_card.Padding = Padding(14, 16, 14, 0)
        wall_card.Margin = Padding(0, 0, 0, 8)
        main_layout.Controls.Add(wall_card, 0, 1)

        point_cloud_group = self._create_group("Point Cloud Instance")
        main_layout.Controls.Add(point_cloud_group, 0, 2)

        point_cloud_layout = TableLayoutPanel()
        point_cloud_layout.Dock = DockStyle.Fill
        point_cloud_layout.Padding = Padding(12, 8, 12, 8)
        point_cloud_layout.ColumnCount = 1
        point_cloud_layout.RowCount = 2
        point_cloud_layout.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 100.0))
        point_cloud_layout.RowStyles.Add(RowStyle(SizeType.Absolute, 34.0))
        point_cloud_layout.RowStyles.Add(RowStyle(SizeType.Percent, 100.0))
        point_cloud_group.Controls.Add(point_cloud_layout)

        self.point_cloud_combo = ComboBox()
        self.point_cloud_combo.Dock = DockStyle.Fill
        self.point_cloud_combo.DropDownStyle = ComboBoxStyle.DropDownList
        self.point_cloud_combo.Margin = Padding(0, 0, 0, 6)
        self.point_cloud_combo.SelectedIndexChanged += self._update_selected_point_cloud
        point_cloud_layout.Controls.Add(self.point_cloud_combo, 0, 0)

        self.selected_point_cloud_label = Label()
        self.selected_point_cloud_label.Dock = DockStyle.Fill
        self.selected_point_cloud_label.AutoSize = False
        self.selected_point_cloud_label.ForeColor = MUTED_COLOR
        point_cloud_layout.Controls.Add(self.selected_point_cloud_label, 0, 1)

        for point_cloud in point_clouds:
            self.point_cloud_combo.Items.Add(
                u"{0}  [ElementId: {1}]".format(
                    get_point_cloud_name(point_cloud),
                    get_element_id_value(point_cloud.Id)
                )
            )

        tolerance_group = self._create_group("Default Tolerances")
        main_layout.Controls.Add(tolerance_group, 0, 3)

        tolerance_layout = TableLayoutPanel()
        tolerance_layout.Dock = DockStyle.Fill
        tolerance_layout.Padding = Padding(12, 8, 12, 8)
        tolerance_layout.ColumnCount = 3
        tolerance_layout.RowCount = 1
        for index in range(3):
            tolerance_layout.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 33.33))
        tolerance_layout.RowStyles.Add(RowStyle(SizeType.Percent, 100.0))
        tolerance_group.Controls.Add(tolerance_layout)

        tolerance_layout.Controls.Add(
            self._create_tolerance_label(
                "OK",
                u"0-{0} mm".format(format_mm_value(tolerance_mm["ok_max"])),
                Color.FromArgb(232, 245, 233)
            ),
            0,
            0
        )
        tolerance_layout.Controls.Add(
            self._create_tolerance_label(
                "Review",
                u"{0}-{1} mm".format(
                    format_mm_value(tolerance_mm["ok_max"]),
                    format_mm_value(tolerance_mm["review_max"])
                ),
                WARNING_BACKGROUND_COLOR
            ),
            1,
            0
        )
        tolerance_layout.Controls.Add(
            self._create_tolerance_label(
                "Critical",
                u"{0} mm+".format(format_mm_value(tolerance_mm["critical_min"])),
                Color.FromArgb(252, 235, 235)
            ),
            2,
            0
        )

        output_group = self._create_group("Output Options")
        main_layout.Controls.Add(output_group, 0, 4)

        output_layout = TableLayoutPanel()
        output_layout.Dock = DockStyle.Fill
        output_layout.Padding = Padding(12, 10, 12, 8)
        output_layout.ColumnCount = 2
        output_layout.RowCount = 2
        output_layout.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 50.0))
        output_layout.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 50.0))
        output_layout.RowStyles.Add(RowStyle(SizeType.Percent, 50.0))
        output_layout.RowStyles.Add(RowStyle(SizeType.Percent, 50.0))
        output_group.Controls.Add(output_layout)

        self.create_plan_check = self._create_check_box(
            "Create QC Plan View",
            output_defaults["create_plan_view"]
        )
        self.create_3d_check = self._create_check_box(
            "Create QC 3D View",
            output_defaults["create_3d_view"]
        )
        self.create_pdf_check = self._create_check_box(
            "Create PDF Report",
            output_defaults["create_pdf_report"]
        )
        self.export_csv_check = self._create_check_box(
            "Export CSV Data",
            output_defaults["export_csv"]
        )
        output_layout.Controls.Add(self.create_plan_check, 0, 0)
        output_layout.Controls.Add(self.create_3d_check, 1, 0)
        output_layout.Controls.Add(self.create_pdf_check, 0, 1)
        output_layout.Controls.Add(self.export_csv_check, 1, 1)

        phase_note = Label()
        phase_note.Text = (
            "Initial UI phase: selections are summarized only. "
            "No deviation analysis, views, PDF, or CSV will be created."
        )
        phase_note.Dock = DockStyle.Fill
        phase_note.AutoSize = False
        phase_note.ForeColor = MUTED_COLOR
        phase_note.Padding = Padding(2, 10, 0, 0)
        main_layout.Controls.Add(phase_note, 0, 5)

        button_layout = FlowLayoutPanel()
        button_layout.Dock = DockStyle.Fill
        button_layout.FlowDirection = FlowDirection.RightToLeft
        button_layout.WrapContents = False
        button_layout.Margin = Padding(0)
        button_layout.Padding = Padding(0, 8, 0, 0)
        main_layout.Controls.Add(button_layout, 0, 6)

        self.run_button = Button()
        self.run_button.Text = "Run"
        self.run_button.Size = Size(104, 34)
        self.run_button.Margin = Padding(10, 0, 0, 0)
        self._apply_primary_button_style(self.run_button)
        self.run_button.Click += self._confirm
        button_layout.Controls.Add(self.run_button)
        self.AcceptButton = self.run_button

        cancel_button = Button()
        cancel_button.Text = "Cancel"
        cancel_button.Size = Size(104, 34)
        cancel_button.Margin = Padding(10, 0, 0, 0)
        self._apply_secondary_button_style(cancel_button)
        cancel_button.DialogResult = DialogResult.Cancel
        button_layout.Controls.Add(cancel_button)
        self.CancelButton = cancel_button

        if point_clouds:
            self.point_cloud_combo.SelectedIndex = 0
        else:
            self.point_cloud_combo.Items.Add("No Point Cloud instances found")
            self.point_cloud_combo.SelectedIndex = 0
            self.point_cloud_combo.Enabled = False
            self.run_button.Enabled = False
            self.selected_point_cloud_label.Text = "Selected Point Cloud: Not available"

    def _create_group(self, text):
        group = GroupBox()
        group.Text = text
        group.Dock = DockStyle.Fill
        group.ForeColor = NAVY_COLOR
        group.Font = get_preferred_font(9.5, FontStyle.Bold)
        group.Margin = Padding(0, 4, 0, 4)
        return group

    def _create_tolerance_label(self, title, value, background_color):
        label = Label()
        label.Text = u"{0}\r\n{1}".format(title, value)
        label.Dock = DockStyle.Fill
        label.AutoSize = False
        label.TextAlign = ContentAlignment.MiddleCenter
        label.BackColor = background_color
        label.ForeColor = NAVY_COLOR
        label.Font = get_preferred_font(9.5, FontStyle.Bold)
        label.Margin = Padding(4)
        return label

    def _create_check_box(self, text, checked):
        check_box = CheckBox()
        check_box.Text = text
        check_box.Dock = DockStyle.Fill
        check_box.AutoSize = True
        check_box.Margin = Padding(6)
        check_box.ForeColor = NAVY_COLOR
        check_box.Font = get_preferred_font(9.5)
        check_box.Checked = checked
        return check_box

    def _apply_secondary_button_style(self, button):
        button.FlatStyle = FlatStyle.Flat
        button.FlatAppearance.BorderSize = 1
        button.FlatAppearance.BorderColor = BORDER_COLOR
        button.BackColor = Color.White
        button.ForeColor = NAVY_COLOR
        button.UseVisualStyleBackColor = False

    def _apply_primary_button_style(self, button):
        button.FlatStyle = FlatStyle.Flat
        button.FlatAppearance.BorderSize = 1
        button.FlatAppearance.BorderColor = BUTTON_NAVY_COLOR
        button.FlatAppearance.MouseOverBackColor = BUTTON_HOVER_COLOR
        button.FlatAppearance.MouseDownBackColor = NAVY_COLOR
        button.BackColor = BUTTON_NAVY_COLOR
        button.ForeColor = Color.White
        button.UseVisualStyleBackColor = False

    def _update_selected_point_cloud(self, sender, event_args):
        selected_index = self.point_cloud_combo.SelectedIndex
        if 0 <= selected_index < len(self.point_clouds):
            selected_point_cloud = self.point_clouds[selected_index]
            self.selected_point_cloud_label.Text = u"Selected Point Cloud: {0}".format(
                get_point_cloud_name(selected_point_cloud)
            )

    def _confirm(self, sender, event_args):
        selected_index = self.point_cloud_combo.SelectedIndex
        if selected_index < 0 or selected_index >= len(self.point_clouds):
            return

        selected_point_cloud = self.point_clouds[selected_index]
        selected_output_options = []

        if self.create_plan_check.Checked:
            selected_output_options.append(u"Create QC Plan View")
        if self.create_3d_check.Checked:
            selected_output_options.append(u"Create QC 3D View")
        if self.create_pdf_check.Checked:
            selected_output_options.append(u"Create PDF Report")
        if self.export_csv_check.Checked:
            selected_output_options.append(u"Export CSV Data")

        self.result = {
            "point_cloud_name": get_point_cloud_name(selected_point_cloud),
            "point_cloud_id": get_element_id_value(selected_point_cloud.Id),
            "selected_output_options": selected_output_options
        }
        self.DialogResult = DialogResult.OK
        self.Close()


def request_scan_qc_options(selected_wall_count, point_clouds, settings):
    options_form = ScanQcForm(selected_wall_count, point_clouds, settings)
    dialog_result = options_form.ShowDialog()
    selected_options = options_form.result
    options_form.Dispose()

    if dialog_result != DialogResult.OK or selected_options is None:
        return None

    return selected_options
