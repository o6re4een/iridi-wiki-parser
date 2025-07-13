# Парсер для [old wiki](https://dev.iridi.com) + проверка в локальном проекте docusaurus

# Установка

## Убедиться что poetry создает окружение локально (Или задать вручную)

```bash
poetry config virtualenvs.in-project true
```

## Установить зависимости

```bash
poetry install
```

## Использование

В файле `to_parse.txt` содержаться ссылки для парсинга в формате:

```
link
link
```

# Запуск парсера

в терминале `python parser.py`

# Проверка в docusaurus

1. перейти в каталог `my-website`
2. устновить зависимости

```bash
npm install
```

3. Запустить проект в watch mode

```bash
npm run start
```

Возможна работа парсера при запущенном проекте docusaurus в watch mode. Страницы будут сразу создаваться после парсинга
