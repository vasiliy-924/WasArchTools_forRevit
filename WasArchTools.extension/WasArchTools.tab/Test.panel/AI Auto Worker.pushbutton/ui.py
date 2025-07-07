# -*- coding: utf-8 -*-
import os
import clr
clr.AddReference('PresentationFramework')
clr.AddReference('WindowsBase')
import System
from System.Windows import Window
from System.Windows.Markup import XamlReader
from System.IO import FileStream, FileMode
from System.Windows.Threading import DispatcherTimer

STATUSES = [
    u"Копаем землю под моделью… 🌏",
    u"Укладываем фундамент-матрицу… 🛖",
    u"Конструируем силовое поле… 🧙‍♂️",
    u"Проверяем уровни гравитации… ✈️",
    u"Делаем перерыв на печеньки… 🍪",
    u"Загружаем новую версию кофеина… ☕️",
    u"Оптимизируем внутренние чайники… ☕️",
    u"Считаем молекулы бетона… 👷‍♂️ 🦺",
    u"Соединяем ключевые фреймы… 📶",
    u"ЗАСКАМИЛИ МАМОНТА 🦣 😂",
]
FINAL_STATUS = u"Иди работай, Солнышко 🌞"

class HelloWindow(Window):
    def __init__(self):
        xaml_path = os.path.join(os.path.dirname(__file__), 'ui.xaml')
        fs = FileStream(xaml_path, FileMode.Open)
        window = XamlReader.Load(fs)
        fs.Close()
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
        self.StatusText = window.FindName('StatusText')
        self.ProgressBar = window.FindName('ProgressBar')
        # Смена статусов и прогресс-бара
        self._status_index = 0
        self.StatusText.Text = STATUSES[0]
        self.ProgressBar.Minimum = 0
        self.ProgressBar.Maximum = len(STATUSES)
        self.ProgressBar.Value = 1
        self._timer = DispatcherTimer()
        self._timer.Interval = System.TimeSpan.FromSeconds(2.5)
        self._timer.Tick += self._on_timer_tick
        self._timer.Start()

    def _on_timer_tick(self, sender, args):
        self._status_index += 1
        if self._status_index < len(STATUSES):
            self.StatusText.Text = STATUSES[self._status_index]
            self.ProgressBar.Value = self._status_index + 1
        else:
            self.StatusText.Text = FINAL_STATUS
            self.ProgressBar.Value = self.ProgressBar.Maximum
            self._timer.Stop()

def show_window():
    win = HelloWindow()
    win.ShowDialog() 