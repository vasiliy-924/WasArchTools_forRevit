# WasArchTools for Revit

WasArchTools — это набор скриптов и инструментов для повышения эффективности работы в Autodesk Revit. Данный проект предназначен для архитекторов и проектировщиков, желающих автоматизировать рутинные задачи и ускорить процесс моделирования.

## Структура проекта

```
WasArchTools_forRevit/
│
├── WasArchTools.extension/           # Основная директория расширения для pyRevit
│   ├── lib/                          # Вспомогательные библиотеки
│   └── WasArchTools.tab/             # Вкладка с панелями и кнопками
│       ├── Model_Cleanup.panel/      # Панель для очистки модели
│       │   └── Model_Cleanup.pushbutton/
│       │       ├── script.py         # Основной скрипт кнопки
│       │       ├── ui.py, ui.xaml    # Интерфейс пользователя
│       │       └── ...               # Прочие файлы
│       ├── TagsData.panel/           # Панель для работы с данными тегов
│       │   └── Automation Apartments.pushbutton/
│       │       ├── script.py
│       │       └── ...
│       └── AI Tools.panel/               # Тестовые и экспериментальные инструменты
│           ├── AI Auto Worker.pushbutton/
│           │   ├── script.py
│           │   └── ...
│           └── Socket AI+.pushbutton/
│               ├── script.py
│               └── ...
├── Readme.md                         # Описание проекта
├── To-Do.md, To-Do-Detail.txt        # Списки задач
└── installing_pyrevit.md             # Инструкция по установке pyRevit
```

## Установка

1. Установите [pyRevit](https://github.com/pyrevitlabs/pyRevit/releases).
2. Склонируйте данный репозиторий в директорию расширений pyRevit:
   ```
   git clone git@github.com:vasiliy-924/WasArchTools_forRevit.git
   ```
3. Перезапустите Revit и убедитесь, что вкладка WasArchTools появилась в интерфейсе.

Подробнее см. файл `installing_pyrevit.md`.

## Использование

- Откройте Revit.
- Перейдите на вкладку **WasArchTools**.
- Используйте доступные панели и кнопки для автоматизации задач:
  - **Model Cleanup** — инструменты для очистки и оптимизации модели.
  - **TagsData** — автоматизация работы с тегами и данными помещений.
  - **AI Tools** — экспериментальные функции (например, AI Auto Worker, Socket AI+).

## Рекомендации по иконкам

- Рекомендованный цвет для значков: `#34495E`
- Все иконки должны быть в формате PNG, размером 32x32 px.


## Авторство

**Василий Петров** - [GitHub https://github.com/vasiliy-924](https://github.com/vasiliy-924)