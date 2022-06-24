#!/bin/sh
/usr/local/bin/aerich init -t database.config.TORTOISE_ORM
/usr/local/bin/aerich init-db
python3 main.py
