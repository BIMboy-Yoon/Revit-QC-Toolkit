# -*- coding: utf-8 -*-

from Autodesk.Revit.DB import (
    BoundingBoxXYZ,
    FilteredElementCollector,
    SubTransaction,
    Transaction,
    TransactionStatus,
    Transform,
    UnitTypeId,
    UnitUtils,
    View,
    ViewDuplicateOption,
    ViewType,
    XYZ
)
from System import DateTime

from scan_qc.settings import (
    get_base_view_names,
    get_view_creation_options,
    get_view_template_names
)
from scan_qc.standards import find_3d_view, find_view_template


PLAN_VIEW_TYPES = (
    ViewType.FloorPlan,
    ViewType.CeilingPlan,
    ViewType.EngineeringPlan,
    ViewType.AreaPlan
)


def _to_text(value):
    if value is None:
        return u""

    try:
        return unicode(value)
    except NameError:
        return str(value)


def _get_view_names(doc):
    view_names = set()
    try:
        views = (
            FilteredElementCollector(doc)
            .OfClass(View)
            .WhereElementIsNotElementType()
            .ToElements()
        )
        for view in views:
            try:
                view_names.add(_to_text(view.Name))
            except Exception:
                pass
    except Exception:
        pass
    return view_names


def _get_unique_view_name(doc, base_name):
    existing_names = _get_view_names(doc)
    if base_name not in existing_names:
        return base_name

    suffix = 2
    while True:
        candidate = u"{0}_{1}".format(base_name, suffix)
        if candidate not in existing_names:
            return candidate
        suffix += 1


def _create_view_result(requested, template_name=u""):
    return {
        "requested": requested,
        "created": False,
        "view_name": u"",
        "template_name": template_name,
        "template_applied": False,
        "template_error": u"",
        "section_box_requested": False,
        "section_box_applied": False,
        "section_box_error": u"",
        "error": u""
    }


def _apply_view_template(doc, view, template_name):
    template = find_view_template(doc, template_name)
    if template is None:
        return False, u"View Template not found: {0}".format(template_name)

    try:
        if not view.IsValidViewTemplate(template.Id):
            return False, u"View Template is not valid for this view: {0}".format(
                template_name
            )
    except Exception as ex:
        return False, _to_text(ex)

    subtransaction = SubTransaction(doc)
    subtransaction_started = False
    try:
        subtransaction.Start()
        subtransaction_started = True
        view.ViewTemplateId = template.Id
        status = subtransaction.Commit()
        subtransaction_started = False
        if status != TransactionStatus.Committed:
            return False, u"Template sub-transaction ended with status: {0}".format(
                status
            )
        return True, u""
    except Exception as ex:
        if subtransaction_started:
            try:
                subtransaction.RollBack()
            except Exception:
                pass
        return False, _to_text(ex)


def _is_valid_active_plan_view(active_view):
    if active_view is None or active_view.IsTemplate:
        return False
    if active_view.ViewType not in PLAN_VIEW_TYPES:
        return False
    try:
        return active_view.CanViewBeDuplicated(ViewDuplicateOption.Duplicate)
    except Exception:
        return False


def create_scan_qc_plan_view(
    doc,
    active_view,
    template_name,
    timestamp=None
):
    """Duplicate a valid active plan without modifying the original view."""
    result = _create_view_result(True, template_name)
    if not _is_valid_active_plan_view(active_view):
        result["error"] = (
            u"The active view must be a duplicable Floor, Ceiling, Engineering, "
            u"or Area Plan view."
        )
        return result

    timestamp = timestamp or DateTime.Now.ToString("yyyyMMdd_HHmmss")
    view_name = _get_unique_view_name(
        doc,
        u"SCAN_QC_PLAN_{0}".format(timestamp)
    )
    transaction = Transaction(doc, "Create Scan QC Plan View")
    transaction_started = False

    try:
        transaction.Start()
        transaction_started = True
        duplicated_view_id = active_view.Duplicate(ViewDuplicateOption.Duplicate)
        duplicated_view = doc.GetElement(duplicated_view_id)
        duplicated_view.Name = view_name

        template_applied, template_error = _apply_view_template(
            doc,
            duplicated_view,
            template_name
        )
        result["template_applied"] = template_applied
        result["template_error"] = template_error

        status = transaction.Commit()
        transaction_started = False
        if status != TransactionStatus.Committed:
            result["error"] = u"Plan View transaction ended with status: {0}".format(
                status
            )
            return result

        result["created"] = True
        result["view_name"] = view_name
    except Exception as ex:
        result["error"] = _to_text(ex)
        if transaction_started:
            try:
                transaction.RollBack()
            except Exception:
                pass

    return result


def _get_bounding_box_corners(bounding_box):
    minimum = bounding_box.Min
    maximum = bounding_box.Max
    transform = bounding_box.Transform or Transform.Identity
    corners = []

    for x_value in (minimum.X, maximum.X):
        for y_value in (minimum.Y, maximum.Y):
            for z_value in (minimum.Z, maximum.Z):
                corners.append(
                    transform.OfPoint(XYZ(x_value, y_value, z_value))
                )

    return corners


def _build_wall_section_box(selected_walls, margin_mm):
    points = []
    for wall in selected_walls:
        try:
            bounding_box = wall.get_BoundingBox(None)
            if bounding_box is not None:
                points.extend(_get_bounding_box_corners(bounding_box))
        except Exception:
            pass

    if not points:
        return None, u"Selected Walls did not provide usable bounding boxes."

    try:
        margin_internal = UnitUtils.ConvertToInternalUnits(
            float(margin_mm),
            UnitTypeId.Millimeters
        )
    except Exception as ex:
        return None, u"Invalid section box margin: {0}".format(_to_text(ex))

    section_box = BoundingBoxXYZ()
    section_box.Transform = Transform.Identity
    section_box.Min = XYZ(
        min(point.X for point in points) - margin_internal,
        min(point.Y for point in points) - margin_internal,
        min(point.Z for point in points) - margin_internal
    )
    section_box.Max = XYZ(
        max(point.X for point in points) + margin_internal,
        max(point.Y for point in points) + margin_internal,
        max(point.Z for point in points) + margin_internal
    )
    return section_box, u""


def _apply_section_box(doc, view3d, section_box):
    subtransaction = SubTransaction(doc)
    subtransaction_started = False
    try:
        subtransaction.Start()
        subtransaction_started = True
        view3d.SetSectionBox(section_box)
        view3d.IsSectionBoxActive = True
        status = subtransaction.Commit()
        subtransaction_started = False
        if status != TransactionStatus.Committed:
            return False, u"Section box sub-transaction ended with status: {0}".format(
                status
            )
        return True, u""
    except Exception as ex:
        if subtransaction_started:
            try:
                subtransaction.RollBack()
            except Exception:
                pass
        return False, _to_text(ex)


def create_scan_qc_3d_view(
    doc,
    selected_walls,
    base_view_name,
    template_name,
    section_box_margin_mm,
    timestamp=None
):
    """Duplicate the installed Scan QC base 3D View and optionally crop to Walls."""
    result = _create_view_result(True, template_name)
    result["section_box_requested"] = bool(selected_walls)
    base_view = find_3d_view(doc, base_view_name)
    if base_view is None:
        result["error"] = u"Base 3D View not found: {0}".format(base_view_name)
        return result

    try:
        if not base_view.CanViewBeDuplicated(ViewDuplicateOption.Duplicate):
            result["error"] = u"Base 3D View cannot be duplicated: {0}".format(
                base_view_name
            )
            return result
    except Exception as ex:
        result["error"] = _to_text(ex)
        return result

    section_box = None
    if selected_walls:
        section_box, section_box_error = _build_wall_section_box(
            selected_walls,
            section_box_margin_mm
        )
        result["section_box_error"] = section_box_error

    timestamp = timestamp or DateTime.Now.ToString("yyyyMMdd_HHmmss")
    view_name = _get_unique_view_name(
        doc,
        u"SCAN_QC_3D_{0}".format(timestamp)
    )
    transaction = Transaction(doc, "Create Scan QC 3D View")
    transaction_started = False

    try:
        transaction.Start()
        transaction_started = True
        duplicated_view_id = base_view.Duplicate(ViewDuplicateOption.Duplicate)
        duplicated_view = doc.GetElement(duplicated_view_id)
        duplicated_view.Name = view_name

        template_applied, template_error = _apply_view_template(
            doc,
            duplicated_view,
            template_name
        )
        result["template_applied"] = template_applied
        result["template_error"] = template_error

        if section_box is not None:
            section_box_applied, section_box_error = _apply_section_box(
                doc,
                duplicated_view,
                section_box
            )
            result["section_box_applied"] = section_box_applied
            result["section_box_error"] = section_box_error
        else:
            duplicated_view.IsSectionBoxActive = False

        status = transaction.Commit()
        transaction_started = False
        if status != TransactionStatus.Committed:
            result["error"] = u"3D View transaction ended with status: {0}".format(
                status
            )
            return result

        result["created"] = True
        result["view_name"] = view_name
    except Exception as ex:
        result["error"] = _to_text(ex)
        if transaction_started:
            try:
                transaction.RollBack()
            except Exception:
                pass

    return result


def create_requested_scan_qc_views(
    doc,
    active_view,
    selected_walls,
    selected_options,
    settings
):
    """Create only the Scan QC working views selected in the dialog."""
    template_names = get_view_template_names(settings)
    base_view_names = get_base_view_names(settings)
    view_creation_options = get_view_creation_options(settings)
    timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss")
    plan_requested = selected_options.get("create_plan_view", False)
    view3d_requested = selected_options.get("create_3d_view", False)

    plan_result = _create_view_result(plan_requested, template_names["plan"])
    if plan_requested:
        plan_result = create_scan_qc_plan_view(
            doc,
            active_view,
            template_names["plan"],
            timestamp
        )

    view3d_result = _create_view_result(view3d_requested, template_names["view3d"])
    if view3d_requested:
        view3d_result = create_scan_qc_3d_view(
            doc,
            selected_walls,
            base_view_names["view3d"],
            template_names["view3d"],
            view_creation_options["section_box_margin_mm"],
            timestamp
        )

    return {
        "selected_wall_count": len(selected_walls),
        "section_box_margin_mm": view_creation_options["section_box_margin_mm"],
        "plan": plan_result,
        "view3d": view3d_result
    }
