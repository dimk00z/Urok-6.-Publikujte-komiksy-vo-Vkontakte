from os import getenv
from dotenv import load_dotenv


def get_data_from_env(data_name):
    load_dotenv()
    return getenv(data_name)
