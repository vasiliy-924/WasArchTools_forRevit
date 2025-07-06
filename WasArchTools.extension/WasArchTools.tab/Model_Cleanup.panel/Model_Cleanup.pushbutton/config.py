# -*- coding: utf-8 -*-
"""Конфигурация для скрипта Model Cleanup"""
from collections import namedtuple

# Структура для хранения информации о категории очистки
CleanupCategory = namedtuple('CleanupCategory', ['name', 'description', 'enabled', 'api_category'])

# Категории очистки
CLEANUP_CATEGORIES = {
    'annotations': CleanupCategory(
        name='Аннотации',
        description='Удаление пустых аннотаций',
        enabled=True,
        api_category='OST_TextNotes'
    ),
    'line_styles': CleanupCategory(
        name='Типы линий',
        description='Удаление неиспользуемых типов линий',
        enabled=True,
        api_category='GraphicsStyle'
    ),
    'view_filters': CleanupCategory(
        name='Фильтры видов',
        description='Удаление неиспользуемых фильтров',
        enabled=True,
        api_category='ParameterFilterElement'
    )
}

# Настройки UI
UI_SETTINGS = {
    'window': {
        'title': 'Model Cleanup',
        'width': 400,
        'height': 300,
        'icon': 'icon.png'
    },
    'validation': {
        'min_categories': 1,  # Минимальное количество выбранных категорий
        'warning_message': 'Выберите хотя бы одну категорию для очистки'
    }
}

# Настройки логирования
LOG_SETTINGS = {
    'file_output': True,  # Записывать ли лог в файл
    'console_output': True,  # Показывать ли лог в консоли
    'level': 'DEBUG'  # Уровень логирования (DEBUG, INFO, WARNING, ERROR)
}

# Структуры для хранения результатов
class CleanupResult:
    """Класс для хранения результатов очистки"""
    def __init__(self, category):
        self.category = category
        self.deleted_count = 0
        self.failed_count = 0
        self.error_messages = []
        self.deleted_elements = []  # Список удаленных элементов
        
    def add_deleted(self, element_id, element_name=None):
        """Добавить информацию об удаленном элементе"""
        self.deleted_count += 1
        self.deleted_elements.append({
            'id': element_id,
            'name': element_name or str(element_id)
        })
    
    def add_error(self, message):
        """Добавить сообщение об ошибке"""
        self.failed_count += 1
        self.error_messages.append(message)
    
    @property
    def total_processed(self):
        """Общее количество обработанных элементов"""
        return self.deleted_count + self.failed_count 