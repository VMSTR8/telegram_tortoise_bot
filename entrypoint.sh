#!/bin/sh
FILE=db.*
DIR=migrations

if [ -n "$FILE" ] && [ -n "$DIR" ]; then
  echo "Db files with wildcard $FILE and $DIR folder exist."
  echo "Starting bot"
  python3 main.py
else
  echo "Db files with wildcard $FILE and $DIR folder does not exist."
  echo "Initializing DB"
  aerich init -t database.config.TORTOISE_ORM
  aerich init-db
  echo "Starting bot"
  python3 main.py
fi