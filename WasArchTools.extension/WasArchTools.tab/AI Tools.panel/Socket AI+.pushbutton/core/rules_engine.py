#! python3
# -*- coding: utf-8 -*-
"""
Модуль для парсинга нормативов и получения правил для различных типов помещений.
"""
import os
import json

class RuleEngine:
    def __init__(self, rules_path=None):
        if rules_path is None:
            # Абсолютный путь к assets/rules.json относительно этого файла
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_path = os.path.join(base_dir, "assets", "rules.json")
        with open(rules_path, encoding='utf-8') as f:
            self.rules = json.load(f)
    
    def get_room_rules(self, room_type):
        return self.rules.get(room_type, self.rules["default"]) 