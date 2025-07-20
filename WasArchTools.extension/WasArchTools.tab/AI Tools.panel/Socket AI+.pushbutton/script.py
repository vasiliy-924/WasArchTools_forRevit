# -*- coding: utf-8 -*-
"""
Скрипт для автоматической расстановки розеток в выбранных помещениях.
Использует правила из assets/rules.json.
"""
from pyrevit import revit, DB, forms
# from core.geometry import generate_wall_points  # больше не используется
from core.geometry import generate_curve_points
from core.rules_engine import RuleEngine
import ui

print('Отладочный вывод')

def get_selected_rooms():
    selection = revit.get_selection()
    print("Выделено элементов:", len(selection))
    rooms = []
    for el in selection:
        cat_name = getattr(el.Category, 'Name', None)
        print("Тип:", type(el), "Категория:", cat_name)
        # Корректная фильтрация помещений
        if isinstance(el, DB.SpatialElement) and cat_name in ["Помещения", "Rooms"]:
            rooms.append(el)
    print(f"Найдено помещений: {len(rooms)}")
    return rooms

def get_room_walls(room):
    doc = room.Document
    boundaries = room.GetBoundarySegments(DB.SpatialElementBoundaryOptions())
    if not boundaries:
        print(f"[!] Нет границ для помещения: {getattr(room, 'Name', None)}")
        return []
    walls = []
    for segment in boundaries[0]:
        wall = doc.GetElement(segment.ElementId)
        if isinstance(wall, DB.Wall):
            walls.append(wall)
    if not walls:
        print(f"[!] Нет стен для помещения: {getattr(room, 'Name', None)}")
    return walls

def get_bottom_wall(room, walls):
    """
    Определяет нижнюю стену помещения по минимальной Y-координате центра стены.
    :param room: объект Room
    :param walls: список стен
    :return: стена с минимальным Y центра
    """
    # Получаем bounding box помещения
    bbox = room.get_BoundingBox(None)
    if not bbox:
        return None
    min_y = bbox.Min.Y
    # Найдём стену, у которой центр ближе всего к min_y
    min_wall = None
    min_dist = None
    for wall in walls:
        curve = wall.Location.Curve
        mid = curve.Evaluate(0.5, True)
        dist = abs(mid.Y - min_y)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            min_wall = wall
    return min_wall

def get_socket_types(doc):
    symbols = DB.FilteredElementCollector(doc)\
        .OfCategory(DB.BuiltInCategory.OST_ElectricalFixtures)\
        .OfClass(DB.FamilySymbol)\
        .ToElements()
    return symbols

def get_room_wall_segments(room):
    doc = room.Document
    boundaries = room.GetBoundarySegments(DB.SpatialElementBoundaryOptions())
    if not boundaries:
        print(f"[!] Нет границ для помещения: {getattr(room, 'Name', None)}")
        return []
    segments = []
    for segment in boundaries[0]:
        wall = doc.GetElement(segment.ElementId)
        if isinstance(wall, DB.Wall):
            segments.append((wall, segment.GetCurve()))
    if not segments:
        print(f"[!] Нет стен для помещения: {getattr(room, 'Name', None)}")
    return segments

def place_sockets(selected_rooms, socket_symbol):
    """
    Расставляет розетки в выбранных помещениях по правилам из rules.json.
    :param selected_rooms: список объектов Room
    :param socket_symbol: выбранный FamilySymbol розетки
    """
    engine = RuleEngine()
    doc = revit.doc
    success_count = 0
    fail_count = 0
    with revit.Transaction("Разместить розетки"):
        for room in selected_rooms:
            room_name = getattr(room, 'Name', None)
            try:
                rules = engine.get_room_rules(room_name)
                print(f"Правила для '{room_name}': {rules}")
                if not rules or 'step' not in rules:
                    print(f"[!] Нет параметра 'step' в правилах для помещения '{room_name}'")
                    continue
            except Exception as e:
                print(f"[!] Ошибка при получении правил для '{room_name}': {e}")
                continue
            segments = get_room_wall_segments(room)
            if not segments:
                continue
            # Определяем нижнюю стену (по-прежнему по всей стене)
            bottom_wall = get_bottom_wall(room, [wall for wall, _ in segments])
            # Получаем высоту из правил или по умолчанию 0.25 м
            height = rules.get("height", 0.25)
            for wall, curve in segments:
                try:
                    points_normals = generate_curve_points(curve, rules["step"])
                    print(
                        f"Room: {room_name}, Wall: {wall.Id}, Points: {points_normals}"
                    )
                    for pt, normal in points_normals:
                        if not room.IsPointInRoom(pt):
                            continue
                        pt_with_height = DB.XYZ(pt.X, pt.Y, height)
                        level = wall.LevelId if hasattr(wall, 'LevelId') else room.LevelId
                        level_obj = doc.GetElement(level)
                        try:
                            # Создаём FamilyInstance
                            inst = doc.Create.NewFamilyInstance(pt_with_height, socket_symbol, wall, level_obj, DB.Structure.StructuralType.NonStructural)
                            # Вычисляем угол между нормалью и осью X
                            from math import atan2, pi
                            angle = atan2(normal.Y, normal.X) + pi/2  # дополнительный поворот на 90 градусов
                            # Если это нижняя стена, добавляем 180 градусов
                            if wall == bottom_wall:
                                angle += pi
                                print(
                                    f"[!] Дополнительный поворот на 180° для нижней стены {wall.Id}"
                                )
                            # Поворачиваем FamilyInstance вокруг Z
                            loc = inst.Location
                            if hasattr(loc, 'Rotate'):
                                axis = DB.Line.CreateUnbound(pt_with_height, DB.XYZ(0,0,1))
                                loc.Rotate(axis, angle)
                                print(
                                    f"Повернули розетку на {angle:.2f} рад (стена {wall.Id})"
                                )
                            else:
                                print(f"[!] Невозможно повернуть розетку: Location не поддерживает Rotate")
                            success_count += 1
                        except Exception as e:
                            print(
                                f"[!] Не удалось разместить розетку в точке ({pt_with_height.X:.2f}, {pt_with_height.Y:.2f}, {pt_with_height.Z:.2f}): {e}"
                            )
                            fail_count += 1
                except Exception as e:
                    print(f"[!] Ошибка при генерации/размещении для стены {wall.Id}: {e}")
    print(f"Успешно размещено розеток: {success_count}")
    if fail_count > 0:
        print(f"Не удалось разместить: {fail_count} розеток (см. сообщения выше)")
    return success_count, fail_count

if __name__ == "__main__":
    doc = revit.doc
    selected_rooms = get_selected_rooms()
    if not selected_rooms:
        print("[!] Выделите хотя бы одно помещение.")
    else:
        socket_types = get_socket_types(doc)
        if not socket_types:
            forms.alert("В проекте нет ни одного типа семейства розеток!", exitscript=True)
        socket_names = ["{} : {}".format(s.FamilyName, s.Name) for s in socket_types]
        selected_name = ui.select_socket_type(socket_names)
        if not selected_name:
            forms.alert("Тип розетки не выбран.", exitscript=True)
        selected_index = socket_names.index(selected_name)
        selected_symbol = socket_types[selected_index]
        # Активируем тип, если не активен
        if not selected_symbol.IsActive:
            with revit.Transaction("Активировать тип розетки"):
                selected_symbol.Activate()
        success_count, fail_count = place_sockets(selected_rooms, selected_symbol)
        msg = f"Розетки размещены! Успешно: {success_count}"
        if fail_count > 0:
            msg += f"\nНе удалось разместить: {fail_count} (см. консоль)"
        forms.alert(msg)
