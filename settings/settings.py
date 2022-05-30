import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

BOT_TOKEN = os.environ.get('BOT_TOKEN')

DATABASE_URL = os.environ.get('DATABASE_URL')

CREATORS_ID = os.environ.get('CREATORS_ID')


CENTER_POINT_LAT = os.environ.get('CENTER_POINT_LAT')
CENTER_POINT_LNG = os.environ.get('CENTER_POINT_LNG')


if __name__ == '__main__':
    pass
