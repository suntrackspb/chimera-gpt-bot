import os

from bot import start_bot

if __name__ == '__main__':

    print("Starting bot...")
    print(os.getenv("TELEGRAM_TOKEN"))

    start_bot()
