# -*- coding: utf-8 -*-

__title__ = "MyAnotherButton"
__author__ = 'Was924'
__doc__ = "Description of the button"

"""Calculates total volume of all walls in the model."""

from Autodesk.Revit import DB


doc = __revit__.ActiveUIDocument.Document


# Creating collector instance and collecting all the walls from the model
wall_collector = DB.FilteredElementCollector(doc)\
                   .OfCategory(DB.BuiltInCategory.OST_Walls)\
                   .WhereElementIsNotElementType()


# Iterate over wall and collect Volume data
total_volume = 0.0

for wall in wall_collector:
    vol_param = wall.Parameter[DB.BuiltInParameter.HOST_VOLUME_COMPUTED]
    if vol_param:
        total_volume = total_volume + vol_param.AsDouble()

# now that results are collected, print the total
print("Total Volume of walls is: {}".format(total_volume))