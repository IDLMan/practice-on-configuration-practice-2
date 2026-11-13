# Практическая работа № 2 — вариант 21

## Этап 4: порядок загрузки зависимостей

На Python 3.10+ построен рекурсивным BFS граф Maven/тестовых пакетов,
затем для ациклических графов вычисляется детерминированный порядок
**сначала зависимости, затем использующие их пакеты**.
Алгоритм основан на топологической сортировке Кана; при цикле
программа выводит явную ошибку, поскольку корректного порядка нет.

## Демонстрация

```powershell
python -m src.main --config config/test.ini
python -m src.main --config config/chain.ini
python -m src.main --config config/complex.ini
python -m src.main --config config/cycle.ini
python -m src.main --config config/remote.ini
```

Для последней команды необходим интернет; Maven-репозиторий и
`group:artifact:version` заданы в `config/remote.ini`.

## Сравнение с Maven

`examples/MAVEN_COMPARISON.md` содержит команды штатного
`mvn dependency:tree` и объяснение различий с нашим порядком.
Для запуска Maven нужны отдельно установленные JDK и Maven;
они **не используются** для извлечения зависимостей программой.

## Конфигурация и тестирование

INI `[settings]`: `package`, `repository`, `test_mode`, `output`.

```powershell
python -m unittest discover -s tests -v
```

Сторонние Python-библиотеки не требуются.

## Локальная HTTP-демонстрация Maven без интернета

См. `examples/LOCAL_MAVEN.md`.
