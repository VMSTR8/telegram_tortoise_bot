import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

BOT_TOKEN = os.environ.get('BOT_TOKEN')

DATABASE_URL = os.environ.get('DATABASE_URL')

CREATORS_ID = os.environ.get('CREATORS_ID')

CREATORS_USERNAME = os.environ.get('CREATORS_USERNAME', 'командира или старшего')

if __name__ == '__main__':
    pass
