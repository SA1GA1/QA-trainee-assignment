# Тестовое задание QA

## Установить Python и Allure Report 2

```bash
brew install python@3.13 allure
```

## Создать и активировать виртуальное окружение

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

## Установить зависимости проекта

```bash
python -m pip install -r requirements.txt
```

## Запустить тесты и записать результаты для Allure

```bash
python -m pytest -v --tb=short --alluredir=allure-results --clean-alluredir --allure-no-capture
```

## Открыть временный отчёт сразу после прогона тестов

```bash
allure serve allure-results
```

## Сохранить HTML-отчёт

```bash
allure generate allure-results --clean -o allure-report
```

## Открыть сохранённый отчёт в браузере

```bash
allure open allure-report
```

## Собрать пример отчёта одним HTML-файлом

```bash
allure_example_dir=$(mktemp -d)
allure generate allure-results --single-file -o "$allure_example_dir" &&
  cp "$allure_example_dir/index.html" allure-example.html
```

## Правила Ruff

Правила заданы в `ruff.toml`. Линтер проверяет базовые ошибки Python (`E4`, `E7`, `E9`, `F`) и порядок импортов (`I`). Форматтер использует двойные кавычки, отступ в четыре пробела и переносит строки с ориентиром на 100 символов.

### Проверить код и форматирование

```bash
python -m ruff check .
python -m ruff format --check .
```

### Исправить замечания и отформатировать код

```bash
python -m ruff check --fix .
python -m ruff format .
```
