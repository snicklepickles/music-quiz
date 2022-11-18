# bot.py
import os
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f'{client.user} has connected to Discord!')


@tree.command(name="ping", description="Ping!")
async def ping(interaction):
    await interaction.response.send_message("Pong!")


@tree.command(name="play", description="Starts a round of music quiz")
@app_commands.describe(url='Playlist URL')
async def play(interaction, url: str):
    channel = interaction.user.voice.channel
    if channel is None:
        await interaction.response.send_message("Please join a voice channel first")
    elif interaction.guild.voice_client is not None:
        await interaction.response.send_message("Quiz is already running")
    else:
        await channel.connect()
        await interaction.response.send_message("Quiz started")


client.run(TOKEN)
