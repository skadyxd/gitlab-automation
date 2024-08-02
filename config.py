import os

from dotenv import load_dotenv

load_dotenv()

GITLAB_URL: str = os.getenv('GITLAB_URL')

PRIVATE_TOKEN: str = os.getenv('PRIVATE_TOKEN')  # user private token

PROJECT_ID: int = int(os.getenv('PROJECT_ID'))
PROJECT_ACCESS_TOKEN: str = os.getenv('PROJECT_ACCESS_TOKEN')

USER_IDS: list = list(map(int, os.getenv("USER_IDS").split(",")))

APPROVERS_IDS: list = list(map(int, os.getenv("APPROVERS_IDS").split(",")))

DISCORD_TOKEN: str = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID: int = int(os.getenv('DISCORD_CHANNEL_ID'))

HEADERS = {
    'Private-Token': PRIVATE_TOKEN
}

SLEEP_PAUSE = 60
