# Учебный проект Yatube

### Описание

Учебный проект социальной сети с постами - YATUBE. Многостраничный сайт с сессионной авторизацией и фронтендом на HTML.

### Функционал сайта

- Создание, редактирование и удаление записей.
- Добавление фотографий к постам.
- Подписка на других авторов и их публикации.
- Оставление комментариев.
- Возможность вступать в группы.
- Фильтрация по группам, подпискам.

#### Дополнительно

- Покрытие проекта 50% тестами
- Кэширование
- Использование индесов
- Пагинация

### Стек
Python, Django, Sqlite3, HTML, Unittest

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/kristina-pachi/pet_project_yatube.git
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```
