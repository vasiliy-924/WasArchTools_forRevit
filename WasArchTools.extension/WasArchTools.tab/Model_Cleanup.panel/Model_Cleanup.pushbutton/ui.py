# -*- coding: utf-8 -*-
"""UI для Model Cleanup"""
from pyrevit import forms
from System.Windows import Window
import wpf
#from System.Windows.Controls import CheckBox  # not needed
#import EventHandler  # not needed
import os

from config import CLEANUP_CATEGORIES, UI_SETTINGS


class ModelCleanupWindow(Window):
    """Главное окно скрипта Model Cleanup"""
    
    def __init__(self):
        """Инициализация окна"""
        xaml_path = os.path.join(os.path.dirname(__file__), 'ui.xaml')
        wpf.LoadComponent(self, xaml_path)
        
        # Настройка окна
        self.Title = UI_SETTINGS['window']['title']
        
        # Привязка обработчиков событий (без EventHandler)
        self.CancelButton.Click += self.on_cancel_click
        self.CleanupButton.Click += self.on_cleanup_click
        
        # Инициализация выбранных категорий
        self.selected_categories = []
        
        # Привязка чекбоксов к категориям
        self._bind_checkboxes()
    
    def _bind_checkboxes(self):
        """Привязка чекбоксов к категориям"""
        self.checkbox_mapping = {
            'annotations': self.AnnotationsCheck,
            'line_styles': self.LineStylesCheck,
            'view_filters': self.ViewFiltersCheck
        }
        
        # Установка начальных значений
        for key, checkbox in self.checkbox_mapping.items():
            checkbox.IsChecked = CLEANUP_CATEGORIES[key].enabled
    
    def get_selected_categories(self):
        """Получить список выбранных категорий"""
        selected = []
        for key, checkbox in self.checkbox_mapping.items():
            if checkbox.IsChecked:
                selected.append(key)
        return selected
    
    def validate_selection(self):
        """Проверка выбора категорий"""
        selected = self.get_selected_categories()
        if len(selected) < UI_SETTINGS['validation']['min_categories']:
            forms.alert(
                msg=UI_SETTINGS['validation']['warning_message'],
                title=self.Title
            )
            return False
        return True
    
    def show_progress(self, visible=True):
        """Показать/скрыть индикатор прогресса"""
        self.ProgressBar.Visibility = (
            'Visible' if visible else 'Collapsed'
        )
        self.CleanupButton.IsEnabled = not visible
        self.CancelButton.IsEnabled = not visible
    
    def on_cancel_click(self, sender, args):
        """Обработчик нажатия кнопки Отмена"""
        self.DialogResult = False
        self.Close()
    
    def on_cleanup_click(self, sender, args):
        """Обработчик нажатия кнопки Очистить"""
        if self.validate_selection():
            self.selected_categories = self.get_selected_categories()
            self.DialogResult = True
            self.Close()
    
    def run_dialog(self):
        """Запуск диалога и возврат выбранных категорий"""
        dialog_result = self.ShowDialog()
        if dialog_result:
            return self.selected_categories
        return None

class PreviewDeleteWindow(Window):
    """Окно предварительного просмотра удаления элементов"""
    def __init__(self, candidates_dict):
        xaml_path = os.path.join(os.path.dirname(__file__), 'preview_delete.xaml')
        wpf.LoadComponent(self, xaml_path)
        self.Title = u'Подтверждение удаления'
        self.candidates_dict = candidates_dict
        self.selected = {k: set() for k in candidates_dict.keys()}
        self._populate_lists()
        self.OkButton.Click += self.on_ok
        self.CancelButton.Click += self.on_cancel
    def _populate_lists(self):
        # Аннотации
        self.AnnotationsList.Items.Clear()
        for el_id in self.candidates_dict.get('annotations', []):
            # el_id теперь это ElementId, а не элемент
            name = u"ID: {0} | [пустая аннотация]".format(el_id)
            self.AnnotationsList.Items.Add(name)
        self.AnnotationsList.SelectAll()
        # Типы линий
        self.LineStylesList.Items.Clear()
        for cand in self.candidates_dict.get('line_styles', []):
            if hasattr(cand, 'used_count'):
                if cand.used_count == 0:
                    name = u"ID: {0} | {1} [не используется]".format(cand.Id, cand.Name)
                    self.LineStylesList.Items.Add(name)
                else:
                    name = u"ID: {0} | {1} [используется в {2} элементах]".format(cand.Id, cand.Name, cand.used_count)
                    self.LineStylesList.Items.Add(name)
            else:
                self.LineStylesList.Items.Add(unicode(cand))
        # Выделяем только неиспользуемые
        for idx, cand in enumerate(self.candidates_dict.get('line_styles', [])):
            if hasattr(cand, 'used_count') and cand.used_count == 0:
                self.LineStylesList.SelectedItems.Add(self.LineStylesList.Items[idx])
        # Фильтры
        self.ViewFiltersList.Items.Clear()
        for cand in self.candidates_dict.get('view_filters', []):
            if hasattr(cand, 'used_in_views'):
                if not cand.used_in_views:
                    name = u"ID: {0} | {1} [не применяется]".format(cand.Id, cand.Name)
                    self.ViewFiltersList.Items.Add(name)
                else:
                    name = u"ID: {0} | {1} [используется в: {2}]".format(cand.Id, cand.Name, u', '.join(cand.used_in_views))
                    self.ViewFiltersList.Items.Add(name)
            else:
                self.ViewFiltersList.Items.Add(unicode(cand))
        # Выделяем только неиспользуемые
        for idx, cand in enumerate(self.candidates_dict.get('view_filters', [])):
            if hasattr(cand, 'used_in_views') and not cand.used_in_views:
                self.ViewFiltersList.SelectedItems.Add(self.ViewFiltersList.Items[idx])
    def on_ok(self, sender, args):
        self.selected = {}
        # Аннотации
        ann_selected = set()
        for idx in range(self.AnnotationsList.Items.Count):
            if self.AnnotationsList.SelectedItems.Contains(self.AnnotationsList.Items[idx]):
                el_id = self.candidates_dict.get('annotations', [])[idx]
                ann_selected.add(el_id)  # el_id уже является ElementId
        self.selected['annotations'] = ann_selected
        # Типы линий (только неиспользуемые)
        ls_selected = set()
        for idx in range(self.LineStylesList.Items.Count):
            cand = self.candidates_dict.get('line_styles', [])[idx]
            if hasattr(cand, 'used_count') and cand.used_count == 0:
                if self.LineStylesList.SelectedItems.Contains(self.LineStylesList.Items[idx]):
                    ls_selected.add(cand.Id)
        self.selected['line_styles'] = ls_selected
        # Фильтры (только неиспользуемые)
        vf_selected = set()
        for idx in range(self.ViewFiltersList.Items.Count):
            cand = self.candidates_dict.get('view_filters', [])[idx]
            if hasattr(cand, 'used_in_views') and not cand.used_in_views:
                if self.ViewFiltersList.SelectedItems.Contains(self.ViewFiltersList.Items[idx]):
                    vf_selected.add(cand.Id)
        self.selected['view_filters'] = vf_selected
        self.DialogResult = True
        self.Close()
    def on_cancel(self, sender, args):
        self.DialogResult = False
        self.Close()
    def get_selected(self):
        return self.selected 