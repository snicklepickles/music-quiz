# bot.py
import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from thefuzz import fuzz
from src.music_quiz import MusicQuiz

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    voice_client = message.guild.voice_client
    if voice_client is not None and voice_client.is_playing():
        token_set_ratio = fuzz.token_set_ratio(message.content, "OMORI OST - 178 My Time")
        print(message.content, token_set_ratio)
        if token_set_ratio > 80:
            pass
            # voice_client.stop()
            # await message.channel.send('Stopped playing')


@tree.command(name="ping", description="Ping!")
async def ping(interaction):
    await interaction.response.send_message("Pong!")


# !TODO - Add a random queue system
# !TODO - Add a (vote to) skip command
# !TODO - Default to a popular songs playlist if no URL is specified
# !TODO - Add a player leaderboard

@tree.command(name="play", description="Starts a round of music quiz")
@app_commands.describe(url='Playlist URL')
async def play(interaction, url: str = None):
    channel = interaction.user.voice.channel
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        await interaction.response.send_message("Quiz is already running")
    elif channel is None:
        await interaction.response.send_message("Please join a voice channel first")
    else:
        music_quiz = MusicQuiz(interaction, url)
        embed = discord.Embed(title="Music Quiz", description="Loading songs... get ready!")
        await interaction.response.send_message(embed=embed)
        await music_quiz.start()


@tree.command(name="pause", description="Pauses a round of music quiz")
async def pause(interaction):
    voice_client = interaction.guild.voice_client
    if voice_client is None:
        await interaction.response.send_message("Quiz is not running")
    else:
        voice_client.pause()
        await interaction.response.send_message("Quiz paused")


@tree.command(name="resume", description="Resumes a round of music quiz")
async def resume(interaction):
    voice_client = interaction.guild.voice_client
    if voice_client is None:
        await interaction.response.send_message("Quiz is not running")
    else:
        voice_client.resume()
        await interaction.response.send_message("Quiz resumed")


@tree.command(name="stop", description="Stops a round of music quiz")
async def stop(interaction):
    voice_client = interaction.guild.voice_client
    if voice_client is None:
        await interaction.response.send_message("Quiz is not running")
    else:
        voice_client.stop()
        await voice_client.disconnect()
        await interaction.response.send_message("Quiz stopped")


client.run(TOKEN)
