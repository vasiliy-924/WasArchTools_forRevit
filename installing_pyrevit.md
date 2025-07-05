## Версия pyRevit, которая запустилась
```
**pyRevit_5.0.1.25051_signed.exe**
```

## Процедура очищения .addin-файлов
```
Уберите все .addin-файлы и плагин-папки из:

%APPDATA%\Autodesk\Revit\Addins\<год>
%APPDATA%\Autodesk\ApplicationPlugins
%PROGRAMDATA%\Autodesk\Revit\Addins\<год>
%PROGRAMDATA%\Autodesk\ApplicationPlugins
```

## Процедура связи pyRevit с Revit
```cmd
  - pyrevit env

  - pyrevit attach master 2712 --installed

  - pyrevit attached


Там должна появиться строка:
master | Product: "Autodesk Revit 2024" | Engine: 2712 | Path: ...
```
