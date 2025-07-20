# -*- coding: utf-8 -*-
"""
Модуль для работы с геометрией архитектурных объектов.
Содержит функции для анализа и преобразования геометрических данных.
"""

from Autodesk.Revit.DB import XYZ, Line

def generate_wall_points(wall, step=0.5):
    """
    Генерирует точки вдоль стены с заданным шагом и нормалью к стене в каждой точке.
    :param wall: Экземпляр стены Revit
    :param step: Шаг между точками (в единицах Revit)
    :return: Список кортежей (XYZ, normal)
    """
    curve = wall.Location.Curve
    length = curve.Length
    points = []
    curve_type = type(curve).__name__
    if not hasattr(curve, "Evaluate"):
        print(f"[!] Стена {getattr(wall, 'Id', '?')}: Кривая не поддерживает Evaluate")
        return points
    if length <= 0:
        print(f"[!] Стена {getattr(wall, 'Id', '?')}: Длина кривой <= 0")
        return points
    # Только для Line
    if curve_type != "Line":
        print(f"[!] Стена {getattr(wall, 'Id', '?')}: Кривая типа {curve_type} не поддерживается (только Line)")
        return points
    direction = curve.Direction
    # Нормаль в XY: (-Y, X, 0)
    normal = XYZ(-direction.Y, direction.X, 0)
    n_points = int(length // step)
    for i in range(n_points + 1):
        norm_param = (i * step) / length
        norm_param = min(max(norm_param, 0.0), 1.0)
        try:
            point = curve.Evaluate(norm_param, True)
            points.append((point, normal))
        except Exception as e:
            print(f"[!] Ошибка Evaluate для стены {getattr(wall, 'Id', '?')}, norm_param={norm_param}, тип кривой: {curve_type}: {e}")
    return points


def generate_curve_points(curve, step=0.5):
    """
    Генерирует точки вдоль кривой с заданным шагом и нормалью к кривой в каждой точке.
    :param curve: Кривая (Curve) сегмента стены
    :param step: Шаг между точками (в единицах Revit)
    :return: Список кортежей (XYZ, normal)
    """
    length = curve.Length
    points = []
    curve_type = type(curve).__name__
    if not hasattr(curve, "Evaluate"):
        print("[!] Кривая не поддерживает Evaluate")
        return points
    if length <= 0:
        print("[!] Длина кривой <= 0")
        return points
    # Только для Line
    if curve_type != "Line":
        print(f"[!] Кривая типа {curve_type} не поддерживается (только Line)")
        return points
    direction = curve.Direction
    normal = XYZ(-direction.Y, direction.X, 0)
    n_points = int(length // step)
    for i in range(n_points + 1):
        norm_param = (i * step) / length
        norm_param = min(max(norm_param, 0.0), 1.0)
        try:
            point = curve.Evaluate(norm_param, True)
            points.append((point, normal))
        except Exception as e:
            msg = (
                f"[!] Ошибка Evaluate для кривой, norm_param={norm_param}, "
                f"тип кривой: {curve_type}: {e}"
            )
            print(msg)
    return points
