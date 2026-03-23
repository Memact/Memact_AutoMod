from bot import MemactAutoModBot
from config import load_settings


def main() -> None:
    settings = load_settings()
    bot = MemactAutoModBot(settings)
    bot.run(settings.token)


if __name__ == "__main__":
    main()
