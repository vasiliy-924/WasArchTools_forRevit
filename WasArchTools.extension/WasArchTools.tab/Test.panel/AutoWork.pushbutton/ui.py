# -*- coding: utf-8 -*-
import os
import clr
clr.AddReference('PresentationFramework')
from System.Windows import Window
from System.Windows.Markup import XamlReader
from System.IO import FileStream, FileMode

class HelloWindow(Window):
    def __init__(self):
        xaml_path = os.path.join(os.path.dirname(__file__), 'ui.xaml')
        fs = FileStream(xaml_path, FileMode.Open)
        window = XamlReader.Load(fs)
        fs.Close()
        # Копируем все свойства из window в self
        for attr in dir(window):
            if not attr.startswith('__') and not hasattr(self, attr):
                try:
                    setattr(self, attr, getattr(window, attr))
                except:
                    pass
        self.Content = window.Content
        self.Title = window.Title
        self.Width = window.Width
        self.Height = window.Height

def show_window():
    win = HelloWindow()
    win.ShowDialog() 