### Описание

Pet-проект социальная сеть YATUBE

Позволяет создавать, добавлять в группы и комментировать посты, подписываться на других авторов

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/kristina-pachi/hw05_final.git
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Script/activate
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
