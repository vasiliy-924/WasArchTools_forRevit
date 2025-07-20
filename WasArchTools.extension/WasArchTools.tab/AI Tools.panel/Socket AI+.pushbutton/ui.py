# coding: utf-8
import clr
from pyrevit import script, forms

clr.AddReference('PresentationFramework')
clr.AddReference('WindowsBase')


class SocketTypeSelector(forms.WPFWindow):
    def __init__(self, xaml_path, socket_names):
        forms.WPFWindow.__init__(self, xaml_path)
        self.SocketTypeList.ItemsSource = socket_names
        self.selected = None

    def on_ok(self, sender, args):
        sel = self.SocketTypeList.SelectedItem
        if sel:
            self.selected = sel
            self.Close()
        else:
            forms.alert("Выберите тип розетки!")

    def on_cancel(self, sender, args):
        self.selected = None
        self.Close()


def select_socket_type(socket_names):
    xaml_path = script.get_bundle_file('ui.xaml')
    win = SocketTypeSelector(xaml_path, socket_names)
    win.show_dialog()
    return win.selected