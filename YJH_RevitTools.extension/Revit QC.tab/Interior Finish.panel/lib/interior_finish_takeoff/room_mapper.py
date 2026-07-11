# -*- coding: utf-8 -*-

"""Room collection and boundary mapping for Interior Finish Takeoff."""

from interior_finish_takeoff.qc_flags import (
    FLAG_API_EXCEPTION,
    FLAG_ROOM_BOUNDARY_ERROR,
    add_flag,
    normalize_flags
)
from interior_finish_takeoff.schemas import RoomMappingRecord
from interior_finish_takeoff.units import (
    revit_area_to_m2,
    revit_length_to_m,
    round_area_m2,
    round_length_m
)

try:
    from Autodesk.Revit.DB import (
        BuiltInCategory,
        FilteredElementCollector,
        SpatialElementBoundaryOptions
    )
except Exception:
    BuiltInCategory = None
    FilteredElementCollector = None
    SpatialElementBoundaryOptions = None


def collect_context_rooms(doc, uidoc=None, view=None):
    """Return selected Rooms, or Rooms visible in the current view.

    Linked model rooms are intentionally excluded in this MVP because only the
    active document is queried.
    """
    selected_rooms = collect_selected_rooms(doc, uidoc)
    if selected_rooms:
        return selected_rooms
    if view is None and doc is not None:
        try:
            view = doc.ActiveView
        except Exception:
            view = None
    return collect_rooms_in_view(doc, view)


def collect_rooms_by_scope(doc, uidoc=None, view=None, scope=u"selected_or_view"):
    """Collect rooms by explicit run scope."""
    if scope == u"selected_rooms":
        return collect_selected_rooms(doc, uidoc)
    if scope == u"current_view":
        if view is None and doc is not None:
            try:
                view = doc.ActiveView
            except Exception:
                view = None
        return collect_rooms_in_view(doc, view)
    return collect_context_rooms(doc, uidoc, view)


def collect_selected_rooms(doc, uidoc):
    """Collect selected Room elements from the active document only."""
    if doc is None or uidoc is None:
        return []
    try:
        selected_ids = uidoc.Selection.GetElementIds()
    except Exception:
        return []

    rooms = []
    for element_id in selected_ids:
        try:
            element = doc.GetElement(element_id)
        except Exception:
            element = None
        if is_room_element(element):
            rooms.append(element)
    return rooms


def collect_rooms_in_view(doc, view):
    """Collect Room elements visible in a Revit view."""
    if doc is None or view is None:
        return []
    if BuiltInCategory is None or FilteredElementCollector is None:
        raise RuntimeError("Revit API is not available.")
    try:
        return list(
            FilteredElementCollector(doc, view.Id)
            .OfCategory(BuiltInCategory.OST_Rooms)
            .WhereElementIsNotElementType()
            .ToElements()
        )
    except Exception:
        return []


def build_room_mapping_records(doc, rooms):
    """Build JSON-exportable room mapping records with boundary metadata."""
    records = []
    for room in rooms:
        records.append(build_room_mapping_record(doc, room))
    return records


def build_room_mapping_record(doc, room):
    """Create one RoomMappingRecord from a Revit Room."""
    flags = []
    boundary_length_m, boundary_flags = get_room_boundary_length_m(room)
    flags = normalize_flags(flags + boundary_flags)
    room_area_m2 = get_room_area_m2(room)
    room_id = get_element_id_value(getattr(room, "Id", None))
    level_id, level_name = get_room_level_info(doc, room)

    return RoomMappingRecord(
        room_id=room_id,
        room_unique_id=_to_text(getattr(room, "UniqueId", u"")),
        room_number=get_room_number(room),
        room_name=get_room_name(room),
        level_id=level_id,
        level_name=level_name,
        department=get_room_parameter_text(room, ("Department", "부서")),
        area_m2=room_area_m2,
        finish_wall=get_room_parameter_text(
            room,
            ("Wall Finish", "벽 마감", "Finish Wall")
        ),
        finish_floor=get_room_parameter_text(
            room,
            ("Floor Finish", "바닥 마감", "Finish Floor")
        ),
        finish_ceiling=get_room_parameter_text(
            room,
            ("Ceiling Finish", "천장 마감", "Finish Ceiling")
        ),
        baseboard_type=get_room_parameter_text(
            room,
            ("Base Finish", "Skirting", "Baseboard", "걸레받이")
        ),
        mapping_status=u"MAPPED" if not flags else u"REVIEW",
        flags=flags,
        metadata={
            "boundary_length_m": boundary_length_m,
            "deduction_mode": "none",
            "linked_model_included": False
        }
    )


def get_room_boundary_length_m(room):
    """Calculate total Room boundary segment length in meters."""
    if room is None or SpatialElementBoundaryOptions is None:
        return 0.0, [FLAG_ROOM_BOUNDARY_ERROR]
    try:
        options = SpatialElementBoundaryOptions()
        boundaries = room.GetBoundarySegments(options)
    except Exception:
        return 0.0, [FLAG_ROOM_BOUNDARY_ERROR, FLAG_API_EXCEPTION]

    if not boundaries:
        return 0.0, [FLAG_ROOM_BOUNDARY_ERROR]

    length_ft = 0.0
    segment_count = 0
    try:
        for loop in boundaries:
            for segment in loop:
                curve = segment.GetCurve()
                length_ft += curve.Length
                segment_count += 1
    except Exception:
        return 0.0, [FLAG_ROOM_BOUNDARY_ERROR, FLAG_API_EXCEPTION]

    if segment_count == 0 or length_ft == 0.0:
        return 0.0, [FLAG_ROOM_BOUNDARY_ERROR]
    return round_length_m(revit_length_to_m(length_ft)), []


def get_room_area_m2(room):
    try:
        return round_area_m2(revit_area_to_m2(room.Area))
    except Exception:
        return 0.0


def is_room_element(element):
    if element is None:
        return False
    if BuiltInCategory is not None:
        try:
            category_id = element.Category.Id.IntegerValue
            room_category_id = int(BuiltInCategory.OST_Rooms)
            return category_id == room_category_id
        except Exception:
            pass
    try:
        return element.Category.Name == "Rooms"
    except Exception:
        return False


def get_room_level_info(doc, room):
    level_id = None
    level_name = u""
    try:
        level_id = room.LevelId
    except Exception:
        level_id = None
    if level_id is not None and doc is not None:
        try:
            level = doc.GetElement(level_id)
            level_name = _to_text(level.Name)
        except Exception:
            level_name = u""
    return get_element_id_value(level_id), level_name


def get_room_number(room):
    try:
        return _to_text(room.Number)
    except Exception:
        return get_room_parameter_text(room, ("Number", "Room Number", "번호"))


def get_room_name(room):
    try:
        return _to_text(room.Name)
    except Exception:
        return get_room_parameter_text(room, ("Name", "Room Name", "이름"))


def get_room_parameter_text(room, names):
    for name in names:
        try:
            parameter = room.LookupParameter(name)
            if parameter is not None:
                value = parameter.AsString()
                if value:
                    return _to_text(value)
                value = parameter.AsValueString()
                if value:
                    return _to_text(value)
        except Exception:
            pass
    return u""


def get_element_id_value(element_id):
    if element_id is None:
        return None
    try:
        return str(element_id.IntegerValue)
    except Exception:
        pass
    try:
        return str(element_id.Value)
    except Exception:
        pass
    try:
        return str(element_id)
    except Exception:
        return None


def _to_text(value):
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return u""
