# -*- coding: utf-8 -*-
"""Configuration for Automation Apartments script"""

# Parameter names in Revit
PARAMETERS = {
    "room_type": "Тип помещения",  # Parameter for room type
    "area_accounted": "ПлощадьСКоэф",  # Parameter for area with coefficient
    "coefficient": "Коэффициент",  # Parameter for coefficient value
}

# Room types that should be treated as balconies/loggias
ROOM_TYPES = {
    "balcony": "Балкон",
    "loggia": "Лоджия",
}

# Default coefficients
DEFAULT_COEFFICIENTS = {
    "room": 1.0,  # Regular rooms
    "balcony": 0.3,  # Balconies
    "loggia": 0.5,  # Loggias
}

# CSV export settings
CSV_SETTINGS = {
    "delimiter": ";",  # CSV delimiter
}

# Parameter group for shared parameters
PARAM_GROUP = "Площади" 