### Подробный пошаговый план разработки SocketAI для pyRevit в Cursor AI IDE

---

#### 🛠️ **Этап 0: Подготовка среды (1 день)**
1. **Настройка IDE**:
   - Установите Cursor AI IDE с поддержкой Python 3.8+
   - Настройте virtual environment:  
     ```bash
     python -m venv socketai_env
     source socketai_env/bin/activate  # Linux/Mac)
     .\socketai_env\Scripts\activate  # Windows
     ```
   - Установите зависимости:
     ```bash
     pip install pyrevit numpy shapely firebase-admin pyyaml tensorflow-cpu
     ```

2. **Структура проекта**:
   ```
   SocketAI/
   ├── .env                  # API keys
   ├── main_plugin.py        # Главный скрипт
   ├── core/                 # Базовые алгоритмы
   │   ├── geometry.py       # Работа с геометрией
   │   ├── rules_engine.py   # Парсинг нормативов
   │   └── collision.py      # Проверка коллизий
   ├── ai/                   # AI-модули
   │   ├── data_logger.py    # Сбор данных
   │   ├── classifier.py     # Классификатор сложности
   │   └── personalizer.py   # Персонализация
   ├── tests/                # Тесты
   │   ├── test_geometry.py
   │   └── test_ai.py
   └── assets/               # Ресурсы
       ├── rules.json        # Нормативы СП 256
       └── model_weights/    # Веса моделей
   ```

3. **Проверка**:
   - Запустите тестовый скрипт в Revit через pyRevit:  
     ```python
     from pyrevit import script
     output = script.get_output()
     output.print_md("## SocketAI: Environment Ready!")
     ```

---

#### 🔧 **Этап 1: Базовый алгоритм расстановки (3 дня)**
1. **Реализация geometry.py**:
   ```python
   # core/geometry.py
   from Autodesk.Revit.DB import XYZ, Line

   def generate_wall_points(wall, step=0.5):
       curve = wall.Location.Curve
       length = curve.Length
       points = []
       for i in range(int(length // step)):
           param = curve.GetEndParameter(0) + i * step
           points.append(curve.Evaluate(param, True))
       return points
   ```

2. **Реализация rules_engine.py**:
   ```python
   # core/rules_engine.py
   import json

   class RuleEngine:
       def __init__(self, rules_path="assets/rules.json"):
           with open(rules_path) as f:
               self.rules = json.load(f)
       
       def get_room_rules(self, room_type):
           return self.rules.get(room_type, self.rules["default"])
   ```

3. **Интеграция в main_plugin.py**:
   ```python
   # main_plugin.py
   from core.geometry import generate_wall_points
   from core.rules_engine import RuleEngine

   def place_devices(selected_rooms):
       engine = RuleEngine()
       for room in selected_rooms:
           rules = engine.get_room_rules(room.Type)
           for wall in room.Walls:
               points = generate_wall_points(wall, rules["step"])
               # ... логика расстановки
   ```

4. **Проверка**:
   - Тест 1.1: Создайте тестовое помещение в Revit
   - Тест 1.2: Запустите скрипт - должны появиться точки расстановки
   - Тест 1.3: Проверьте соответствие нормам в rules.json

---

#### 📊 **Этап 2: Система сбора данных (2 дня)**
1. **Реализация data_logger.py**:
   ```python
   # ai/data_logger.py
   import firebase_admin
   from firebase_admin import db

   class DataLogger:
       def __init__(self):
           cred = firebase_admin.credentials.Certificate('path/to/creds.json')
           firebase_admin.initialize_app(cred, {'databaseURL': 'https://socketai.firebaseio.com'})
       
       def log_correction(self, user_id, original, corrected, room_data):
           ref = db.reference(f'corrections/{user_id}')
           ref.push({
               'original': original.Coordinates,
               'corrected': corrected.Coordinates,
               'room_data': room_data
           })
   ```

2. **Интеграция в UI**:
   - Добавьте кнопку "Разрешить сбор данных" в настройках плагина
   - При ручной коррекции:
     ```python
     if config.allow_data_collection:
         logger.log_correction(user.id, original_point, corrected_point, room.get_data())
     ```

3. **Проверка**:
   - Тест 2.1: Сделайте ручную коррекцию
   - Тест 2.2: Проверьте появление данных в Firebase Realtime Database
   - Тест 2.3: Отключите сбор данных - логирование должно прекратиться

---

#### 🧠 **Этап 3: AI-классификатор сложных помещений (4 дня)**
1. **Обучение модели** (выполнить до реализации):
   - Используйте синтетические данные из Dynamo
   - Колаб-ноутбук: [gist.github.com/socketai-model](ссылка)
   - Экспорт в TFLite:
     ```python
     import tensorflow as tf
     converter = tf.lite.TFLiteConverter.from_saved_model('complex_room_model')
     tflite_model = converter.convert()
     with open('assets/model_weights/room_classifier.tflite', 'wb') as f:
         f.write(tflite_model)
     ```

2. **Реализация classifier.py**:
   ```python
   # ai/classifier.py
   import tensorflow.lite as tflite
   import numpy as np

   class RoomClassifier:
       def __init__(self, model_path):
           self.interpreter = tflite.Interpreter(model_path)
           self.interpreter.allocate_tensors()
           
       def is_complex(self, room_snapshot):
           input_data = self._preprocess(room_snapshot)
           input_index = self.interpreter.get_input_details()[0]['index']
           self.interpreter.set_tensor(input_index, input_data)
           self.interpreter.invoke()
           output = self.interpreter.get_tensor(self.output_details[0]['index'])
           return output[0][0] > 0.7
   ```

3. **Интеграция**:
   ```python
   # main_plugin.py
   from ai.classifier import RoomClassifier

   def place_devices(selected_rooms):
       classifier = RoomClassifier("assets/model_weights/room_classifier.tflite")
       for room in selected_rooms:
           snapshot = room.get_2d_snapshot()  # Метод для генерации 2D-схемы
           if classifier.is_complex(snapshot):
               self._handle_complex_room(room)
   ```

4. **Проверка**:
   - Тест 3.1: Создайте Г-образное помещение
   - Тест 3.2: Проверьте определение как "сложное"
   - Тест 3.3: Замерьте время классификации (должно быть < 1 сек)

---

#### 🎯 **Этап 4: Система персонализации (3 дня)**
1. **Реализация personalizer.py**:
   ```python
   # ai/personalizer.py
   from sklearn.ensemble import RandomForestRegressor
   import joblib

   class PersonalizationEngine:
       def __init__(self, user_id):
           self.model_path = f"user_models/{user_id}.joblib"
           try:
               self.model = joblib.load(self.model_path)
           except:
               self.model = RandomForestRegressor(n_estimators=10)
       
       def predict_adjustment(self, features):
           return self.model.predict([features])[0]
       
       def update_model(self, X, y):
           self.model.fit(X, y)
           joblib.dump(self.model, self.model_path)
   ```

2. **Интеграция с сбором данных**:
   ```python
   # При коррекции пользователя
   features = room.get_features()  # Параметры помещения
   adjustment = corrected_point - original_point
   personalizer.update_model(features, adjustment)
   ```

3. **Использование в расстановке**:
   ```python
   if config.enable_personalization:
       adjustment = personalizer.predict_adjustment(room_features)
       final_point = algorithmic_point + adjustment
   ```

4. **Проверка**:
   - Тест 4.1: Сделайте 5 коррекций в одинаковых помещениях
   - Тест 4.2: Проверьте применение паттерна в новых комнатах
   - Тест 4.3: Убедитесь, что файлы моделей создаются в user_models/

---

#### 🧪 **Этап 5: Комплексное тестирование (2 дня)**
1. **Тест-кейсы**:
   ```markdown
   | Сценарий               | Ожидаемый результат         | Метрика           |
   |------------------------|-----------------------------|-------------------|
   | Типовая кухня 12м²     | 4 розетки по СП 256         | 100% соответствие |
   | Г-образная гостиная    | AI-коррекция + сохранение   | Время < 15 сек    |
   | Отключение сбора данных| Нет записей в Firebase      | 0 новых записей   |
   | Сессия из 10 помещений | Стабильность памяти Revit   | RAM < 500 MB      |
   ```

2. **Автоматизированные тесты**:
   ```python
   # tests/test_ai.py
   def test_personalization():
       engine = PersonalizationEngine("test_user")
       X = [[12, 3.5, 1, 2]]  # площадь, высота, окна, двери
       y = [0.15]  # коррекция по X
       engine.update_model(X, y)
       assert abs(engine.predict_adjustment(X[0]) - 0.15) < 0.01
   ```

3. **Проверка производительности**:
   - Замеры времени для разных типов помещений
   - Профилирование памяти с помощью memory_profiler
   - Стресс-тест: 100+ помещений одновременно

---

#### 🚀 **Этап 6: Упаковка и распространение (1 день)**
1. **Создание .bundle для pyRevit**:
   ```yaml
   # socketai.bundle
   name: SocketAI
   version: 1.0.0
   description: AI-enhanced outlet placement
   author: Your Name
   commands:
     - name: Run SocketAI
       script: main_plugin.py
       icon: assets/icon.png
   ```

2. **Установка через pyRevit CLI**:
   ```bash
   pyrevit extend bundle install path/to/socketai.bundle
   ```

3. **Обновление моделей**:
   - Настройте CI/CD для переобучения моделей раз в неделю
   - Механизм автообновления через Firebase Storage

---

### Чеклист завершения этапов
1. [ ] Этап 0: Cursor IDE настроена, тестовый скрипт работает в Revit
2. [ ] Этап 1: Базовый алгоритм расставляет розетки по нормам
3. [ ] Этап 2: Данные коррекций появляются в Firebase
4. [ ] Этап 3: Классификатор верно определяет сложные помещения
5. [ ] Этап 4: Система запоминает предпочтения пользователя
6. [ ] Этап 5: Все тесты пройдены, отчет о производительности
7. [ ] Этап 6: Плагин установлен через pyRevit CLI

### Важные замечания
1. **Безопасность**:
   - Все данные пользователя шифруйте с помощью AES-256
   - Используйте .env для хранения секретных ключей
   - Регулярно обновляйте зависимости

2. **Оптимизация**:
   - Для тяжелых операций используйте `IDisposable` и `TransactionGroup`
   - Кэшируйте результаты геометрических расчетов
   - Ограничьте использование AI в реальном времени

3. **Совместимость**:
   - Протестируйте на Revit 2023-2025
   - Поддерживайте Python 3.8+ для совместимости с pyRevit

Разработка займет ~15 рабочих дней. Рекомендую начинать каждый этап с создания feature-ветки в Git и делать коммиты после каждой проверки!