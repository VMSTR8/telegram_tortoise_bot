# Telegram bot for organizing events using geolocation
[![workflow](https://github.com/VMSTR8/telegram_tortoise_bot/actions/workflows/docker-image.yml/badge.svg)](https://github.com/VMSTR8/telegram_tortoise_bot/tree/main)

Русская версия доступна тут: [README.ru.md](README.ru.md)

The bot was created to organize gaming events (first of all - airsoft). It works with geolocation of users and offers 
various game scenarios depending on the location of the player.

At the moment, the bot is being actively developed.

Stack: [Python 3.8](https://www.python.org/), 
[Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot), 
[Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/)

## Downloading and installing the bot
If all you need is to launch a ready-to-work bot, then go straight to the section
[Installing and launching a bot via Docker](#installing-and-launching-a-bot-via-docker).

If you don't need to run the bot through the docker container, and you want to run it through the terminal, test
the functionality, add your own functionality, then this instruction is for you.

At the beginning, we clone this repository to our computer:
```bash
$ git clone https://github.com/VMSTR8/telegram_tortoise_bot.git
```

Go to the folder with the project, enter the cd command and the path to the folder, for example:
```console
cd some_folder/telegram_tortoise_bot
```

Next, before installing all the dependencies, do not forget to create and activate a virtual environment.

Creating a virtual environment:
```bash
$ python3 -m venv venv
```

Activation for Linux and macOS:
```bash
$ source venv/bin/activate
```

Activation for Windows:
```cmd
venv\Scripts\activate.bat
```

Well, for now we're ready to install dependencies:
```bash
$ pip install -r requirements.txt
```

Then you need to create and fill in a file named .env in the **settings** folder (yes, just call it that,
with a dot at the beginning):
```text
BOT_TOKEN=<Your Telegram bot token>
DATABASE_URL=sqlite://db.sqlite3
CREATORS_ID=<Your Telegram account ID>
CREATORS_USERNAME=<Your username in the telegram>
```

### Explanation of environment variables
* You can create your bot and get a token from [@BotFather](https://t.me/BotFather ).
* DATABASE_URL is a standard database reference. The project uses sqlite as a database. But suddenly you need
to change the name or other settings. That is why the reference to the database is placed in the environment variables. 
If there is no point in personal settings, copy the link from the example.
* CREATORS_ID, this is the ID of your telegram account. You can find it out through the bots in the telegram. 
For example, through [@userinfobot](https://t.me/userinfobot).
* CREATORS_USERNAME your nickname in the telegram, for example @fakeusernameofuser.

As soon as all the steps from this point are done, we move on to initializing the database and migrating
[initializing the database and migrating](#initializing-the-database-and-migrating).

### Initializing the database and migrating
Migrations are started quite easily, with just two commands.

At the beginning, we will transfer the written models to a migration tool called Aerich:
```bash
$ aerich init -t database.config.TORTOISE_ORM
```

All that's left to do is initiate the database:
```bash
$ aerich init-db
```

You can proceed to [launching the bot](#launching-the-bot).

### Launching the bot
All you need to do is enter the command in the terminal, being in the root folder with the project:
```bash
$ python main.py
```

That's it! You are great :)

## Installing and launching a bot via Docker
This section is for those people who just want to download and run a bot.
Let's take it in order. The first thing you need to do is download and install the [Docker application](https://www.docker.com/get-started/)
for your computer.

Note that if you install Docker for Windows, the application will ask you to install the WSL package. Docker won't
work without it.

After installing the application, you will need to run the command in the terminal on macOS/Linux 
or in CMD.exe with administrator rights on Windows.

### If you deployed Docker on macOS/Linux

```bash
$ docker run --name Telegram_bot -d \
-e 'BOT_TOKEN=Your Telegram bot token' \
-e 'DATABASE_URL=sqlite://db.sqlite3' \
-e 'CREATORS_ID=Your Telegram account ID' \
-e 'CREATORS_USERNAME=Your username in the telegram' vmstr8/rdwn-telegram-bot:1.2
```

### If you deployed Docker on Windows
```cmd
docker run --name Telegram_bot -d ^
-e BOT_TOKEN="Your Telegram bot token" ^
-e DATABASE_URL="sqlite://db.sqlite3" ^
-e CREATORS_ID="Your Telegram account ID" ^
-e CREATORS_USERNAME="Your username in the telegram" vmstr8/rdwn-telegram-bot:1.2
```

That's all. Your bot is running. You are great :)

P.S. What each variable means (BOT_TOKEN, DATABASE_URL, etc.) has already been described above.
Just go to [explanation of environment variables](#explanation-of-environment-variables).

## Roadmap
- ✅: Registration of a user callsign
- ✅: Joining the gaming side
- ✅: Admin Menu
- ✅: (For the admin) Adding, editing, and deleting a side
- ✅: (For the admin) Adding, editing, and deleting a point
- ❌: (For the admin) View all users
- ❌: (For the admin) Editing user information
- ❌: (For admin) Pagination of the menu when the admin views the sides, points or users
- ✅: Game Point Activation
- ❌: Display information about the remaining time until the point is removed from the game
- ❌: Checking the status of the point (Activated (and by whom) | Not activated)
- ❌: The user's output of information about himself

As we work on the bot, new functionality will be added to the roadmap, both already implemented and planned.