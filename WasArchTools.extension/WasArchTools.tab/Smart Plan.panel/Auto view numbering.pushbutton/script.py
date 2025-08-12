"""Copy token from View.Name into Viewport Detail Number.

Selection-based only:
- Select one or more Viewports on sheet, or Views in Project Browser,
  or Sheets (to process their viewports), then run the script.

Rule:
- Token is substring before " - " (space-hyphen-space). If not found, use
  the full trimmed View.Name.
"""

import importlib
import re


def _extract_token(view_name):
    if not view_name:
        return None
    # Take characters from start until first space or hyphen
    name = view_name.strip()
    match = re.match(r"^([^\s\-]+)", name)
    return match.group(1) if match else name


def _gather_viewports_from_selection(db_module, doc, uidoc):
    selected_ids = list(uidoc.Selection.GetElementIds())
    if not selected_ids:
        return []

    # Build map ViewId -> [Viewport, ...] once for efficient lookup
    all_viewports = (
        db_module.FilteredElementCollector(doc)
        .OfClass(db_module.Viewport)
        .ToElements()
    )
    viewid_to_viewports = {}
    for vp in all_viewports:
        viewid_to_viewports.setdefault(vp.ViewId, []).append(vp)

    targets = []
    for elid in selected_ids:
        el = doc.GetElement(elid)
        if el is None:
            continue
        if isinstance(el, db_module.Viewport):
            targets.append(el)
        elif isinstance(el, db_module.View) and not el.IsTemplate:
            # Map selected View to its placed Viewports (if any)
            vps = viewid_to_viewports.get(el.Id)
            if vps:
                targets.extend(vps)
        elif isinstance(el, db_module.ViewSheet):
            # All viewports on the selected sheet
            sheet_vps = (
                db_module.FilteredElementCollector(doc, el.Id)
                .OfClass(db_module.Viewport)
                .ToElements()
            )
            targets.extend(sheet_vps)

    # Deduplicate
    unique = {}
    for vp in targets:
        unique[vp.Id.IntegerValue] = vp
    return list(unique.values())


def main():
    # Load Revit API
    clr = importlib.import_module("clr")
    clr.AddReference("RevitAPI")

    # Import DB
    _ns = {}
    exec('from Autodesk.Revit import DB as __DB', _ns, _ns)
    DB = _ns['__DB']

    # Resolve doc/uidoc via pyRevit when available, otherwise __revit__
    revit_mod = None
    try:
        revit_mod = importlib.import_module("pyrevit.revit")
    except Exception:
        revit_mod = None

    if revit_mod is not None:
        uidoc = revit_mod.uidoc
        doc = revit_mod.doc
    else:
        revit_ctx = globals().get("__revit__")
        if revit_ctx is None:
            return
        uidoc = revit_ctx.ActiveUIDocument
        doc = uidoc.Document

    # Selection is required per spec
    target_viewports = _gather_viewports_from_selection(DB, doc, uidoc)
    if not target_viewports:
        return

    t = DB.Transaction(doc, "Auto view numbering")
    t.Start()
    try:
        for vp in target_viewports:
            view = doc.GetElement(vp.ViewId)
            if view is None:
                continue
            token = _extract_token(view.Name)
            if not token:
                continue
            param = vp.get_Parameter(
                DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER
            )
            if param and not param.IsReadOnly:
                try:
                    param.Set(token)
                except Exception:
                    # Ignore failures (e.g., duplicate number on same sheet)
                    pass
    finally:
        t.Commit()


if __name__ == "__main__":
    main()
