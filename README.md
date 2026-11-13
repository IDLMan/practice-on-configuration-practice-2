# Практическая работа № 2 — вариант 21

## Цель

Разработать анализатор и визуализатор зависимостей Maven на Python.
Это **этап 1**: конфигурация через INI и обработка ошибок.

## Требования

Python 3.10 или новее. Сторонние библиотеки не требуются.

## Запуск

Из корня проекта:

```powershell
python -m src.main --config config/test.ini
```

Для Windows можно использовать `run.bat`, для Linux — `sh run.sh`.

## Настройки

В `[settings]` используются **четыре обязательных параметра**:

- `package` — `A` в тестовом режиме или `group:artifact:version` для Maven;
- `repository` — локальный путь к графу или URL Maven-репозитория;
- `test_mode` — строго `true` или `false`;
- `output` — путь к целевому файлу `.svg`.

Относительные пути задаются относительно папки INI-файла.

## Тесты

```powershell
python -m unittest discover -s tests -v
```
