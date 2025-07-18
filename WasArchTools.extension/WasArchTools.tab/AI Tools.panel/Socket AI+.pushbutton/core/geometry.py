#! python3
# -*- coding: utf-8 -*-
"""
Модуль для работы с геометрией архитектурных объектов.
Содержит функции для анализа и преобразования геометрических данных.
"""

from Autodesk.Revit.DB import XYZ, Line

def generate_wall_points(wall, step=0.5):
    """
    Генерирует точки вдоль стены с заданным шагом.
    :param wall: Экземпляр стены Revit
    :param step: Шаг между точками (в единицах Revit)
    :return: Список точек XYZ
    """
    curve = wall.Location.Curve
    length = curve.Length
    points = []
    for i in range(int(length // step)):
        param = curve.GetEndParameter(0) + i * step
        points.append(curve.Evaluate(param, True))
    return points
