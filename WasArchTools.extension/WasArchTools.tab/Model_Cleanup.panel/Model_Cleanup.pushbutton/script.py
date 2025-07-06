#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Model Cleanup
Cleanup model from unused elements (annotations, line styles, view filters, etc.)
"""
from pyrevit import revit, DB, script
from collections import OrderedDict
import config
import ui
import os
import datetime
import codecs
import re

logger = script.get_logger()
output = script.get_output()
doc = revit.doc

LOG_FILE = os.path.join(os.path.dirname(__file__), 'log.txt')

def log_to_file(message):
    if config.LOG_SETTINGS.get('file_output', False):
        with codecs.open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(u"[{0}] {1}\n".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message))

def cleanup_annotations(result):
    """Удаление пустых аннотаций"""
    logger.info(u"[Аннотации] Поиск пустых аннотаций...")
    log_to_file(u"[Аннотации] Поиск пустых аннотаций...")
    try:
        with revit.Transaction(u"Удаление пустых аннотаций"):
            notes = DB.FilteredElementCollector(doc)\
                .OfCategory(DB.BuiltInCategory.OST_TextNotes)\
                .WhereElementIsNotElementType()\
                .ToElements()
            for note in notes:
                if not note.Text.strip():
                    doc.Delete(note.Id)
                    result.add_deleted(note.Id)
                    log_to_file(u"Удалена пустая аннотация: {0}".format(note.Id))
        logger.info(u"[Аннотации] Удалено: {0}".format(result.deleted_count))
        log_to_file(u"[Аннотации] Удалено: {0}".format(result.deleted_count))
    except Exception:
        logger.error(u"[Аннотации] Ошибка при удалении аннотаций")
        log_to_file(u"[Аннотации] Ошибка при удалении аннотаций")
        result.add_error(u"Ошибка при удалении аннотаций")
    return result

def cleanup_line_styles(result):
    """Удаление неиспользуемых типов линий"""
    logger.info(u"[Типы линий] Поиск неиспользуемых типов...")
    log_to_file(u"[Типы линий] Поиск неиспользуемых типов...")
    try:
        with revit.Transaction(u"Удаление неиспользуемых типов линий"):
            styles = DB.FilteredElementCollector(doc)\
                .OfClass(DB.GraphicsStyle)\
                .ToElements()
            for style in styles:
                cat = style.GraphicsStyleCategory
                if cat and cat.CategoryType == DB.CategoryType.Annotation:
                    try:
                        doc.Delete(style.Id)
                        result.add_deleted(style.Id, style.Name)
                        log_to_file(u"Удалён тип линии: {0}".format(style.Name))
                    except Exception:
                        result.add_error(u"Ошибка при удалении типа линии: {0}".format(style.Name))
                        log_to_file(u"Ошибка при удалении типа линии: {0}".format(style.Name))
        logger.info(u"[Типы линий] Удалено: {0}".format(result.deleted_count))
        log_to_file(u"[Типы линий] Удалено: {0}".format(result.deleted_count))
    except Exception:
        logger.error(u"[Типы линий] Ошибка при удалении типов линий")
        log_to_file(u"[Типы линий] Ошибка при удалении типов линий")
        result.add_error(u"Ошибка при удалении типов линий")
    return result

def cleanup_view_filters(result):
    """Удаление неиспользуемых фильтров видов"""
    logger.info(u"[Фильтры] Поиск неиспользуемых фильтров...")
    log_to_file(u"[Фильтры] Поиск неиспользуемых фильтров...")
    try:
        with revit.Transaction(u"Удаление неиспользуемых фильтров видов"):
            filters = DB.FilteredElementCollector(doc)\
                .OfClass(DB.ParameterFilterElement)\
                .ToElements()
            all_views = DB.FilteredElementCollector(doc)\
                .OfClass(DB.View)\
                .ToElements()
            for filter_elem in filters:
                is_used = False
                for view in all_views:
                    try:
                        if view.IsFilterApplied(filter_elem.Id):
                            is_used = True
                            break
                    except Exception:
                        continue
                if not is_used:
                    try:
                        doc.Delete(filter_elem.Id)
                        result.add_deleted(filter_elem.Id, filter_elem.Name)
                        log_to_file(u"Удалён фильтр: {0}".format(filter_elem.Name))
                    except Exception:
                        result.add_error(u"Ошибка при удалении фильтра: {0}".format(filter_elem.Name))
                        log_to_file(u"Ошибка при удалении фильтра: {0}".format(filter_elem.Name))
        logger.info(u"[Фильтры] Удалено: {0}".format(result.deleted_count))
        log_to_file(u"[Фильтры] Удалено: {0}".format(result.deleted_count))
    except Exception:
        logger.error(u"[Фильтры] Ошибка при удалении фильтров")
        log_to_file(u"[Фильтры] Ошибка при удалении фильтров")
        result.add_error(u"Ошибка при удалении фильтров")
    return result

def show_results(results):
    output.print_md(u"# Model Cleanup — Результаты\n")
    total = 0
    for key, result in results.items():
        output.print_md(u"## {0}".format(config.CLEANUP_CATEGORIES[key].name))
        output.print_md(u"- Удалено: {0}".format(result.deleted_count))
        if result.failed_count:
            output.print_md(u"- Ошибок: {0}".format(result.failed_count))
            for msg in result.error_messages:
                output.print_md(u"    - {0}".format(msg))
        total += result.deleted_count
    output.print_md(u"\n**Всего удалено: {0}**".format(total))
    log_to_file(u"Итог: всего удалено {0}".format(total))

    # Итоговый TaskDialog
    from pyrevit import forms
    msg = u"Очистка завершена!\n\n"
    for key, result in results.items():
        msg += u"{0}: {1}\n".format(config.CLEANUP_CATEGORIES[key].name, result.deleted_count)
    msg += u"\nВсего: {0}".format(total)
    forms.alert(msg=msg, title="Model Cleanup", sub_msg="Подробности в окне результатов pyRevit")
    log_to_file(u"=== Model Cleanup завершён ===\n")

# --- DRY-RUN: поиск кандидатов на удаление ---
def find_empty_annotations():
    notes = DB.FilteredElementCollector(doc)\
        .OfCategory(DB.BuiltInCategory.OST_TextNotes)\
        .WhereElementIsNotElementType()\
        .ToElements()
    empty_notes = []
    for n in notes:
        try:
            # Проверяем, что элемент валиден
            if n and n.IsValidObject:
                text = getattr(n, 'Text', u'')
                # Удаляем все пробельные символы (включая невидимые)
                if re.sub(u'\s+', u'', text) == u'':
                    # Сохраняем только ID элемента, а не сам объект
                    empty_notes.append(n.Id)
        except Exception as e:
            log_to_file(u"Ошибка при проверке аннотации {0}: {1}".format(
                getattr(n, 'Id', 'Unknown'), str(e)))
    return empty_notes

# Новый тип: LineStyleCandidate
class LineStyleCandidate(object):
    def __init__(self, style, used_count):
        self.style = style
        self.used_count = used_count
        self.Id = style.Id
        self.Name = getattr(style, 'Name', u'')

# Новый тип: ViewFilterCandidate
class ViewFilterCandidate(object):
    def __init__(self, filter_elem, used_in_views):
        self.filter_elem = filter_elem
        self.used_in_views = used_in_views  # список имён видов
        self.Id = filter_elem.Id
        self.Name = getattr(filter_elem, 'Name', u'')

# Поиск использования стилей линий
LINE_STYLE_CLASSES = [DB.DetailLine, DB.FilledRegion, DB.AnnotationSymbol]
def find_unused_line_styles():
    styles = DB.FilteredElementCollector(doc)\
        .OfClass(DB.GraphicsStyle)\
        .ToElements()
    candidates = []
    for style in styles:
        cat = style.GraphicsStyleCategory
        if not cat:
            continue
        if hasattr(cat, 'IsSystem') and cat.IsSystem:
            continue
        if cat.Name.startswith(u'<'):
            continue
        # Проверяем использование: ищем элементы, у которых LineStyle.Id == style.Id
        used_count = 0
        for cls in LINE_STYLE_CLASSES:
            try:
                elems = DB.FilteredElementCollector(doc).OfClass(cls).ToElements()
                for el in elems:
                    if hasattr(el, 'LineStyle') and el.LineStyle and el.LineStyle.Id == style.Id:
                        used_count += 1
            except Exception:
                continue
        candidates.append(LineStyleCandidate(style, used_count))
    return candidates

def find_unused_view_filters():
    filters = DB.FilteredElementCollector(doc)\
        .OfClass(DB.ParameterFilterElement)\
        .ToElements()
    all_views = DB.FilteredElementCollector(doc)\
        .OfClass(DB.View)\
        .ToElements()
    candidates = []
    for filter_elem in filters:
        used_in_views = []
        for view in all_views:
            try:
                if view.IsFilterApplied(filter_elem.Id):
                    used_in_views.append(view.Name)
            except Exception:
                continue
        candidates.append(ViewFilterCandidate(filter_elem, used_in_views))
    return candidates

# --- Удаление выбранных элементов ---
def delete_elements(elements, category_name):
    deleted = 0
    errors = 0
    # Для аннотаций — реальное удаление
    if category_name == 'annotations':
        for element_id in elements:
            try:
                # Проверяем, что ID валиден
                if element_id and element_id.IntegerValue != -1:
                    # Получаем элемент заново перед удалением
                    element = doc.GetElement(element_id)
                    if element and element.IsValidObject:
                        # Удаляем каждый элемент в отдельной транзакции
                        with revit.Transaction(u"Удаление аннотации {0}".format(element_id)):
                            doc.Delete(element_id)
                            deleted += 1
                            log_to_file(u"Удалён: {0} {1}".format(category_name, element_id))
                    else:
                        errors += 1
                        log_to_file(u"Элемент {0} {1} недействителен".format(category_name, element_id))
                else:
                    errors += 1
                    log_to_file(u"Элемент {0} {1} имеет недействительный ID".format(category_name, element_id))
            except Exception as e:
                errors += 1
                log_to_file(u"Ошибка при удалении {0} {1}: {2}".format(category_name, element_id, str(e)))
    # Для остальных категорий — заглушка
    else:
        for el in elements:
            log_to_file(u"[ЗАГЛУШКА] Был бы удалён: {0} {1}".format(category_name, el.Id))
            # Для реального удаления раскомментируйте следующий блок:
            # try:
            #     with revit.Transaction(u"Удаление: {0}".format(category_name)):
            #         doc.Delete(el.Id)
            #         deleted += 1
            #         log_to_file(u"Удалён: {0} {1}".format(category_name, el.Id))
            # except Exception:
            #     errors += 1
            #     log_to_file(u"Ошибка при удалении {0}: {1}".format(category_name, el.Id))
    return deleted, errors

def main():
    logger.info(u"=== Model Cleanup: запуск ===")
    log_to_file(u"=== Model Cleanup: запуск ===")
    win = ui.ModelCleanupWindow()
    selected = win.run_dialog()
    if not selected:
        logger.info(u"Model Cleanup: отменено пользователем")
        log_to_file(u"Model Cleanup: отменено пользователем")
        return
    # DRY-RUN: поиск кандидатов
    candidates = {}
    if 'annotations' in selected:
        candidates['annotations'] = find_empty_annotations()
    # Отключено для диагностики:
    # if 'line_styles' in selected:
    #     candidates['line_styles'] = find_unused_line_styles()
    # if 'view_filters' in selected:
    #     candidates['view_filters'] = find_unused_view_filters()
    # Окно предварительного просмотра
    preview = ui.PreviewDeleteWindow(candidates)
    if not preview.ShowDialog():
        log_to_file(u"Удаление отменено пользователем на этапе предпросмотра")
        return
    selected_to_delete = preview.get_selected()
    # Явное предупреждение пользователя о рисках
    from pyrevit import forms
    warning_msg = u"ВНИМАНИЕ!\n\nУдаление некоторых стилей линий и фильтров может привести к аварийному завершению Revit.\n\nРекомендуется использовать этот скрипт только на копии проекта!\n\nПродолжить удаление выбранных элементов?"
    if not forms.alert(warning_msg, title="Model Cleanup — ВАЖНО!", options=["Продолжить", "Отмена"]) == "Продолжить":
        log_to_file(u"Удаление отменено пользователем после предупреждения о рисках")
        return
    # Удаление
    results = OrderedDict()
    for key in selected:
        if key == 'annotations':
            # Для аннотаций работаем с ID
            elements = [el_id for el_id in candidates.get(key, []) 
                       if el_id in selected_to_delete.get(key, set())]
        else:
            # Для остальных категорий работаем с объектами
            elements = [el for el in candidates.get(key, []) 
                       if el.Id in selected_to_delete.get(key, set())]
        log_to_file(u"Начинаем удаление {0}: найдено {1} элементов".format(
            key, len(elements)))
        deleted, errors = delete_elements(elements, key)
        results[key] = (deleted, errors)
        log_to_file(u"Завершено удаление {0}: удалено {1}, ошибок {2}".format(
            key, deleted, errors))
    # Вывод результатов
    output.print_md(u"# Model Cleanup — Результаты\n")
    total = 0
    for key, (deleted, errors) in results.items():
        output.print_md(u"## {0}".format(config.CLEANUP_CATEGORIES[key].name))
        output.print_md(u"- Было бы удалено: {0}".format(deleted))
        if errors:
            output.print_md(u"- Ошибок: {0}".format(errors))
        total += deleted
    output.print_md(u"\n**Всего было бы удалено: {0}**".format(total))
    log_to_file(u"Итог: всего было бы удалено {0}".format(total))
    msg = u"Анализ завершён!\n\n"
    for key, (deleted, errors) in results.items():
        msg += u"{0}: {1}\n".format(config.CLEANUP_CATEGORIES[key].name, deleted)
    msg += u"\nВсего: {0}".format(total)
    forms.alert(msg=msg, title="Model Cleanup", sub_msg="Подробности в окне результатов pyRevit")
    log_to_file(u"=== Model Cleanup завершён ===\n")

if __name__ == '__main__':
    main() 