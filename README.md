# Практическая работа № 2 — вариант 21

## Этап 2: сбор зависимостей Maven

CLI-приложение на Python 3.10+ с конфигурацией в INI. Получает
**прямые** зависимости Maven из XML POM по Maven2 HTTP URL.
Не использует готовые менеджеры пакетов для извлечения зависимостей.
В тестовом режиме доступен локальный текстовый граф.

## Запуск

```powershell
python -m src.main --config config/test.ini
python -m src.main --config config/remote.ini
```

Вторая команда требует доступа к Maven Central. Для локальной
демонстрации достаточно первой команды.

## Настройки

`package`, `repository`, `test_mode`, `output` находятся в
`[settings]` INI-файла; только `--config` выбирает INI.
Реальный пакет задаётся как `group:artifact:version`.

## Что понимает XML-парсер

Парсер читает POM `<dependencies>`, свойства этого POM и
`<dependencyManagement>` текущего POM; пропускает зависимости со
scope `test`, `provided`, `system`, `import`, а также `optional`.
**Не реализована полная модель наследования Maven, импортируемых BOM,
профилей и разрешения конфликтов версий**. Для этих случаев выдаётся
ошибка вместо подстановки выдуманной версии.

## Тесты

```powershell
python -m unittest discover -s tests -v
```

## Структура

`src/` — логика; `tests/` — тесты; `config/` — INI;
`fixtures/graphs/` — тестовые графы; `run.bat` / `run.sh` — запуск.
