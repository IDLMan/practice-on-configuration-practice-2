# Локальная демонстрация Maven POM без интернета

В первом терминале VS Code из корня проекта:

```powershell
python -m http.server 8765 --directory fixtures/maven_repo
```

Не закрывая сервер, во втором терминале:

```powershell
python -m src.main --config config/local_maven.ini
```

`demo:app:1.0` зависит от `demo:core:1.0`, а тот —
от `demo:api:1.0`. Версия `core` наследуется через
`parent-1.0.pom` и `<dependencyManagement>`.

Это настоящие XML POM-файлы в структуре Maven2-репозитория,
обслуживаемые локальным HTTP-сервером. Maven/pip при получении
зависимостей не вызываются. Для остановки сервера нажмите `Ctrl+C`.
