# Практическая работа № 2 — вариант 21

## Этап 3: рекурсивный BFS

Программа читает Maven POM по HTTP или тестовый граф из файла,
затем строит **полный транзитивный граф зависимостей**.
Обход реализован алгоритмом **BFS с рекурсией по уровням**.
Посещённые вершины отслеживаются, поэтому циклы не вызывают
бесконечный обход; обратные рёбра сохраняются.

## Команды демонстрации

```powershell
python -m src.main --config config/test.ini
python -m src.main --config config/cycle.ini
python -m src.main --config config/chain.ini
python -m src.main --config config/complex.ini
python -m src.main --config config/remote.ini
```

Последняя команда требует доступа к Maven Central.

## Формат тестового репозитория

```text
A: B C
B: D
C: D
D:
```

Все названия состоят из **заглавных латинских букв**. Каждая
упомянутая вершина должна быть объявлена. Допустимы циклы.

## Настройки и тесты

INI-файл содержит `package`, `repository`, `test_mode`, `output`.
В обычном режиме `package` записывается как `group:artifact:version`.

```powershell
python -m unittest discover -s tests -v
```

## Локальная HTTP-демонстрация Maven без интернета

См. `examples/LOCAL_MAVEN.md`.
