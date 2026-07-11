# -*- coding: utf-8 -*-

"""WinForms settings UI for Interior Finish Takeoff."""

import clr

clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")

from System.Drawing import Color, ContentAlignment, Font, FontStyle, Size
from System.Windows.Forms import (
    AnchorStyles,
    Button,
    CheckBox,
    ComboBox,
    ComboBoxStyle,
    DialogResult,
    DockStyle,
    FolderBrowserDialog,
    Form,
    FormBorderStyle,
    FormStartPosition,
    Label,
    Padding,
    TableLayoutPanel,
    TextBox,
    ColumnStyle,
    RowStyle,
    SizeType
)

from interior_finish_takeoff.config import (
    PART_POLICIES,
    REPORT_FORMATS,
    normalize_settings
)
from interior_finish_takeoff.constants import (
    TARGET_CEILING,
    TARGET_FLOOR,
    TARGET_PART,
    TARGET_WALL
)


def show_settings_dialog(settings):
    form = SettingsForm(settings)
    result = form.ShowDialog()
    if result == DialogResult.OK:
        return form.get_settings()
    return None


def show_run_takeoff_options_dialog(settings):
    form = RunTakeoffOptionsForm(settings)
    result = form.ShowDialog()
    if result == DialogResult.OK:
        return form.get_options()
    return None


class RunTakeoffOptionsForm(Form):
    def __init__(self, settings):
        self._settings = settings
        self.Text = "Run Interior Finish Takeoff"
        self.ClientSize = Size(680, 500)
        self.MinimumSize = Size(640, 480)
        self.StartPosition = FormStartPosition.CenterScreen
        self.FormBorderStyle = FormBorderStyle.Sizable
        self.BackColor = Color.White
        self.Font = Font("Segoe UI", 9.0)
        self._build_layout()
        self._load_defaults(settings)

    def _build_layout(self):
        self.root = TableLayoutPanel()
        self.root.Dock = DockStyle.Fill
        self.root.Padding = Padding(18)
        self.root.ColumnCount = 2
        self.root.RowCount = 14
        self.root.ColumnStyles.Add(ColumnStyle(SizeType.Absolute, 230.0))
        self.root.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 100.0))
        self.Controls.Add(self.root)

        title = Label()
        title.Text = "Run Takeoff Options"
        title.Font = Font("Segoe UI", 13.0, FontStyle.Bold)
        title.Dock = DockStyle.Fill
        title.TextAlign = ContentAlignment.MiddleLeft
        self.root.Controls.Add(title, 0, 0)
        self.root.SetColumnSpan(title, 2)
        self.root.RowStyles.Add(RowStyle(SizeType.Absolute, 44.0))

        self.scope = self._add_combo_row(
            1,
            "Scope",
            ("selected_or_view", "selected_rooms", "current_view")
        )
        self.include_walls = self._add_checkbox_row(2, "Category: Walls")
        self.include_floors = self._add_checkbox_row(3, "Category: Floors")
        self.include_ceilings = self._add_checkbox_row(4, "Category: Ceilings")
        self.include_parts = self._add_checkbox_row(5, "Category: Parts")
        self.include_type_material = self._add_checkbox_row(
            6,
            "Material Source: Type/Layer"
        )
        self.include_paint = self._add_checkbox_row(
            7,
            "Material Source: Paint"
        )
        self.part_policy = self._add_combo_row(
            8,
            "Part Policy",
            PART_POLICIES
        )
        self.open_report = self._add_checkbox_row(9, "Open HTML Report")

        spacer = Label()
        spacer.Text = ""
        self.root.Controls.Add(spacer, 0, 10)
        self.root.SetColumnSpan(spacer, 2)
        self.root.RowStyles.Add(RowStyle(SizeType.Percent, 100.0))

        cancel_button = Button()
        cancel_button.Text = "Cancel"
        cancel_button.Width = 110
        cancel_button.Height = 34
        cancel_button.Anchor = AnchorStyles.Right
        cancel_button.DialogResult = DialogResult.Cancel
        self.root.Controls.Add(cancel_button, 0, 11)

        run_button = Button()
        run_button.Text = "Run"
        run_button.Width = 110
        run_button.Height = 34
        run_button.Anchor = AnchorStyles.Right
        run_button.DialogResult = DialogResult.OK
        self.root.Controls.Add(run_button, 1, 11)

        self.AcceptButton = run_button
        self.CancelButton = cancel_button
        self.root.RowStyles.Add(RowStyle(SizeType.Absolute, 48.0))

    def _add_label(self, row_index, text):
        label = Label()
        label.Text = text
        label.Dock = DockStyle.Fill
        label.TextAlign = ContentAlignment.MiddleLeft
        label.Padding = Padding(0, 3, 10, 3)
        self.root.Controls.Add(label, 0, row_index)
        self.root.RowStyles.Add(RowStyle(SizeType.Absolute, 38.0))
        return label

    def _add_checkbox_row(self, row_index, label_text):
        self._add_label(row_index, label_text)
        control = CheckBox()
        control.Dock = DockStyle.Fill
        control.Padding = Padding(0, 6, 0, 0)
        self.root.Controls.Add(control, 1, row_index)
        return control

    def _add_combo_row(self, row_index, label_text, options):
        self._add_label(row_index, label_text)
        control = ComboBox()
        control.Dock = DockStyle.Fill
        control.DropDownStyle = ComboBoxStyle.DropDownList
        for option in options:
            control.Items.Add(option)
        self.root.Controls.Add(control, 1, row_index)
        return control

    def _load_defaults(self, settings):
        self._set_combo_value(self.scope, "selected_or_view")
        self.include_walls.Checked = True
        self.include_floors.Checked = True
        self.include_ceilings.Checked = True
        self.include_parts.Checked = bool(settings.get("include_parts", True))
        self.include_type_material.Checked = bool(
            settings.get("include_type_material", True)
        )
        self.include_paint.Checked = bool(settings.get("include_paint", True))
        self._set_combo_value(
            self.part_policy,
            settings.get("part_policy", PART_POLICIES[0])
        )
        self.open_report.Checked = True

    def get_options(self):
        target_types = []
        if self.include_walls.Checked:
            target_types.append(TARGET_WALL)
        if self.include_floors.Checked:
            target_types.append(TARGET_FLOOR)
        if self.include_ceilings.Checked:
            target_types.append(TARGET_CEILING)
        if self.include_parts.Checked:
            target_types.append(TARGET_PART)

        return {
            "scope": _selected_combo_text(self.scope),
            "target_types": target_types,
            "include_paint": self.include_paint.Checked,
            "include_type_material": self.include_type_material.Checked,
            "include_parts": self.include_parts.Checked,
            "part_policy": _selected_combo_text(self.part_policy),
            "open_report": self.open_report.Checked
        }

    def _set_combo_value(self, combo, value):
        for index in range(combo.Items.Count):
            if _to_text(combo.Items[index]) == _to_text(value):
                combo.SelectedIndex = index
                return
        if combo.Items.Count:
            combo.SelectedIndex = 0


class SettingsForm(Form):
    def __init__(self, settings):
        self._initial_settings = settings
        self.Text = "Interior Finish Takeoff Settings"
        self.ClientSize = Size(760, 650)
        self.MinimumSize = Size(720, 620)
        self.StartPosition = FormStartPosition.CenterScreen
        self.FormBorderStyle = FormBorderStyle.Sizable
        self.BackColor = Color.White
        self.Font = Font("Segoe UI", 9.0)
        self._build_layout()
        self._load_settings(settings)

    def _build_layout(self):
        self.root = TableLayoutPanel()
        self.root.Dock = DockStyle.Fill
        self.root.Padding = Padding(18)
        self.root.ColumnCount = 2
        self.root.RowCount = 18
        self.root.ColumnStyles.Add(ColumnStyle(SizeType.Absolute, 250.0))
        self.root.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 100.0))
        self.Controls.Add(self.root)

        self.title_label = Label()
        self.title_label.Text = "Interior Finish Takeoff Settings"
        self.title_label.Font = Font("Segoe UI", 13.0, FontStyle.Bold)
        self.title_label.Height = 36
        self.title_label.Dock = DockStyle.Fill
        self.title_label.TextAlign = ContentAlignment.MiddleLeft
        self.root.Controls.Add(self.title_label, 0, 0)
        self.root.SetColumnSpan(self.title_label, 2)
        self.root.RowStyles.Add(RowStyle(SizeType.Absolute, 44.0))

        self.include_paint = self._add_checkbox_row(1, "Include Paint")
        self.include_type_material = self._add_checkbox_row(
            2,
            "Include Type Material"
        )
        self.include_parts = self._add_checkbox_row(3, "Include Parts")
        self.part_policy = self._add_combo_row(
            4,
            "Part Policy",
            PART_POLICIES
        )
        self.default_wall_finish_height_mm = self._add_text_row(
            5,
            "Default Wall Finish Height (mm)"
        )
        self.default_ceiling_offset_mm = self._add_text_row(
            6,
            "Default Ceiling Offset (mm)"
        )
        self.default_waste_rate_wall = self._add_text_row(
            7,
            "Default Wall Waste Rate"
        )
        self.default_waste_rate_floor = self._add_text_row(
            8,
            "Default Floor Waste Rate"
        )
        self.default_waste_rate_ceiling = self._add_text_row(
            9,
            "Default Ceiling Waste Rate"
        )
        self.default_skirting_height_mm = self._add_text_row(
            10,
            "Default Skirting Height (mm)"
        )
        self.default_skirting_waste_rate = self._add_text_row(
            11,
            "Default Skirting Waste Rate"
        )
        self.output_folder = self._add_folder_row(12, "Output Folder")
        self.report_format = self._add_combo_row(
            13,
            "Report Format",
            REPORT_FORMATS
        )

        spacer = Label()
        spacer.Text = ""
        self.root.Controls.Add(spacer, 0, 14)
        self.root.SetColumnSpan(spacer, 2)
        self.root.RowStyles.Add(RowStyle(SizeType.Percent, 100.0))

        self.cancel_button = Button()
        self.cancel_button.Text = "Cancel"
        self.cancel_button.Width = 110
        self.cancel_button.Height = 34
        self.cancel_button.Anchor = AnchorStyles.Right
        self.cancel_button.DialogResult = DialogResult.Cancel
        self.root.Controls.Add(self.cancel_button, 0, 15)

        self.save_button = Button()
        self.save_button.Text = "Save"
        self.save_button.Width = 110
        self.save_button.Height = 34
        self.save_button.Anchor = AnchorStyles.Right
        self.save_button.DialogResult = DialogResult.OK
        self.root.Controls.Add(self.save_button, 1, 15)

        self.AcceptButton = self.save_button
        self.CancelButton = self.cancel_button
        self.root.RowStyles.Add(RowStyle(SizeType.Absolute, 48.0))

    def _add_label(self, row_index, text):
        label = Label()
        label.Text = text
        label.Dock = DockStyle.Fill
        label.TextAlign = ContentAlignment.MiddleLeft
        label.Padding = Padding(0, 3, 10, 3)
        self.root.Controls.Add(label, 0, row_index)
        self.root.RowStyles.Add(RowStyle(SizeType.Absolute, 40.0))
        return label

    def _add_checkbox_row(self, row_index, label_text):
        self._add_label(row_index, label_text)
        control = CheckBox()
        control.Dock = DockStyle.Fill
        control.Text = ""
        control.Padding = Padding(0, 6, 0, 0)
        self.root.Controls.Add(control, 1, row_index)
        return control

    def _add_text_row(self, row_index, label_text):
        self._add_label(row_index, label_text)
        control = TextBox()
        control.Dock = DockStyle.Fill
        self.root.Controls.Add(control, 1, row_index)
        return control

    def _add_combo_row(self, row_index, label_text, options):
        self._add_label(row_index, label_text)
        control = ComboBox()
        control.Dock = DockStyle.Fill
        control.DropDownStyle = ComboBoxStyle.DropDownList
        for option in options:
            control.Items.Add(option)
        self.root.Controls.Add(control, 1, row_index)
        return control

    def _add_folder_row(self, row_index, label_text):
        self._add_label(row_index, label_text)
        row = TableLayoutPanel()
        row.Dock = DockStyle.Fill
        row.ColumnCount = 2
        row.ColumnStyles.Add(ColumnStyle(SizeType.Percent, 100.0))
        row.ColumnStyles.Add(ColumnStyle(SizeType.Absolute, 92.0))
        self.root.Controls.Add(row, 1, row_index)

        text_box = TextBox()
        text_box.Dock = DockStyle.Fill
        row.Controls.Add(text_box, 0, 0)

        button = Button()
        button.Text = "Browse"
        button.Dock = DockStyle.Fill
        button.Click += self._browse_output_folder
        row.Controls.Add(button, 1, 0)
        return text_box

    def _load_settings(self, settings):
        self.include_paint.Checked = bool(settings["include_paint"])
        self.include_type_material.Checked = bool(
            settings["include_type_material"]
        )
        self.include_parts.Checked = bool(settings["include_parts"])
        self._set_combo_value(self.part_policy, settings["part_policy"])
        self.default_wall_finish_height_mm.Text = _to_text(
            settings["default_wall_finish_height_mm"]
        )
        self.default_ceiling_offset_mm.Text = _to_text(
            settings["default_ceiling_offset_mm"]
        )
        self.default_waste_rate_wall.Text = _to_text(
            settings["default_waste_rate_wall"]
        )
        self.default_waste_rate_floor.Text = _to_text(
            settings["default_waste_rate_floor"]
        )
        self.default_waste_rate_ceiling.Text = _to_text(
            settings["default_waste_rate_ceiling"]
        )
        self.default_skirting_height_mm.Text = _to_text(
            settings["default_skirting_height_mm"]
        )
        self.default_skirting_waste_rate.Text = _to_text(
            settings["default_skirting_waste_rate"]
        )
        self.output_folder.Text = _to_text(settings["output_folder"])
        self._set_combo_value(self.report_format, settings["report_format"])

    def get_settings(self):
        raw_settings = {
            "include_paint": self.include_paint.Checked,
            "include_type_material": self.include_type_material.Checked,
            "include_parts": self.include_parts.Checked,
            "part_policy": _selected_combo_text(self.part_policy),
            "default_wall_finish_height_mm": self.default_wall_finish_height_mm.Text,
            "default_ceiling_offset_mm": self.default_ceiling_offset_mm.Text,
            "default_waste_rate_wall": self.default_waste_rate_wall.Text,
            "default_waste_rate_floor": self.default_waste_rate_floor.Text,
            "default_waste_rate_ceiling": self.default_waste_rate_ceiling.Text,
            "default_skirting_height_mm": self.default_skirting_height_mm.Text,
            "default_skirting_waste_rate": self.default_skirting_waste_rate.Text,
            "output_folder": self.output_folder.Text,
            "report_format": _selected_combo_text(self.report_format)
        }
        return normalize_settings(raw_settings, self._initial_settings)

    def _set_combo_value(self, combo, value):
        for index in range(combo.Items.Count):
            if _to_text(combo.Items[index]) == _to_text(value):
                combo.SelectedIndex = index
                return
        if combo.Items.Count:
            combo.SelectedIndex = 0

    def _browse_output_folder(self, sender, args):
        dialog = FolderBrowserDialog()
        dialog.Description = "Select Interior Finish Takeoff output folder"
        dialog.SelectedPath = self.output_folder.Text
        if dialog.ShowDialog() == DialogResult.OK:
            self.output_folder.Text = dialog.SelectedPath


def _selected_combo_text(combo):
    if combo.SelectedItem is None:
        return ""
    return _to_text(combo.SelectedItem)


def _to_text(value):
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return ""
