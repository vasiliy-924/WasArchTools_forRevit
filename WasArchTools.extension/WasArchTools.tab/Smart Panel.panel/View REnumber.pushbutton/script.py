"""Copy token from View.Name into Viewport Detail Number.

Selection-based only:
- Select one or more Viewports on sheet, or Views in Project Browser,
  or Sheets (to process their viewports), then run the script.

Rule:
- Token is substring before first space or hyphen. If not found, use
  the full trimmed View.Name.
"""

import importlib
import re


def _extract_token(view_name):
    if not view_name:
        return None
    # Take characters from start until " -" or "-"
    name = view_name.strip()
    # Look for " -" first, then "-"
    if " -" in name:
        return name.split(" -")[0]
    elif "-" in name:
        return name.split("-")[0]
    else:
        return name


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
    clr.AddReference("RevitAPIUI")

    # Import DB and UI with fallback
    try:
        DB = importlib.import_module("Autodesk.Revit.DB")
    except ImportError:
        ns_db = {}
        exec('from Autodesk.Revit import DB as __DB', ns_db, ns_db)
        DB = ns_db['__DB']

    try:
        UI = importlib.import_module("Autodesk.Revit.UI")
    except ImportError:
        ns_ui = {}
        exec('from Autodesk.Revit import UI as __UI', ns_ui, ns_ui)
        UI = ns_ui['__UI']

    # Resolve doc/uidoc via pyRevit when available, else __revit__
    try:
        revit_mod = importlib.import_module("pyrevit.revit")
        uidoc = revit_mod.uidoc
        doc = revit_mod.doc
    except ImportError:
        revit_ctx = globals().get("__revit__")
        if revit_ctx is None:
            return
        uidoc = revit_ctx.ActiveUIDocument
        doc = uidoc.Document

    # Selection is required per spec
    target_viewports = _gather_viewports_from_selection(DB, doc, uidoc)
    if not target_viewports:
        UI.TaskDialog.Show(
            "Auto view numbering",
            "Выдели хотя бы 1 Viewport",
        )
        return

    updated = 0
    skipped_no_token = 0
    failed = 0

    t = DB.Transaction(doc, "Auto view numbering")
    t.Start()
    try:
        for vp in target_viewports:
            view = doc.GetElement(vp.ViewId)
            if view is None:
                continue
            token = _extract_token(view.Name)
            if not token:
                skipped_no_token += 1
                continue
            param = vp.get_Parameter(
                DB.BuiltInParameter.VIEWPORT_DETAIL_NUMBER
            )
            if param and not param.IsReadOnly:
                try:
                    param.Set(token)
                    updated += 1
                except Exception:
                    failed += 1
            else:
                failed += 1
    finally:
        t.Commit()

    UI.TaskDialog.Show(
        "Auto view numbering",
        (
            "Готово.\n"
            "Обновлено: {0}\n"
            "Пропущено (нет токена): {1}\n"
            "Ошибок: {2}".format(updated, skipped_no_token, failed)
        ),
    )


if __name__ == "__main__":
    main()
