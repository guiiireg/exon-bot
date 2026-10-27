"""Entry point for the bot."""

from exon_bot.core.config import load_config
from exon_bot.discord_app.bot import ExonBot


def main() -> None:
    """Start the bot."""
    config = load_config()
    bot = ExonBot(config)
    bot.run(config.token)


if __name__ == "__main__":
    main()
