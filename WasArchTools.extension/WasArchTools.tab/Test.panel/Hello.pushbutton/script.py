"""Hello World скрипт для проверки работы PyRevit."""

from pyrevit import forms
from pyrevit import script

# Получаем логгер
logger = script.get_logger()
logger.info("Hello World скрипт запущен")

try:
    # Показываем диалоговое окно
    forms.alert(
        msg='Hello World из WasArchTools!',
        title='Тестовый скрипт',
        sub_msg='Если вы видите это сообщение, значит PyRevit работает корректно'
    )
    logger.info("Диалоговое окно показано успешно")
except Exception as e:
    logger.error("Произошла ошибка: %s", str(e))
    forms.alert(
        msg='Произошла ошибка при выполнении скрипта',
        title='Ошибка',
        sub_msg=str(e)
    ) 