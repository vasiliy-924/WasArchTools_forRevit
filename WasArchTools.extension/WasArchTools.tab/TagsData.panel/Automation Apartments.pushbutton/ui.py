# -*- coding: utf-8 -*-
"""UI components for Automation Apartments script"""

from pyrevit import forms
from System.Windows.Forms import (
    Form, Label, TextBox, Button,
    DialogResult, FormBorderStyle, FormStartPosition
)
from System.Drawing import Point, Size
import config


class CoefficientsForm(Form):
    """Form for entering area coefficients"""
    
    def __init__(self):
        super(CoefficientsForm, self).__init__()
        self.init_components()
        
        # Set default values
        self.balcony_box.Text = str(config.DEFAULT_COEFFICIENTS["balcony"])
        self.loggia_box.Text = str(config.DEFAULT_COEFFICIENTS["loggia"])
    
    def init_components(self):
        """Initialize form components"""
        self.Text = "Коэффициенты площадей"
        self.Size = Size(420, 250)
        self.FormBorderStyle = FormBorderStyle.FixedDialog
        self.StartPosition = FormStartPosition.CenterScreen
        
        # Balcony coefficient
        balcony_label = Label()
        balcony_label.Text = "Коэффициент для балконов:"
        balcony_label.Location = Point(10, 20)
        balcony_label.Size = Size(300, 20)
        self.Controls.Add(balcony_label)
        
        self.balcony_box = TextBox()
        self.balcony_box.Location = Point(310, 20)
        self.balcony_box.Size = Size(60, 20)
        self.Controls.Add(self.balcony_box)
        
        # Loggia coefficient
        loggia_label = Label()
        loggia_label.Text = "Коэффициент для лоджий:"
        loggia_label.Location = Point(10, 50)
        loggia_label.Size = Size(300, 20)
        self.Controls.Add(loggia_label)
        
        self.loggia_box = TextBox()
        self.loggia_box.Location = Point(310, 50)
        self.loggia_box.Size = Size(60, 20)
        self.Controls.Add(self.loggia_box)
        
        # OK button
        ok_button = Button()
        ok_button.Text = "OK"
        ok_button.DialogResult = DialogResult.OK
        ok_button.Location = Point(120, 120)
        ok_button.Size = Size(75, 23)
        self.Controls.Add(ok_button)
        
        # Cancel button
        cancel_button = Button()
        cancel_button.Text = "Отмена"
        cancel_button.DialogResult = DialogResult.Cancel
        cancel_button.Location = Point(200, 120)
        cancel_button.Size = Size(75, 23)
        self.Controls.Add(cancel_button)
    
    def get_coefficients(self):
        """Get entered coefficients"""
        try:
            return {
                "balcony": float(self.balcony_box.Text),
                "loggia": float(self.loggia_box.Text)
            }
        except ValueError:
            return None


def select_levels(doc):
    """Show level selection dialog"""
    all_levels = forms.select_levels(
        title="Выберите этажи",
        multiple=True
    )
    return all_levels


def show_coefficients_dialog():
    """Show coefficients input dialog"""
    form = CoefficientsForm()
    if form.ShowDialog() == DialogResult.OK:
        return form.get_coefficients()
    return None


def show_progress(title, max_value):
    """Show progress bar"""
    return forms.ProgressBar(
        title=title,
        cancellable=True,
        step=1,
        max_value=max_value
    )


def show_results(processed, failed, filepath=None):
    """Show results dialog"""
    msg = "Обработано помещений: {0}\nОшибок: {1}".format(processed, failed)
    if filepath:
        msg += "\n\nФайл сохранен:\n{0}".format(filepath)
    forms.alert(
        msg=msg,
        title="Результаты расчета"
    ) 