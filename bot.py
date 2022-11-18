# bot.py
import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


@tree.command(name="ping", description="Ping!")
async def first_command(interaction):
    await interaction.response.send_message("Pong!")


@client.event
async def on_ready():
    await tree.sync()
    print(f'{client.user} has connected to Discord!')


client.run(TOKEN)
