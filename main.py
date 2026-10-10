from dotenv import load_dotenv
import sys
import os

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

if token is None:
    print(
        "[WARNING] DISCORD_TOKEN is missing, check if .env or variable is named correctly."
    )
    sys.exit()

if token is not None:
    print("[INFORMATIONS] DISCORD_TOKEN loaded successfully.")
