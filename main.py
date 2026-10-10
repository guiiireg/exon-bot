import os
import random
import sys
import time

import discord
from discord import ActionRow, Poll, app_commands, ui
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("DISCORD_TOKEN")
guild_str = os.getenv("GUILD_ID")

if guild_str is None:
    print(
        "[WARNING] GUILD_ID is missing, check if .env or variable is named correctly."
    )
    sys.exit(1)

guild = int(guild_str)

intents = discord.Intents.default()

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(guild=discord.Object(id=guild))
async def ping(inter: discord.Interaction) -> None:
    """
    Get the bot's latency

    Parameters
    ----------
    inter : discord.Interaction
        The interaction object
    """
    start_time = time.perf_counter()
    await inter.response.defer()
    final_time = time.perf_counter()
    response_time = final_time - start_time
    response_time *= 1000
    await inter.edit_original_response(
        content=f"The latency is: {round(client.latency * 1000)}ms. \n"
        f"The Response Time is: {round(response_time)}ms."
    )


@tree.command(guild=discord.Object(id=guild))
async def choose(inter: discord.Interaction, options: str) -> None:
    """
    Choose a random option between the options

    Parameters
    ----------
    inter : discord.Interaction
        The interaction object
    options: str
        The options to choose
    """
    choices = options.split(",")
    for index in range(len(choices)):
        choices[index] = choices[index].strip()
        if not choices[index]:
            await inter.response.send_message(
                "One option is empty. Separate the options with commas without leaving any empty field."
            )
            return
    if len(choices) < 2:
        await inter.response.send_message("You need at least two options.")
        return
    chosen = random.choice(choices)
    await inter.response.send_message(f"{chosen}")


class PollButton(ui.Button):
    def __init__(
        self, choice: str, votes: dict[int, str], poll_view: "PollView"
    ) -> None:
        super().__init__(label=choice)

        self.choice = choice
        self.votes = votes
        self.poll_view = poll_view

    async def callback(self, inter: discord.Interaction) -> None:
        self.votes[inter.user.id] = self.choice
        self.poll_view.results_display.content = self.poll_view.format_results()
        await inter.response.edit_message(view=self.poll_view)


class PollView(ui.LayoutView):
    def __init__(
        self,
        question: str,
        choices: list[str],
        votes: dict[int, str],
    ) -> None:
        super().__init__()
        self.votes = votes
        self.choices = choices
        self.question_display = ui.TextDisplay(question)
        self.results_display = ui.TextDisplay(self.format_results())

        action_row = ui.ActionRow()
        for index in range(len(choices)):
            button = PollButton(choice=choices[index], votes=self.votes, poll_view=self)
            action_row.add_item(button)
        container = ui.Container(
            self.question_display, action_row, self.results_display
        )
        self.add_item(container)

    def count_votes(self):
        res = {}
        for index in self.choices:
            res[index] = 0
        for vote in self.votes.values():
            res[vote] += 1
        return res

    def format_results(self):
        total_votes = self.count_votes()
        text_result = ""

        for choice in self.choices:
            text_result += f"{choice} : {total_votes[choice]}\n"
        return text_result


@tree.command(guild=discord.Object(id=guild))
async def poll(inter: discord.Interaction, question: str, options: str) -> None:
    """
    Create a poll

    Parameters
    ----------
    inter : discord.Interaction
    question: str
    options: str
    """
    choices = options.split(",")
    fixed_question = question.strip()
    if not fixed_question:
        await inter.response.send_message("The question is empty.")
        return
    for index in range(len(choices)):
        choices[index] = choices[index].strip()
        if not choices[index]:
            await inter.response.send_message(
                "One option is empty. Separate the options with commas without leaving any empty field."
            )
            return
    if len(choices) < 2 or len(choices) > 5:
        await inter.response.send_message("You need between 2 and 5 options.")
        return
    await inter.response.send_message(view=PollView(fixed_question, choices, votes={}))


if token is None:
    print(
        "[WARNING] DISCORD_TOKEN is missing, check if .env or variable is named correctly."
    )
    sys.exit(1)


@client.event
async def on_ready():
    print("[INFORMATIONS] Bot is ready to be used.")
    await tree.sync(guild=discord.Object(id=guild))


client.run(token=token)
