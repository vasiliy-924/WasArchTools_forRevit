# -*- coding: urf-8 -*-

__title__ = 'Моя просто кнопка.'
__author__ = 'WassiliyPertow'
__doc__ = 'Описание кнопки'

from Autodesk.Revit import DB

doc = __revit__.ActiveUIDocument.Document

def pin(el, status):
    el.get_Parameter(DB.BuiltInParameter.ELEMENT_LOCKER_PARAM).Set(status)
    print('Прикрепил ось. Имя: {} ID:{}'.format(el.Name, el.Id))

grids = DB.FilteredElementCollection(doc).\
            OfCategory(DB.BuiltInCategory.OST_Grids).\
            WhereElementIsNotElementType().\
            ToElements()

with DB.Transaction(doc, 'Автозакрепление') as t:
    t.Start()
    if grids:
        for grid in grids:
            pin(grid, 1)
        t.Commit()