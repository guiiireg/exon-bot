# Exon Bot

A Discord bot.

## Setup

```bash
uv sync
```

Copy `.env.example` to `.env` and fill in your bot token:

```bash
cp .env.example .env
```

## Run

```bash
uv run exon-bot
```

## Project structure

```
src/exon_bot/
├── __init__.py
├── __main__.py          # Entry point
├── core/                # Configuration and shared core logic
└── discord_app/         # Discord client and cogs
```
