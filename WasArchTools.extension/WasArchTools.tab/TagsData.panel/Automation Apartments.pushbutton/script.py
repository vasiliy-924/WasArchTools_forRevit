# -*- coding: utf-8 -*-
"""Automation Apartments

Calculates apartment areas with coefficients for balconies and loggias.
Exports results to CSV and updates room parameters.
"""

import os
import csv
from datetime import datetime

from Autodesk.Revit.DB import (
    BuiltInParameter,
    FilteredElementCollector,
    Transaction,
    SpatialElement,
)
from Autodesk.Revit.DB.Architecture import Room
from pyrevit import script

import config
import ui

# Initialize logger
logger = script.get_logger()
output = script.get_output()

# Get current document
try:
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
except NameError:
    doc = None
    uidoc = None
    logger.error("This script must be run from within Revit")
    script.exit()


def get_all_rooms():
    """Get all rooms from current document"""
    collector = FilteredElementCollector(doc).OfClass(SpatialElement)
    return [elem for elem in collector if isinstance(elem, Room)]


def filter_rooms_by_level(rooms, level_ids):
    """Filter rooms by level ids"""
    if not level_ids:
        return rooms
    return [room for room in rooms if room.LevelId in level_ids]


def is_balcony(room):
    """Check if room is a balcony or loggia"""
    room_type = room.LookupParameter(config.PARAMETERS["room_type"])
    if not room_type:
        return False
    room_type_value = room_type.AsString()
    return room_type_value in [
        config.ROOM_TYPES["balcony"],
        config.ROOM_TYPES["loggia"]
    ]


def get_coefficient(room, coefficients=None):
    """Get area coefficient for room"""
    if not is_balcony(room):
        return config.DEFAULT_COEFFICIENTS["room"]
    
    room_type = room.LookupParameter(config.PARAMETERS["room_type"]).AsString()
    if coefficients:
        if room_type == config.ROOM_TYPES["balcony"]:
            return coefficients["balcony"]
        return coefficients["loggia"]
    else:
        if room_type == config.ROOM_TYPES["balcony"]:
            return config.DEFAULT_COEFFICIENTS["balcony"]
        return config.DEFAULT_COEFFICIENTS["loggia"]


def calculate_area(room, coefficients=None):
    """Calculate room area with coefficient"""
    base_area = room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble()
    coefficient = get_coefficient(room, coefficients)
    return base_area * coefficient


def format_area(area_value):
    """Format area value for display and export"""
    # Convert from square feet to square meters and round to 2 decimal places
    return round(area_value * 0.092903, 2)


def update_room_parameters(room, area, coefficient):
    """Update room parameters with calculated values"""
    with Transaction(doc, "Update Room Parameters") as t:
        t.Start()
        try:
            # Update accounted area
            area_param = room.LookupParameter(config.PARAMETERS["area_accounted"])
            if area_param:
                area_param.Set(area)
            
            # Update coefficient
            coeff_param = room.LookupParameter(config.PARAMETERS["coefficient"])
            if coeff_param:
                coeff_param.Set(coefficient)
            
            t.Commit()
            return True
        except Exception as ex:
            logger.error("Error updating parameters for room {0}: {1}".format(
                room.Id, str(ex)))
            t.RollBack()
            return False


def get_room_data(room, area, coefficient):
    """Get room data for export"""
    level = doc.GetElement(room.LevelId)
    room_type_param = room.LookupParameter(config.PARAMETERS["room_type"])
    room_type = (room_type_param.AsString() if room_type_param else "")
    
    return {
        "level": level.Name if level else "Unknown",
        "number": room.Number,
        "name": room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString(),
        "type": room_type,
        "base_area": format_area(
            room.get_Parameter(BuiltInParameter.ROOM_AREA).AsDouble()
        ),
        "coefficient": coefficient,
        "accounted_area": format_area(area)
    }


def export_to_csv(rooms_data, filepath=None):
    """Export results to CSV file"""
    if not filepath:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Get path to Results folder in root directory
        script_dir = os.path.dirname(__file__)
        extension_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        root_dir = os.path.dirname(extension_dir)
        results_dir = os.path.join(root_dir, "Results")
        
        # Create Results directory if it doesn't exist
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            
        filepath = os.path.join(
            results_dir,
            "room_areas_{0}.csv".format(timestamp)
        )
    
    try:
        with open(filepath, 'wb') as f:
            # Write UTF-8 BOM
            f.write('\xef\xbb\xbf'.encode('utf-8'))
            writer = csv.writer(f, delimiter=config.CSV_SETTINGS["delimiter"])
            # Write header
            header = [
                "Этаж", "Номер", "Имя", "Тип",
                "Площадь", "Коэффициент", "Площадь с коэф."
            ]
            writer.writerow([x.encode('utf-8') for x in header])
            # Write data
            for data in rooms_data:
                row = [
                    data["level"],
                    data["number"],
                    data["name"],
                    data["type"],
                    str(data["base_area"]),
                    str(data["coefficient"]),
                    str(data["accounted_area"])
                ]
                writer.writerow([x.encode('utf-8') for x in row])
        return filepath
    except Exception as ex:
        logger.error("Error exporting to CSV: {0}".format(str(ex)))
        return None


def main():
    """Main entry point for the script"""
    logger.info("Starting Automation Apartments script...")
    
    # Get levels
    selected_levels = ui.select_levels(doc)
    if not selected_levels:
        logger.warning("No levels selected. Exiting...")
        return
    
    # Get coefficients
    coefficients = ui.show_coefficients_dialog()
    if not coefficients:
        logger.warning("No coefficients entered. Using defaults...")
        coefficients = config.DEFAULT_COEFFICIENTS
    
    # Get rooms
    all_rooms = get_all_rooms()
    rooms = filter_rooms_by_level(all_rooms, [level.Id for level in selected_levels])
    
    if not rooms:
        logger.warning("No rooms found on selected levels")
        return
    
    # Process rooms
    progress = ui.show_progress("Processing rooms...", len(rooms))
    rooms_data = []
    processed = 0
    failed = 0
    
    for i, room in enumerate(rooms, 1):
        if progress.cancelled:
            break
        
        # Calculate area
        area = calculate_area(room, coefficients)
        coefficient = get_coefficient(room, coefficients)
        
        # Update parameters
        if update_room_parameters(room, area, coefficient):
            processed += 1
            rooms_data.append(get_room_data(room, area, coefficient))
        else:
            failed += 1
        
        progress.update_progress(i)
    
    # Export results
    if rooms_data:
        export_path = export_to_csv(rooms_data)
        if export_path:
            logger.info("Results exported successfully")
        else:
            logger.error("Failed to export results")
    
    # Show results
    result_path = export_path if 'export_path' in locals() else None
    ui.show_results(processed, failed, result_path)


if __name__ == '__main__':
    main() 