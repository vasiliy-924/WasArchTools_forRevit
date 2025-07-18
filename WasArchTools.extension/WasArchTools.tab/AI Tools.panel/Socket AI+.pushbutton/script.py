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
    for el in selection:
        print("Тип:", type(el), "Категория:", getattr(el.Category, 'Name', None))
    rooms = []
    for el in selection:
        if isinstance(el, DB.SpatialElement) and el.Category and el.Category.Name == "Помещения":
            rooms.append(el)
    return rooms

def get_room_walls(room):
    doc = room.Document
    boundaries = room.GetBoundarySegments(DB.SpatialElementBoundaryOptions())
    walls = []
    if boundaries:
        for segment in boundaries[0]:
            wall = doc.GetElement(segment.ElementId)
            if isinstance(wall, DB.Wall):
                walls.append(wall)
    return walls

def place_sockets(selected_rooms):
    """
    Расставляет розетки в выбранных помещениях по правилам из rules.json.
    :param selected_rooms: список объектов Room
    """
    engine = RuleEngine()
    for room in selected_rooms:
        rules = engine.get_room_rules(room.Name)
        walls = get_room_walls(room)
        for wall in walls:
            points = generate_wall_points(wall, rules["step"])
            # Здесь добавить логику фильтрации по min_distance и размещения розеток
            print(f"Room: {room.Name}, Wall: {wall.Id}, Points: {points}")

if __name__ == "__main__":
    selected_rooms = get_selected_rooms()
    if not selected_rooms:
        print("Выделите хотя бы одно помещение.")
    else:
        place_sockets(selected_rooms)
