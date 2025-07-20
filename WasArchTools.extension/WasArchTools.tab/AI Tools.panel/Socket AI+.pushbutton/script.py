#! python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматической расстановки розеток в выбранных помещениях.
Использует правила из assets/rules.json.
"""
from pyrevit import revit, DB
from core.geometry import generate_wall_points
from core.rules_engine import RuleEngine

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

def place_sockets(selected_rooms):
    """
    Расставляет розетки в выбранных помещениях по правилам из rules.json.
    :param selected_rooms: список объектов Room
    """
    engine = RuleEngine()
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
        walls = get_room_walls(room)
        if not walls:
            continue
        for wall in walls:
            try:
                points = generate_wall_points(wall, rules["step"])
                print(f"Room: {room_name}, Wall: {wall.Id}, Points: {points}")
            except Exception as e:
                print(f"[!] Ошибка при генерации точек для стены {wall.Id}: {e}")

if __name__ == "__main__":
    selected_rooms = get_selected_rooms()
    if not selected_rooms:
        print("[!] Выделите хотя бы одно помещение.")
    else:
        place_sockets(selected_rooms)
