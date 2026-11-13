# Практическая работа № 2 — вариант 21

**Дисциплина:** Конфигурационное управление.  
**Тема:** анализ и визуализация графов зависимостей Maven.  
**Реализация:** Python 3.10+, только стандартная библиотека.

## Что делает программа

- Читает четыре настройки из INI: имя пакета, репозиторий,
  тестовый режим, целевой файл SVG.
- Получает зависимости реального Maven-пакета из HTTP POM,
  **без готовых менеджеров и библиотек получения зависимостей**.
- Загружает тестовые графы с узлами A-Z из текстовых файлов.
- Строит транзитивный граф рекурсивным BFS; не зацикливается.
- Вычисляет порядок «сначала зависимости» для DAG.
- Создаёт исходную диаграмму PlantUML `.puml` и изображение `.svg`.

## Как запустить (Windows / VS Code)

1. Распаковать проект и открыть его корневую папку в VS Code.
2. Открыть `Terminal -> New Terminal`.
3. Выполнить:

```powershell
python -m src.main --config config/test.ini
```

При стандартной конфигурации результат окажется в `output/diamond.svg`.
Откройте его браузером или двойным щелчком в проводнике Windows.
Для запуска через скрипт доступен `run.bat` (Windows) или `sh run.sh`.

## Три разных пакета

```powershell
python -m src.main --config config/test.ini
python -m src.main --config config/b.ini
python -m src.main --config config/c.ini
```

Будут созданы изображения **A**, **B**, **C**. Дополнительные сценарии:

```powershell
python -m src.main --config config/cycle.ini
python -m src.main --config config/chain.ini
python -m src.main --config config/complex.ini
```

Тестовый формат: `A: B C` означает зависимости A от B и C.
В файле обязательно объявлять все упомянутые пакеты.

## Анализ реального Maven-пакета

```powershell
python -m src.main --config config/remote.ini
```

Нужен интернет. Пример: `org.slf4j:slf4j-simple:2.0.13`.
Репозиторий Maven Central указан в INI.

Для воспроизводимого сравнения со штатным Maven см.
[инструкцию](examples/MAVEN_COMPARISON.md):

```powershell
mvn -f examples/maven_reference/pom.xml dependency:tree
```

`mvn` нужен только для **сравнения результатов**, а не для сбора
зависимостей нашей программой. Сравнение проводится отдельно при
установленных JDK и Maven.

## Конфигурация — только INI

Пример `config/test.ini`:

```ini
[settings]
package = A
repository = ../fixtures/graphs/diamond.txt
test_mode = true
output = ../output/diamond.svg
```

Файл выбирается `--config`; остальные параметры живут **только в INI**.
В обычном режиме имя имеет вид `group:artifact:version`, а источник
представляет собой Maven2 HTTP(S)-репозиторий. Для тестового режима
используются имена в верхнем регистре (`A`, `B`, ...).
Относительные пути разрешаются **относительно файла INI**.

## Тестирование

```powershell
python -m unittest discover -s tests -v
```

## Архитектура

- `src/config.py` — строгая INI-конфигурация и проверки;
- `src/maven.py` — получение и разбор POM;
- `src/test_repo.py` — текстовый тестовый репозиторий;
- `src/sources.py` — интерфейс источника зависимостей;
- `src/graph.py` — рекурсивный обход в ширину;
- `src/order.py` — топологический порядок;
- `src/visualize.py` — PlantUML и SVG;
- `src/main.py` — CLI.
- `tests/` — автономные автоматические тесты;
- `fixtures/` и `config/` — примеры входных данных.