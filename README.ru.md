# Telegram бот-ассистент для проведения игровых мероприятий
[![workflow](https://github.com/VMSTR8/telegram_tortoise_bot/actions/workflows/docker-image.yml/badge.svg)](https://github.com/VMSTR8/telegram_tortoise_bot/tree/main)

Бот создан для организации игровых мероприятий. Работает с геолокацией пользователей и предлагает различные игровые
сценарии в зависимости от местонахождения игрока.

На данный момент ведется активная разработка бота.

Стэк: [Python 3.8](https://www.python.org/), 
[Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot), 
[Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/)

## Скачивание и установка бота
Если все, что вам нужно, это запустить уже готового к работе бота, то сразу переходите к пункту 
[Установка и запуск бота через Docker](#установка-и-запуск-бота-через-Docker).

Если же вам не нужно запускать бота через докер контейнер и вы хотите поднять его через терминал, протестировать
функционал, покопаться "под капотом", то эта инструкция для вас.

Для начала клонируем себе этот репозиторий:

```bash
$ git clone https://github.com/VMSTR8/telegram_tortoise_bot.git
```

Переходим в папку с проектом, вводим команду cd и путь к папке, например:
```console
cd some_folder/telegram_tortoise_bot
```

Далее, перед тем, как установить все зависимости, не забываем создать и активировать виртуальное окружение.

Создание виртуального окружения:

```bash
$ python3 -m venv venv
```

Активация для Linux и macOS:

```bash
$ source venv/bin/activate
```

Активация для Windows:

```cmd
venv\Scripts\activate.bat
```

Ну и вот теперь уже устанавливаем зависимости:

```bash
$ pip install -r requirements.txt
```

Затем вам требуется создать и заполнить в папке **settings** файл с названием .env (да, прям так и назвать, 
с точкой в начале):

```text
BOT_TOKEN=<Токен вашего телеграм бота>
DATABASE_URL=sqlite://db.sqlite3
CREATORS_ID=<ID вашего аккаунта в телеграме>
CREATORS_USERNAME=<Ваш username в телеграме>
```

### Разъяснение значения переменных окружения
* Создать своего бота и получить токен вы можете у [@BotFather](https://t.me/BotFather).
* DATABASE_URL - ссылка на базу данных стандартная, проект использует sqlite в качестве БД. Но вдруг вам необходимо 
поменять название или иные настройки. Именно поэтому ссылка на БД вынесена в переменные окружения. Если в персональных
настройках нет смысла, скопируйте ссылку из примера.
* CREATORS_ID, это id вашего телеграм аккаунта. Выяснить его можно через ботов в телеграме. Например, через
[@userinfobot](https://t.me/userinfobot).
* CREATORS_USERNAME ваш ник в телеграме, например @fakeusernameofuser.

Как только все шаги из этого пункта сделаны, переходим к 
[инициализации базы и миграции](#инициализация-базы-и-миграции).

### Инициализация базы и миграции
Миграции запускаются довольно легко, всего лишь две команды.

Для начала передадим написанные модели инструменту миграции под названием Aerich:

```bash
$ aerich init -t database.config.TORTOISE_ORM
```

Все, что осталось сделать, это инициировать базу данных:

```bash
$ aerich init-db
```

Можете переходить к [запуску бота](#запуск-бота).

### Запуск бота
Все, что вам нужно, это ввести команду в терминале, находясь в корневой папке с проектом:

```bash
$ python main.py
```

Все! Вы великолепны :)

## Установка и запуск бота через Docker
Этот пункт предназначен для тех, кто хочет **относительно** просто скачать и запустить бота.
Давайте по порядку. Первое, что вам необходимо сделать, это скачать и установить приложение [Docker](https://www.docker.com/get-started/)
для своего компьютера.

Учтите, что если ставить Docker для Windows, приложение попросит установить пакет WSL. Без него Docker не будет 
работать.

После установки приложения вам останется выполнить одну команду в терминале на macOS/Linux или запустим от
администратора CMD.exe на Windows.

### Если разворачивали Docker на macOS/Linux

```bash
$ docker run --name Telegram_bot -d \
-e 'BOT_TOKEN=токен вашего телеграм бота' \
-e 'DATABASE_URL=sqlite://db.sqlite3' \
-e 'CREATORS_ID=ID вашего аккаунта в телеграме' \
-e 'CREATORS_USERNAME=Ваш username в телеграме' vmstr8/rdwn-telegram-bot:1.2
```

### Если разворачивали Docker на Windows
```cmd
docker run --name Telegram_bot -d ^
-e BOT_TOKEN="токен вашего телеграм бота" ^
-e DATABASE_URL="sqlite://db.sqlite3" ^
-e CREATORS_ID="ID вашего аккаунта в телеграме" ^
-e CREATORS_USERNAME="Ваш username в телеграме" vmstr8/rdwn-telegram-bot:1.2
```

И все. Ваш бот запущен. Вы великолепны :)

P.S. Что означает каждая переменная (BOT_TOKEN, DATABASE_URL и т.д.) в инструкции запуска было уже описано выше.
Просто перейдите к пункту [разъяснение значения переменных окружения](#разъяснение-значения-переменных-окружения).

## Roadmap
- ✅: Регистрация пользовательского позывного
- ✅: Присоединение к игровой стороне
- ✅: Админ меню
- ✅: (Для админа) Добавление, редактирование и удаление стороны
- ✅: (Для админа) Добавление, редактирование и удаление точки
- ❌: (Для админа) Вывод всех пользователей
- ❌: (Для админа) Редактирование информации пользователя
- ❌: (Для админа) Пагинация меню, когда админ просматривает стороны, точки или пользователей
- ✅: (Для админа) Отправка сообщений всем пользователям, которые находятся в игре
- ❌: (Для админа) Отправка разного типа сообщений: фото, голосовые, аудио, видео
- ✅: Активация игровой точки
- ✅: Возможность посмотреть, сколько осталось до вывода точки из игры
- ✅: Проверка состояния точки (Активирована (и кем) | Не активирована)
- ❌: Возможность вывода пользователем информации о себе

По мере работы над ботом в roadmap будет добавляться новый функционал, как уже реализованный, так и запланированный.