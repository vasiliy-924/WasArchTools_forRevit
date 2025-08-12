1) Active Engine: писать для IronPython3 (342): IronPython 3 Engine
Active CPython Engine: CPython (3123): CPython Engine (включается шебангом `#! python3`)

2) Правила для скриптов pyRevit (IronPython 3) — кратко

- Импорт Revit API только внутри функций:
  - `clr = importlib.import_module('clr')`
  - `clr.AddReference('RevitAPI'); clr.AddReference('RevitAPIUI')`
  - Далее импорт `DB`/`UI` (через `importlib.import_module` или через `exec` при необходимости)

- Контекст Revit:
  - Сначала пробуй `pyrevit.revit` (`uidoc`, `doc`), иначе `__revit__.ActiveUIDocument`
  - Не рассчитывай, что `__revit__` всегда есть (тихо выходи вне Revit)

- Работа с выделением/областью:
  - Поддерживай выбор `Viewport`, `View`, `Sheet`
  - Для `View` находи соответствующие `Viewport`(ы); для `Sheet` — все `Viewport` листа
  - Если ничего не выделено — покажи короткое сообщение (`UI.TaskDialog.Show`)

- Транзакции:
  - Изменения только внутри `DB.Transaction(doc, 'Name')`; `Start()` → работа → `Commit()` в `finally`
  - По возможности одна транзакция на всю операцию

- Параметры:
  - `param = elem.get_Parameter(BuiltInParameter.XXX)`; проверяй `param` и `not param.IsReadOnly`
  - `param.Set(...)` оборачивай точечно в `try/except` (конфликты, дубликаты)

- Импорты и совместимость:
  - Не импортируй `Autodesk.Revit.*` на уровне модуля (делай это после `AddReference` внутри функций)
  - Не используй `from __future__ import annotations`, типовые аннотации, `dataclasses`, f-строки; предпочитай `str.format(...)`
  - Длина строки ≤ 79 символов

- Ошибки и UX:
  - Не ставь глобальный `except Exception`; только вокруг рискованных вызовов API
  - После выполнения показывай краткую сводку (обновлено/пропущено/ошибок)

- Производительность:
  - Используй `FilteredElementCollector` с `.OfClass(...)` и ограничением области (по листу), избегай полного обхода

- Зависимости:
  - Только стандартная библиотека, Revit API, pyRevit (без внешних пакетов)

- Структура кода:
  - Маленькие функции с одной ответственностью; точка входа `if __name__ == '__main__': main()`
  - Никаких действий на уровне модуля (импортов API/транзакций/побочных эффектов)