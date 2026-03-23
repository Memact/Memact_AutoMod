import random
import time

import nextcord

from bot import MemactAutoModBot
from config import load_settings


def _is_retryable_startup_error(error: Exception) -> bool:
    if not isinstance(error, nextcord.HTTPException):
        return False
    message = str(error)
    return error.status == 429 or "Error 1015" in message or "You are being rate limited" in message


def main() -> None:
    settings = load_settings()
    backoff_seconds = 60

    while True:
        bot = MemactAutoModBot(settings)
        try:
            bot.run(settings.token)
            return
        except Exception as error:
            if not _is_retryable_startup_error(error):
                raise

            print(
                "Discord blocked the current host IP during startup "
                f"({type(error).__name__}). Retrying in {backoff_seconds} seconds..."
            )
            time.sleep(backoff_seconds + random.randint(0, 10))
            backoff_seconds = min(backoff_seconds * 2, 900)


if __name__ == "__main__":
    main()
