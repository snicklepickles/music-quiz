# bot.py
import os
import discord
import youtube_dl
import asyncio
from discord import app_commands
from dotenv import load_dotenv
from thefuzz import fuzz, process

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


voice_clients = {}
ytdl_options = {'format': 'bestaudio/best'}
ytdl = youtube_dl.YoutubeDL(ytdl_options)
ffmpeg_options = {'options': '-vn'}


# !TODO - Add a random queue system
# !TODO - Add a (vote to) skip command
# !TODO - Default to a popular songs playlist if no URL is specified
# !TODO - Add a player leaderboard

@tree.command(name="play", description="Starts a round of music quiz")
@app_commands.describe(url='Playlist URL')
async def play(interaction, url: str = None):
    channel = interaction.user.voice.channel
    voice_client = voice_clients.get(channel.guild.id)
    if voice_client is not None and voice_client.is_playing():
        await interaction.response.send_message("Quiz is already running")
    elif channel is None:
        await interaction.response.send_message("Please join a voice channel first")
    else:
        voice_client = await channel.connect()
        voice_clients[voice_client.guild.id] = voice_client

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        # print(data['title'])
        song = data['url']
        player = discord.FFmpegPCMAudio(song, **ffmpeg_options, executable="C:\\ffmpeg\\ffmpeg.exe")

        voice_client.play(player)

        # url = url.replace("https://open.spotify.com/playlist/", "https://open.spotify.com/embed/playlist/")
        # await interaction.response.send_message("Quiz started")


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
    try:
        voice_client = voice_clients[interaction.guild.id]
        voice_client.stop()
        await voice_client.disconnect()
        await interaction.response.send_message("Quiz stopped")
    except KeyError:
        await interaction.response.send_message("Quiz is not running")


client.run(TOKEN)
